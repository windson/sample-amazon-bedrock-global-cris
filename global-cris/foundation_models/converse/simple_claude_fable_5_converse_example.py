#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using Converse API
Demonstrates basic usage of Claude Fable 5 with Global CRIS

Note: Converse API does not support adaptive thinking during beta.
For adaptive thinking, use InvokeModel API.

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

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"

try:
    print("🚀 Invoking Claude Fable 5 via Global CRIS...")
    print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")

    # Use Converse API for simplified interaction
    # Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is not supported
    response = bedrock.converse(
        messages=[
            {
                "role": "user",
                "content": [{"text": "Explain cloud computing in 2 sentences."}],
            }
        ],
        modelId=MODEL_ID,
    )

    # Extract and display response
    response_text = response["output"]["message"]["content"][0]["text"]
    print("Response:", response_text)

    # Display token usage information
    usage = response.get("usage", {})
    print("Tokens used:", usage)

    if usage:
        print(f"Input tokens: {usage.get('inputTokens', 'N/A')}")
        print(f"Output tokens: {usage.get('outputTokens', 'N/A')}")
        print(f"Total tokens: {usage.get('totalTokens', 'N/A')}")

    print("\n✅ Global CRIS request completed successfully!")
    print("💡 Claude Fable 5 has adaptive thinking always on with 1M context window")
    print("💡 For adaptive thinking with effort control, use InvokeModel API")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your AWS credentials and region configuration.")
