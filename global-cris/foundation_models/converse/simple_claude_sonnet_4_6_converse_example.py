#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS example using Converse API
Demonstrates basic usage of Claude Sonnet 4.6 with Global CRIS

Author: Navule Pavan Kumar Rao
Date: March 3, 2026
"""

import boto3

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Sonnet 4.6
MODEL_ID = "global.anthropic.claude-sonnet-4-6"

try:
    print("🚀 Invoking Claude Sonnet 4.6 via Global CRIS...")

    # Use Converse API for simplified interaction
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
    print("💡 Claude Sonnet 4.6 balances intelligence and speed for most tasks")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your AWS credentials and region configuration.")
