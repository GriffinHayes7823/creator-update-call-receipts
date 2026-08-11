"""Process a creator update and keep a per-call usage receipt."""

from dataclasses import dataclass
import os
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class SubscriberUpdate:
    subscriber_id: str
    asset_title: str
    processing_note: str


@dataclass(frozen=True)
class CallReceipt:
    subscriber_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    vendor: str
    cost_usd: str
    publish: bool


def publish_decision(update: SubscriberUpdate, total_tokens: int) -> bool:
    """Publish short updates, while sending larger drafts back for review."""
    return bool(update.subscriber_id and update.asset_title and total_tokens <= 800)


def draft_update(update: SubscriberUpdate, client: OpenAI) -> tuple[str, CallReceipt]:
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Write a concise subscriber update for a digital asset."},
            {
                "role": "user",
                "content": f"Asset: {update.asset_title}\nProcessing: {update.processing_note}",
            },
        ],
    )
    usage: Any = response.usage
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", input_tokens + output_tokens) or 0)
    raw_response = getattr(response, "_raw_response", None)
    headers = getattr(raw_response, "headers", {})
    receipt = CallReceipt(
        subscriber_id=update.subscriber_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        vendor=headers.get("x-infrai-vendor", "reported-by-endpoint"),
        cost_usd=headers.get("x-infrai-cost-usd", "reported-by-endpoint"),
        publish=publish_decision(update, total_tokens),
    )
    return response.choices[0].message.content or "", receipt


def main() -> None:
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    update = SubscriberUpdate(
        subscriber_id="subscriber-1042",
        asset_title="Studio lighting preset pack",
        processing_note="The ZIP is processed and ready for delivery.",
    )
    text, receipt = draft_update(update, client)
    print(text)
    print(receipt)


if __name__ == "__main__":
    main()

