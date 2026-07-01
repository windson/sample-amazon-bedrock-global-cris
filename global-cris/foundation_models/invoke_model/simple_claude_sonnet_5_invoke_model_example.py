#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using InvokeModel API
Demonstrates basic Claude Sonnet 5 inference with Global CRIS

Note: Claude Sonnet 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Note: Claude Sonnet 5 has adaptive thinking ALWAYS ON — it cannot be disabled.
The effort level is configurable via the effort parameter.

For advanced features like adaptive thinking and compaction,
see advanced_examples/claude_sonnet_5/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import json

import boto3
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Sonnet 5
MODEL_ID = "global.anthropic.claude-sonnet-5"

# Simple prompt for testing
PROMPT = "Explain the CAP theorem in distributed systems."

print("🌍 Amazon Bedrock Global CRIS InvokeModel Demo")
print("🚀 Model: Claude Sonnet 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("\n💬 Response:")
print("-" * 50)

try:
    # Basic request — adaptive thinking is always on for Sonnet 5
    # Note: temperature, top_p, and top_k are not supported in Sonnet 5
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

    # Invoke the model with the request
    response = bedrock.invoke_model(
        modelId=MODEL_ID, body=request_body, contentType="application/json"
    )

    # Decode the response body
    model_response = json.loads(response["body"].read())

    # Extract and print the response text
    print(model_response["content"][0]["text"])

    print("\n" + "-" * 50)
    print("✅ InvokeModel completed successfully!")
    print("🌐 Request automatically routed to optimal region via Global CRIS")

    # Display token usage if available
    if "usage" in model_response:
        usage = model_response["usage"]
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens
        print("🔢 Token Usage:")
        print(f"   Input tokens: {input_tokens}")
        print(f"   Output tokens: {output_tokens}")
        print(f"   Total tokens: {total_tokens}")

except ClientError as e:
    print(f"❌ Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
