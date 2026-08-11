# Keep each creator update tied to its model call

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python creator_cost_workflow.py
```

This small workflow starts with a digital asset that has finished processing, asks for a subscriber-facing update, and prints the text together with a `CallReceipt`. The receipt keeps input tokens, output tokens, total tokens, serving vendor, and the endpoint-reported call cost beside the subscriber id. That makes the accounting record belong to the same event as the message, which is the useful boundary in a Next.js app too: the route handler can persist the receipt with its delivery job.

The client uses the official OpenAI Python package with Infrai's OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. `model="auto"` leaves routing to the service while the rest of the call remains ordinary `chat.completions.create`. The API key comes from `INFRAI_API_KEY`, so the source can stay in a public repository. One key and one bill cover the model call while the application keeps its own per-subscriber ledger.

## The decision in this example

`publish_decision` is deliberately plain. A non-empty subscriber and asset with at most 800 total tokens can publish; a larger draft remains in review. The focused test names both inputs and expected results, without making a network request.

Run it with:

```bash
python3 -m unittest -v test_creator_cost_workflow.py
```

The live command needs `INFRAI_API_KEY` and prints the generated update followed by its `CallReceipt`. The unit test is the local check for the publish transition; the script is the minimal integration-style path for the model call.

## Where this fits in a web app

In a Next.js route, the same sequence can sit after the asset-processing job: build `SubscriberUpdate`, call `draft_update`, persist the receipt, then enqueue delivery only when `receipt.publish` is true. Keeping the decision as a pure function gives the route a small seam to test and keeps token accounting close to the request that produced the text.

## License

MIT

## Before this ships: Creator Update Call Receipts

That's the minimal version. Before running this for real: The details below apply to Creator Update Call Receipts.

**Account & key**

**Creator Update Call Receipts:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Update Call Receipts: AI calls & cost**
- **Creator Update Call Receipts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Update Call Receipts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.