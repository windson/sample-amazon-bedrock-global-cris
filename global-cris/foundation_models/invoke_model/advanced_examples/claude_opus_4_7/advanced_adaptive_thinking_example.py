#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 4.7 Adaptive Thinking + Effort (InvokeModel)

Demonstrates adaptive thinking combined with the effort parameter on Claude Opus 4.7:
- Adaptive thinking is the only supported thinking mode on Opus 4.7
  (manual thinking with budget_tokens is NOT supported)
- effort='max' triggers thinking blocks; lower levels may skip them
- Opus 4.7 supports: low, medium, high, xhigh (4.7 exclusive), max

Note: Claude Opus 4.7 no longer supports temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

References:
- Adaptive thinking: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html
- Effort parameter: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
- Thinking differences: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-thinking-differences.html
- Claude Opus 4.7 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html

Author: Navule Pavan Kumar Rao
Date: April 20, 2026

Expected output:
=================
  - effort='max'  → Thinking block detected (green), deep reasoning
  - effort='low'  → No thinking block (orange), concise answer
"""

import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from common.colors import MAGENTA, BOLD, RESET, GREEN, ORANGE

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    config=Config(read_timeout=300)
)

# Global CRIS model ID for Claude Opus 4.7
MODEL_ID = "global.anthropic.claude-opus-4-7"


def invoke_with_adaptive_thinking(prompt: str, effort: str = "max", max_tokens: int = 16000):
    """
    Invoke Claude Opus 4.7 with adaptive thinking and effort control.

    Args:
        prompt: The user prompt.
        effort: Reasoning depth. Opus 4.7 supports:
                "low", "medium", "high", "xhigh" (4.7 exclusive), "max"
        max_tokens: Maximum output tokens.
    """
    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 4.7
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Effort beta header — required to use output_config.effort
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
        "anthropic_beta": ["effort-2025-11-24"],
        "max_tokens": max_tokens,
        # Adaptive thinking: only supported thinking mode on Opus 4.7
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html
        "thinking": {
            "type": "adaptive"
        },
        # Effort parameter: guides reasoning depth
        # Opus 4.7: low, medium, high, xhigh (exclusive), max
        "output_config": {
            "effort": effort
        },
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    return json.loads(response["body"].read())


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.7 Adaptive Thinking + Effort")
print("🚀 Model: Claude Opus 4.7 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print("⚠️  Note: temperature, top_p, and top_k are no longer supported")

try:
    # =========================================================================
    # Query 1: effort='max' — triggers thinking blocks
    # =========================================================================
    prompt_max = "Explain why the sum of two even numbers is always even."

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 effort='max' — Maximum reasoning depth{RESET}")
    print("=" * 60)
    print(f"📝 Prompt: {prompt_max}")
    print("-" * 50)

    response = invoke_with_adaptive_thinking(prompt_max, effort="max")

    has_thinking = any(b["type"] == "thinking" for b in response["content"])
    print(f"\n   🧠 Claude decided to think: {GREEN}{has_thinking}{RESET}" if has_thinking
          else f"\n   🧠 Claude decided to think: {ORANGE}{has_thinking}{RESET}")

    for block in response["content"]:
        if block["type"] == "thinking":
            print(f"\n   {GREEN}🤔 [Thinking block detected]{RESET}")
            print(f"   [Thinking (first 500 chars)]:\n   {block['thinking'][:500]}...")
        elif block["type"] == "text":
            print(f"\n   📝 [Response]:\n   {block['text']}")

    usage = response.get("usage", {})
    print(f"\n   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")

    # =========================================================================
    # Query 2: effort='low' — skips thinking, concise answer
    # =========================================================================
    prompt_low = "What is the capital of France?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 effort='low' — Minimal reasoning{RESET}")
    print("=" * 60)
    print(f"📝 Prompt: {prompt_low}")
    print("-" * 50)

    response = invoke_with_adaptive_thinking(prompt_low, effort="low", max_tokens=4000)

    has_thinking = any(b["type"] == "thinking" for b in response["content"])
    print(f"\n   🧠 Claude decided to think: {GREEN}{has_thinking}{RESET}" if has_thinking
          else f"\n   🧠 Claude decided to think: {ORANGE}{has_thinking}{RESET}")

    for block in response["content"]:
        if block["type"] == "text":
            print(f"\n   📝 [Response]: {block['text']}")
            break

    usage = response.get("usage", {})
    print(f"   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")

    print("\n✅ Adaptive thinking + effort demo completed!")
    print("💡 Opus 4.7 effort levels: low, medium, high, xhigh (exclusive), max")
    print("💡 effort='max' triggers thinking blocks; lower levels may skip them")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
