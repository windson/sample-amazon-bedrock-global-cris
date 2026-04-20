#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using Converse API
Demonstrates basic usage of Claude Opus 4.7 with Global CRIS

Note: Converse API does not support adaptive thinking during beta.
For adaptive thinking, use InvokeModel API.

Note: Claude Opus 4.7 no longer supports temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Author: Navule Pavan Kumar Rao
Date: April 20, 2026
"""

import boto3

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Opus 4.7
MODEL_ID = "global.anthropic.claude-opus-4-7"

try:
    print("🚀 Invoking Claude Opus 4.7 via Global CRIS...")

    # Use Converse API for simplified interaction
    # Note: Do not pass temperature, top_p, or top_k — they are no longer supported
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
    print("💡 Claude Opus 4.7 is Anthropic's most capable GA model with 1M context window")
    print("💡 For adaptive thinking support, use InvokeModel API")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your AWS credentials and region configuration.")
