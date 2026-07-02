#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Fable 5 Adaptive Thinking + Effort (InvokeModel)

Demonstrates adaptive thinking combined with the effort parameter on Claude Fable 5:
- Adaptive thinking is ALWAYS ON in Fable 5 — it cannot be disabled
- effort='max' triggers deeper thinking blocks; lower levels produce lighter reasoning
- Fable 5 supports: low, medium, high, xhigh, max

Claude Fable 5 is Anthropic's next-generation model for complex knowledge work
and coding, capable of sustained autonomous operation across multi-day tasks.

Note: Claude Fable 5 sampling constraints: temperature must be 1.0 or unset;
top_p must be >= 0.99 or unset; top_k is not supported.

Note: Requires data retention opt-in (provider_data_share) before first invocation.

Note: The model may return stop_reason: 'refusal' for dual-use content (cyber/bio).

References:
- Adaptive thinking: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html
- Effort parameter: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
- Thinking differences: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-thinking-differences.html
- Claude Fable 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html
- Blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026

Expected output:
=================
  - effort='max'  -> Thinking block detected (green), deep reasoning
  - effort='low'  -> Thinking still occurs (always on), but lighter reasoning
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

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"


def invoke_with_adaptive_thinking(prompt: str, effort: str = "max", max_tokens: int = 16000):
    """
    Invoke Claude Fable 5 with adaptive thinking and effort control.

    Note: Adaptive thinking is ALWAYS ON in Fable 5 — it cannot be disabled.
    The effort parameter controls reasoning depth.

    Args:
        prompt: The user prompt.
        effort: Reasoning depth. Fable 5 supports:
                "low", "medium", "high", "xhigh", "max"
        max_tokens: Maximum output tokens.
    """
    # Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is NOT supported
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Effort beta header — required to use output_config.effort
        "anthropic_beta": ["effort-2025-11-24"],
        "max_tokens": max_tokens,
        # Adaptive thinking: ALWAYS ON in Fable 5 (cannot be disabled)
        "thinking": {
            "type": "adaptive"
        },
        # Effort parameter: guides reasoning depth
        # Fable 5: low, medium, high, xhigh, max
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


print("🌍 Amazon Bedrock Global CRIS - Claude Fable 5 Adaptive Thinking + Effort")
print("🚀 Model: Claude Fable 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print("⚠️  Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is not supported")
print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")
print("💡 Adaptive thinking is ALWAYS ON in Fable 5 — effort controls depth")

try:
    # =========================================================================
    # Query 1: effort='max' — deep thinking blocks
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
    # Query 2: effort='low' — lighter reasoning (still always on)
    # =========================================================================
    prompt_low = "What is the capital of France?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 effort='low' — Minimal reasoning (thinking still always on){RESET}")
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
    print("💡 Fable 5 effort levels: low, medium, high, xhigh, max")
    print("💡 Adaptive thinking is ALWAYS ON — effort controls reasoning depth")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
