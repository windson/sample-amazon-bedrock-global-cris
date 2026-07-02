#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using InvokeModel API
Demonstrates basic Claude Fable 5 inference with Global CRIS

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

import json

import boto3
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"

# Simple prompt for testing
PROMPT = "Explain the CAP theorem in distributed systems."

print("🌍 Amazon Bedrock Global CRIS InvokeModel Demo")
print("🚀 Model: Claude Fable 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📝 Prompt: {PROMPT}")
print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")
print("\n💬 Response:")
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
