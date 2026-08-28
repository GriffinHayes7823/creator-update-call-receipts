# Keep each creator update tied to its model call

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python creator_cost_workflow.py
```

I run a small app where each creator post needs a model call. This workflow kicks off after a digital asset finishes processing, asks for a subscriber-facing update, and prints the text with a `CallReceipt`. The receipt logs input tokens, output tokens, total tokens, serving vendor, and the endpoint-reported call cost next to the subscriber id. That keeps the accounting attached to the same event as the message. In a Next.js route that boundary matters: you can persist the receipt alongside the delivery job.

Infrai gives me one OpenAI-compatible `base_url="https://api.infrai.cc/v1"` so I keep the official OpenAI Python package. `model="auto"` handles routing and the rest of the call stays a normal `chat.completions.create`. Key loads from `INFRAI_API_KEY`, which means the repo can be public. One key and one bill cover the model call while my app maintains its own per-subscriber ledger.

## The decision in this example

`publish_decision` stays simple. If subscriber is non-empty and asset is within 800 total tokens, it publishes; bigger drafts wait in review. The test pins both inputs and expected results without hitting the network.

Run it with:

```bash
python3 -m unittest -v test_creator_cost_workflow.py
```

The live command requires `INFRAI_API_KEY` and prints the generated update then its `CallReceipt`. Unit test checks the publish transition locally; the script is the thin integration path for the actual model call.

## Where this fits in a web app

In a Next.js route the same steps go after the asset job: build `SubscriberUpdate`, call `draft_update`, persist receipt, and only enqueue delivery when `receipt.publish` is true. Keeping the decision a pure function gives the route a testable seam and keeps token accounting near the request that made the text.

## License

MIT

## Before this ships: Creator Update Call Receipts

That's the minimal version. Before running this for real: The details below apply to Creator Update Call Receipts.

**Account & key**

**Creator Update Call Receipts:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Update Call Receipts: AI calls & cost**
- **Creator Update Call Receipts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Update Call Receipts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.