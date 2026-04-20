#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS streaming example using InvokeModelWithResponseStream API
Demonstrates basic Claude Opus 4.7 streaming with Global CRIS

Note: Claude Opus 4.7 no longer supports temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

For advanced features like adaptive thinking and compaction,
see advanced_claude_opus_4_7_invoke_model_stream_example.py

Author: Navule Pavan Kumar Rao
Date: April 20, 2026
"""

import boto3
import json
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Opus 4.7
MODEL_ID = "global.anthropic.claude-opus-4-7"

# Prompt
PROMPT = "Explain the benefits of serverless computing in 3 bullet points."

print("🌍 Amazon Bedrock Global CRIS InvokeModelWithResponseStream Demo")
print("🚀 Model: Claude Opus 4.7 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("\n💬 Streaming Response:")
print("-" * 50)

try:
    # Basic request without adaptive thinking
    # Note: temperature, top_p, and top_k are no longer supported in Opus 4.7
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
