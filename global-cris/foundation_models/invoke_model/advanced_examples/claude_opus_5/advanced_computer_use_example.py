#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 5 Computer Use (InvokeModel)

Demonstrates computer use tool with Claude Opus 5:
- Defines a computer_20251124 tool for screen interaction
- Sends a screenshot and asks the model to perform an action
- Model returns tool_use blocks with coordinates for interaction

Computer use requirements for Claude Opus 5:
- Tool type: computer_20251124
- Beta header: computer-use-2025-11-24
- Returns tool_use results with action, coordinates

Note: Claude Opus 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Note: Claude Opus 5 does NOT require data retention opt-in
(zero data retention by default).

References:
- Computer use: https://docs.aws.amazon.com/bedrock/latest/userguide/computer-use.html
- Claude Opus 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html
- Blog: https://aws.amazon.com/blogs/machine-learning/introducing-claude-opus-5-on-aws-anthropics-most-capable-opus-model/

Author: Navule Pavan Kumar Rao
Date: July 24, 2026

Expected output:
=================
  - Model returns tool_use block with computer action (click, type, etc.)
  - Coordinates and action details are included in the response
"""

import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from common.colors import MAGENTA, BOLD, RESET, GREEN

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    config=Config(read_timeout=300)
)

# Global CRIS model ID for Claude Opus 5
MODEL_ID = "global.anthropic.claude-opus-5"


def invoke_with_computer_use(prompt: str, display_width: int = 1920, display_height: int = 1080):
    """
    Invoke Claude Opus 5 with computer use tool enabled.

    The computer_20251124 tool allows the model to interact with
    a virtual desktop by specifying actions like click, type,
    screenshot, scroll, etc.

    Args:
        prompt: The user prompt describing the task.
        display_width: Screen width in pixels.
        display_height: Screen height in pixels.

    Returns:
        The full model response dict.
    """
    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 5
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Computer use beta header — required for computer_20251124 tool
        "anthropic_beta": ["computer-use-2025-11-24"],
        "max_tokens": 4096,
        # Computer use tool definition
        "tools": [
            {
                "type": "computer_20251124",
                "name": "computer",
                "display_width_px": display_width,
                "display_height_px": display_height,
                "display_number": 1
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    return json.loads(response["body"].read())


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 5 Computer Use")
print("🚀 Model: Claude Opus 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print("⚠️  Note: temperature, top_p, and top_k are not supported")
print("💡 Computer use tool: computer_20251124")
print("💡 Beta header: computer-use-2025-11-24")

try:
    # =========================================================================
    # Example: Ask model to perform a computer action
    # =========================================================================
    prompt = (
        "Open a web browser and navigate to https://aws.amazon.com. "
        "Take a screenshot first to see the current state of the desktop."
    )

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 Computer Use — Desktop interaction{RESET}")
    print("=" * 60)
    print(f"📝 Task: {prompt}")
    print(f"🖥️  Display: 1920x1080")
    print("-" * 50)

    response = invoke_with_computer_use(prompt)

    # Process response blocks
    has_tool_use = False
    for block in response["content"]:
        if block["type"] == "text":
            print(f"\n   📝 [Text]: {block['text']}")
        elif block["type"] == "tool_use":
            has_tool_use = True
            tool_name = block.get("name", "unknown")
            tool_input = block.get("input", {})
            action = tool_input.get("action", "unknown")
            print(f"\n   {GREEN}🖱️  [Tool Use: {tool_name}]{RESET}")
            print(f"   Action: {action}")

            # Display action-specific details
            if action == "click" or action == "mouse_move":
                coords = tool_input.get("coordinate", [])
                print(f"   Coordinates: {coords}")
            elif action == "type":
                text = tool_input.get("text", "")
                print(f"   Text: {text}")
            elif action == "key":
                key = tool_input.get("text", "")
                print(f"   Key: {key}")
            elif action == "screenshot":
                print("   (Requesting screenshot of current state)")

            # Print full tool input for reference
            print(f"   Full input: {json.dumps(tool_input, indent=2)}")

    if has_tool_use:
        print(f"\n   {GREEN}✅ Model returned computer use actions{RESET}")
        print("   In a real implementation, you would:")
        print("   1. Execute the action on the virtual desktop")
        print("   2. Capture a screenshot of the result")
        print("   3. Send the screenshot back as a tool_result")
        print("   4. Continue the conversation loop")
    else:
        print("\n   ℹ️  Model responded with text only (no tool_use block)")

    # Display usage
    usage = response.get("usage", {})
    print(f"\n   🔢 Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out")

    print("\n" + "=" * 60)
    print("✅ Computer use demo completed!")
    print("💡 Tool type: computer_20251124")
    print("💡 Actions: click, type, key, screenshot, scroll, mouse_move, etc.")
    print("💡 Returns coordinates and action details for desktop automation")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/computer-use.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
