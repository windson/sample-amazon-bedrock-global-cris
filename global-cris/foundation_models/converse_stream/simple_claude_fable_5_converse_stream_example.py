#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS streaming example using ConverseStream API
Demonstrates Claude Fable 5 with streaming

Note: ConverseStream API does not support adaptive thinking during beta.
For adaptive thinking, use InvokeModelWithResponseStream API.

Note: Claude Fable 5 sampling constraints: temperature must be 1.0 or unset;
top_p must be >= 0.99 or unset; top_k is not supported.

Note: Claude Fable 5 has adaptive thinking ALWAYS ON — it cannot be disabled.
The effort level is configurable via InvokeModel API.

Note: Requires data retention opt-in (provider_data_share) before first invocation.

Note: The model may return stop_reason: 'refusal' for dual-use content (cyber/bio).

References:
- Claude Fable 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html
- Blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import boto3
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"

# Prompt
PROMPT = "Explain the benefits of serverless computing in 3 bullet points."

print("🌍 Amazon Bedrock Global CRIS Streaming Demo")
print("🚀 Model: Claude Fable 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")
print("\n💬 Streaming Response:")
print("-" * 50)

try:
    # Create conversation with single user message
    conversation = [{"role": "user", "content": [{"text": PROMPT}]}]

    # Stream response using ConverseStream API
    # Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is not supported
    streaming_response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=conversation,
        inferenceConfig={"maxTokens": 4096},
    )

    # Process and display streaming response in real-time
    usage_info = None
    for chunk in streaming_response["stream"]:
        if "contentBlockDelta" in chunk:
            delta = chunk["contentBlockDelta"]["delta"]
            # Fable 5 has adaptive thinking always on, so deltas may include
            # reasoningContent blocks alongside text blocks
            if "text" in delta:
                print(delta["text"], end="", flush=True)
        elif "metadata" in chunk:
            # Capture usage information from metadata event
            usage_info = chunk["metadata"].get("usage")

    print("\n" + "-" * 50)
    print("✅ Streaming completed successfully!")
    print("🌐 Request automatically routed to optimal region via Global CRIS")
    print("💡 Claude Fable 5 has adaptive thinking always on with 1M context window")
    print("💡 For adaptive thinking with effort control, use InvokeModelWithResponseStream API")

    # Display token usage if available
    if usage_info:
        print("🔢 Token Usage:")
        print(f"   Input tokens: {usage_info.get('inputTokens', 'N/A')}")
        print(f"   Output tokens: {usage_info.get('outputTokens', 'N/A')}")
        print(f"   Total tokens: {usage_info.get('totalTokens', 'N/A')}")

except ClientError as e:
    print(f"❌ Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
