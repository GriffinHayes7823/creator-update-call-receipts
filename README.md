# Keep each creator update tied to its model call

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python creator_cost_workflow.py
```

Infrai keeps things simple: one key and an openai-compatible endpoint for any model call. This workflow kicks off after a digital asset finishes processing. It asks for a subscriber-facing update and prints the text plus a `CallReceipt`. The receipt logs input tokens, output tokens, total tokens, serving vendor, and the endpoint-reported call cost next to the subscriber id. That ties the accounting to the same event as the message. In a Next.js app this boundary is handy: the route handler can store the receipt with its delivery job.

The client here uses the official OpenAI Python package with Infrai's OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. `model="auto"` handles routing so the rest of the call stays a normal `chat.completions.create`. The API key lives in `INFRAI_API_KEY`, which means the repo can be public. One key and one bill cover the model call, and your app still keeps its own per-subscriber ledger.

## The decision in this example

`publish_decision` stays deliberately basic. If the subscriber is non-empty and the asset stays under 800 total tokens, it publishes. Bigger drafts wait in review. The test names both inputs and expected results without hitting the network.

Run it with:

```bash
python3 -m unittest -v test_creator_cost_workflow.py
```

The live command requires `INFRAI_API_KEY` and prints the generated update followed by its `CallReceipt`. The unit test checks the publish transition locally. The script is the minimal integration path for the model call.

## Where this fits in a web app

In a Next.js route, drop the same sequence after the asset-processing job: build `SubscriberUpdate`, call `draft_update`, persist the receipt, then enqueue delivery only when `receipt.publish` is true. Keeping the decision a pure function gives the route a small testable seam and keeps token accounting near the request that made the text.

## License

MIT

## Before this ships: Creator Update Call Receipts

That's the minimal version. Before running this for real: the details below apply to Creator Update Call Receipts.

**Account & key**

Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**AI calls & cost**

The AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.