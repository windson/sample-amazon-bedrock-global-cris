#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 4.7 Pause After Compaction (InvokeModel)

Demonstrates pause_after_compaction for advanced workflows:
- API returns with stop_reason: "compaction" after generating the summary
- You can inspect or modify the compacted context before continuing
- After continuing, the model responds with the compacted context

Compaction is in beta and requires the anthropic_beta header.
Compaction only works with InvokeModel (not Converse API during beta).
Minimum trigger threshold is 50,000 tokens (default: 150,000).

Note: Claude Opus 4.7 no longer supports temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

References:
- Compaction: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
- Claude Opus 4.7 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html

Author: Navule Pavan Kumar Rao
Date: April 20, 2026

Expected output flow:
======================
  Turn 1: Large API spec (~19K tokens) → Normal response
          Compaction paused: False (context still under 50K threshold)

  Turn 2: Second large API spec → Context exceeds 50K threshold
          → COMPACTION TRIGGERS → API PAUSES (stop_reason: "compaction")
          → We inspect the compaction summary
          → We inject a reminder about Turn 1 decisions
          → We CONTINUE → Get the actual response

  Turn 3: Follow-up question → Normal response
          → Proves conversation still works with compacted context
"""

import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from common.colors import status_color, turn_header, GREEN, ORANGE, RESET
from common.context_generator import generate_api_spec

# Initialize Bedrock client for India region (Mumbai)
# Extended read timeout for large-context requests
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    config=Config(read_timeout=300)
)

# Global CRIS model ID for Claude Opus 4.7
MODEL_ID = "global.anthropic.claude-opus-4-7"

# Compaction trigger threshold in input tokens.
# The minimum allowed value is 50,000 tokens (default is 150,000).
COMPACTION_TRIGGER_THRESHOLD = 50000

# Conversation history shared across turns
messages = []


def send_message(user_message: str, pause_on_compaction: bool = True):
    """
    Send a message with compaction enabled.

    Args:
        user_message: The user's message text.
        pause_on_compaction: If True, API pauses after compaction for inspection.

    Returns:
        Tuple of (model_response_dict, was_paused: bool)
    """
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 4.7
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Compaction beta header — required during beta period
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
        "anthropic_beta": ["compact-2026-01-12"],
        "max_tokens": 4096,
        "messages": messages,
        # Server-side compaction with pause
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
        "context_management": {
            "edits": [{
                "type": "compact_20260112",
                "trigger": {
                    "type": "input_tokens",
                    "value": COMPACTION_TRIGGER_THRESHOLD
                },
                # When True, API returns stop_reason: "compaction" after summary
                # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html#pausing-after-compaction
                "pause_after_compaction": pause_on_compaction
            }]
        }
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    model_response = json.loads(response["body"].read())
    stop_reason = model_response.get("stop_reason", "")

    if stop_reason == "compaction":
        return model_response, True

    # Normal response — append to conversation history
    messages.append({
        "role": "assistant",
        "content": model_response["content"]
    })

    return model_response, False


def extract_text(response: dict) -> str:
    """Extract text content from a model response."""
    for block in response.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    return ""


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.7 Pause After Compaction")
print("🚀 Model: Claude Opus 4.7 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📦 Compaction trigger threshold: {COMPACTION_TRIGGER_THRESHOLD:,} input tokens")
print("⏸️  pause_after_compaction: True")
print("⚠️  Compaction is in beta — requires anthropic_beta header")

try:
    # =========================================================================
    # Turn 1: First large API spec. Context is under 50K — no compaction yet.
    # =========================================================================
    spec1 = generate_api_spec("User Management Service", num_endpoints=30)
    prompt1 = f"Review this API specification and identify the top 5 security concerns:\n\n{spec1}"

    print("\n" + "=" * 60)
    print(f"{turn_header(1, f'User Management Service ({len(prompt1):,} chars)')}")
    print("=" * 60)
    response, was_paused = send_message(prompt1)
    text = extract_text(response)
    usage = response.get("usage", {})
    print(f"   Response: {text[:200]}...")
    print(f"   ⏸️  Compaction paused: {status_color(was_paused)}")
    print(f"   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")

    # =========================================================================
    # Turn 2: Second large API spec pushes context past 50K threshold.
    # Compaction triggers and the API PAUSES for inspection.
    # =========================================================================
    spec2 = generate_api_spec("Payment Processing Service", num_endpoints=30)
    prompt2 = f"Now review this payment API spec and suggest performance optimizations:\n\n{spec2}"

    print("\n" + "=" * 60)
    print(f"{turn_header(2, f'Payment Processing Service ({len(prompt2):,} chars)')}")
    print("=" * 60)
    response, was_paused = send_message(prompt2)

    if was_paused:
        print(f"   ⏸️  Compaction triggered — API paused! {status_color(True)}")
        print(f"   stop_reason: {response.get('stop_reason')}")
        print(f"   Content blocks: {len(response.get('content', []))}")

        # Show the compaction summary
        for block in response.get("content", []):
            if block.get("type") == "compaction":
                summary = block.get("content", "")[:300]
                print(f"\n   📦 Compaction summary (first 300 chars):")
                print(f"   {summary}...")

        # =================================================================
        # Inspect → Inject → Continue: the core pause_after_compaction flow.
        # =================================================================
        print("\n" + "=" * 60)
        print("📋 Inspect → Inject reminder → Continue")
        print("=" * 60)

        # Append the compacted response to conversation history
        messages.append({
            "role": "assistant",
            "content": response["content"]
        })

        # Inject a reminder about Turn 1 findings
        reminder = (
            "[IMPORTANT: In the User Management API review, we identified "
            "SQL injection in sort_by, broken object-level authorization, "
            "and SSRF via webhooks as critical issues. Keep these in mind "
            "when reviewing the Payment API — check for the same patterns.]"
        )
        print(f"\n   💉 Injecting reminder about Turn 1 findings...")
        print(f"   ▶️  Continuing request (pause_after_compaction=False)...")

        response, was_paused = send_message(reminder, pause_on_compaction=False)
        text = extract_text(response)
        usage = response.get("usage", {})
        print(f"\n   Response: {text[:300]}...")
        print(f"   ⏸️  Compaction paused: {status_color(was_paused)}")
        print(f"   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")
    else:
        text = extract_text(response)
        print(f"   Response: {text[:200]}...")
        print(f"   ⏸️  Compaction paused: {status_color(was_paused)}")

    # =========================================================================
    # Turn 3: Post-compaction follow-up. Proves context survived compaction.
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"{turn_header(3, 'Post-compaction follow-up (context check)')}")
    print("=" * 60)

    followup = (
        "Summarize the key security and performance findings from both API "
        "reviews in a single prioritized list. Reference specific endpoints."
    )
    response, was_paused = send_message(followup, pause_on_compaction=False)
    text = extract_text(response)
    usage = response.get("usage", {})
    print(f"   Response: {text[:500]}...")
    print(f"   ⏸️  Compaction paused: {status_color(was_paused)}")
    print(f"   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")

    print("\n" + "-" * 60)
    print("✅ Pause after compaction demo completed!")
    print("\n💡 The pause_after_compaction workflow:")
    print("   1. Turn 1 builds context (under threshold — no compaction)")
    print("   2. Turn 2 pushes past threshold → compaction → API pauses")
    print("   3. Inspect summary, inject reminders, continue request")
    print("   4. Turn 3 works normally with compacted context")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
