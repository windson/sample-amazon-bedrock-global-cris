#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using Converse API
Demonstrates basic usage of Claude Sonnet 5 with Global CRIS

Note: Converse API does not support adaptive thinking during beta.
For adaptive thinking, use InvokeModel API.

Note: Claude Sonnet 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Note: Claude Sonnet 5 has adaptive thinking ALWAYS ON — it cannot be disabled.
The effort level is configurable via InvokeModel API.

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import boto3

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Sonnet 5
MODEL_ID = "global.anthropic.claude-sonnet-5"

try:
    print("🚀 Invoking Claude Sonnet 5 via Global CRIS...")

    # Use Converse API for simplified interaction
    # Note: Do not pass temperature, top_p, or top_k — they are not supported
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
    print("💡 Claude Sonnet 5 has adaptive thinking always on with 1M context window")
    print("💡 For adaptive thinking with effort control, use InvokeModel API")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your AWS credentials and region configuration.")
