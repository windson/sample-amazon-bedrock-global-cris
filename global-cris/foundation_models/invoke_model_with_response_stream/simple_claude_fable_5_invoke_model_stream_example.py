#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS streaming example using InvokeModelWithResponseStream API
Demonstrates basic Claude Fable 5 streaming with Global CRIS

Note: Claude Fable 5 sampling constraints: temperature must be 1.0 or unset;
top_p must be >= 0.99 or unset; top_k is not supported.

Note: Claude Fable 5 has adaptive thinking ALWAYS ON — it cannot be disabled.
The effort level is configurable via the effort parameter.

Note: Requires data retention opt-in (provider_data_share) before first invocation.

Note: The model may return stop_reason: 'refusal' for dual-use content (cyber/bio).

For advanced features like adaptive thinking and compaction,
see advanced_examples/claude_fable_5/

References:
- Claude Fable 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html
- Blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import boto3
import json
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"

# Prompt
PROMPT = "Explain the benefits of serverless computing in 3 bullet points."

print("🌍 Amazon Bedrock Global CRIS InvokeModelWithResponseStream Demo")
print("🚀 Model: Claude Fable 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")
print("\n💬 Streaming Response:")
print("-" * 50)

try:
    # Basic request — adaptive thinking is always on for Fable 5
    # Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is not supported
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": PROMPT}],
            }
        ],
    }

    # Convert the native request to JSON
    request_body = json.dumps(native_request)

    # Invoke the model with streaming response
    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID, body=request_body, contentType="application/json"
    )

    # Extract and print the response text in real-time
    complete_response = ""
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            if chunk["delta"].get("type") == "text_delta":
                text = chunk["delta"].get("text", "")
                print(text, end="", flush=True)
                complete_response += text

    print("\n" + "-" * 50)
    print("✅ InvokeModelWithResponseStream completed successfully!")
    print("🌐 Request automatically routed to optimal region via Global CRIS")
    print(f"📊 Response length: {len(complete_response)} characters")

except ClientError as e:
    print(f"❌ Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
