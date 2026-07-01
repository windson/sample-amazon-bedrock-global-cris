#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS streaming example using ConverseStream API
Demonstrates Claude Sonnet 5 with streaming

Note: ConverseStream API does not support adaptive thinking during beta.
For adaptive thinking, use InvokeModelWithResponseStream API.

Note: Claude Sonnet 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Note: Claude Sonnet 5 has adaptive thinking ALWAYS ON — it cannot be disabled.
The effort level is configurable via InvokeModel API.

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import boto3
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Sonnet 5
MODEL_ID = "global.anthropic.claude-sonnet-5"

# Prompt
PROMPT = "Explain the benefits of serverless computing in 3 bullet points."

print("🌍 Amazon Bedrock Global CRIS Streaming Demo")
print("🚀 Model: Claude Sonnet 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("\n💬 Streaming Response:")
print("-" * 50)

try:
    # Create conversation with single user message
    conversation = [{"role": "user", "content": [{"text": PROMPT}]}]

    # Stream response using ConverseStream API
    # Note: Do not pass temperature, top_p, or top_k — they are not supported
    streaming_response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=conversation,
        inferenceConfig={"maxTokens": 4096},
    )

    # Process and display streaming response in real-time
    usage_info = None
    for chunk in streaming_response["stream"]:
        if "contentBlockDelta" in chunk:
            text = chunk["contentBlockDelta"]["delta"]["text"]
            print(text, end="", flush=True)
        elif "metadata" in chunk:
            # Capture usage information from metadata event
            usage_info = chunk["metadata"].get("usage")

    print("\n" + "-" * 50)
    print("✅ Streaming completed successfully!")
    print("🌐 Request automatically routed to optimal region via Global CRIS")
    print("💡 Claude Sonnet 5 has adaptive thinking always on with 1M context window")
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
