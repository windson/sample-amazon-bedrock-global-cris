#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 5 Adaptive Thinking + Disable
(InvokeModelWithResponseStream)

Demonstrates adaptive thinking on Claude Opus 5 via streaming with three modes:
- ON with effort='max': deep thinking blocks streamed for complex reasoning
- ON with effort='low': lighter reasoning for simpler queries
- DISABLED: thinking turned off entirely (effort capped at 'high')

Claude Opus 5 has adaptive thinking ON by default but CAN be disabled.
When disabled, the effort parameter is capped at 'high'.
Opus 5 supports effort levels: low, medium, high, xhigh, max

Note: Claude Opus 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

References:
- Adaptive thinking: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html
- Effort parameter: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
- Thinking differences: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-thinking-differences.html
- Claude Opus 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html
- Blog: https://aws.amazon.com/blogs/machine-learning/introducing-claude-opus-5-on-aws-anthropics-most-capable-opus-model/

Author: Navule Pavan Kumar Rao
Date: July 24, 2026

Expected output:
=================
  - effort='max'  -> Thinking block streamed (green), deep reasoning
  - effort='low'  -> No thinking block (orange), concise answer
  - DISABLED      -> No thinking block, effort capped at 'high'
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

# Global CRIS model ID for Claude Opus 5
MODEL_ID = "global.anthropic.claude-opus-5"


def stream_with_adaptive_thinking(prompt: str, effort: str = "max", max_tokens: int = 16000):
    """
    Stream a response with adaptive thinking enabled and effort control.

    Args:
        prompt: The user prompt.
        effort: Reasoning depth. Opus 5 supports:
                "low", "medium", "high", "xhigh", "max"
        max_tokens: Maximum output tokens.

    Returns:
        Tuple of (thinking_detected: bool, thinking_content: str, text_content: str).
    """
    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 5
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Effort beta header — required to use output_config.effort
        "anthropic_beta": ["effort-2025-11-24"],
        "max_tokens": max_tokens,
        # Adaptive thinking: ON by default on Opus 5
        "thinking": {
            "type": "adaptive"
        },
        # Effort parameter: guides reasoning depth
        # Opus 5: low, medium, high, xhigh, max
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

    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    thinking_content = ""
    text_content = ""
    thinking_detected = False

    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            block_type = block.get("type")
            if block_type == "thinking":
                thinking_detected = True
                print(f"\n{GREEN}🤔 [Thinking block detected]{RESET}")
            elif block_type == "text":
                print("\n📝 [Response]:")

        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "thinking_delta":
                thinking = delta.get("thinking", "")
                thinking_content += thinking
                print(f"\033[90m{thinking}\033[0m", end="", flush=True)

            elif delta_type == "text_delta":
                text = delta.get("text", "")
                text_content += text
                print(text, end="", flush=True)

    return thinking_detected, thinking_content, text_content


def stream_with_thinking_disabled(prompt: str, max_tokens: int = 16000):
    """
    Stream a response with adaptive thinking DISABLED.

    When thinking is disabled, effort is capped at 'high'.
    This mode is useful for low-latency responses where reasoning
    overhead is not desired.

    Args:
        prompt: The user prompt.
        max_tokens: Maximum output tokens.

    Returns:
        Tuple of (thinking_detected: bool, thinking_content: str, text_content: str).
    """
    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 5
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        # Disable thinking: Opus 5 allows this (unlike Sonnet 5/Fable 5)
        "thinking": {
            "type": "disabled"
        },
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    text_content = ""
    thinking_detected = False

    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            block_type = block.get("type")
            if block_type == "text":
                print("\n📝 [Response]:")

        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "text_delta":
                text = delta.get("text", "")
                text_content += text
                print(text, end="", flush=True)

    return thinking_detected, "", text_content


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 5 Adaptive Thinking + Disable (Streaming)")
print("🚀 Model: Claude Opus 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print("⚠️  Note: temperature, top_p, and top_k are not supported")
print("💡 Opus 5 has thinking ON by default but CAN be disabled")

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

    thinking_detected, thinking, text = stream_with_adaptive_thinking(prompt_max, effort="max")

    print(f"\n\n   🧠 Claude decided to think: {GREEN}{thinking_detected}{RESET}" if thinking_detected
          else f"\n\n   🧠 Claude decided to think: {ORANGE}{thinking_detected}{RESET}")
    if thinking_detected and len(thinking) > 0:
        print(f"   📊 Thinking: {len(thinking):,} chars | Response: {len(text):,} chars")
    else:
        print(f"   📊 Response: {len(text):,} chars")

    # =========================================================================
    # Query 2: effort='low' — skips thinking, concise answer
    # =========================================================================
    prompt_low = "What is the capital of France?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 effort='low' — Minimal reasoning{RESET}")
    print("=" * 60)
    print(f"📝 Prompt: {prompt_low}")
    print("-" * 50)

    thinking_detected, thinking, text = stream_with_adaptive_thinking(prompt_low, effort="low", max_tokens=4000)

    print(f"\n\n   🧠 Claude decided to think: {GREEN}{thinking_detected}{RESET}" if thinking_detected
          else f"\n\n   🧠 Claude decided to think: {ORANGE}{thinking_detected}{RESET}")
    print(f"   📊 Response: {len(text):,} chars")

    # =========================================================================
    # Query 3: Thinking DISABLED — no reasoning blocks, effort capped at 'high'
    # =========================================================================
    prompt_disabled = "What are the three states of matter?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 Thinking DISABLED — No reasoning, effort capped at 'high'{RESET}")
    print("=" * 60)
    print(f"📝 Prompt: {prompt_disabled}")
    print("-" * 50)

    thinking_detected, thinking, text = stream_with_thinking_disabled(prompt_disabled, max_tokens=4000)

    print(f"\n\n   🧠 Claude decided to think: {GREEN}{thinking_detected}{RESET}" if thinking_detected
          else f"\n\n   🧠 Claude decided to think: {ORANGE}{thinking_detected}{RESET}")
    print(f"   📊 Response: {len(text):,} chars")

    print("\n✅ Adaptive thinking + disable streaming demo completed!")
    print("💡 Opus 5 effort levels: low, medium, high, xhigh, max")
    print("💡 effort='max' triggers thinking blocks; lower levels may skip them")
    print("💡 Thinking CAN be disabled on Opus 5 (effort capped at 'high' when disabled)")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
