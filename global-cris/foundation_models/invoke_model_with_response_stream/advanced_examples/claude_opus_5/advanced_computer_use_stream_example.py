#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 5 Computer Use
(InvokeModelWithResponseStream)

Demonstrates computer use tool with streaming on Claude Opus 5:
- Defines a computer_20251124 tool for screen interaction
- Sends a task and streams the model response
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
  - Model streams text and tool_use blocks with computer actions
  - Coordinates and action details are included in streamed chunks
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


def stream_with_computer_use(prompt: str, display_width: int = 1920, display_height: int = 1080):
    """
    Stream a response from Claude Opus 5 with computer use tool enabled.

    The computer_20251124 tool allows the model to interact with
    a virtual desktop by specifying actions like click, type,
    screenshot, scroll, etc.

    Args:
        prompt: The user prompt describing the task.
        display_width: Screen width in pixels.
        display_height: Screen height in pixels.

    Returns:
        Tuple of (text_content, tool_use_blocks).
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

    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    text_content = ""
    tool_use_blocks = []
    current_tool_input = ""
    current_tool_name = ""
    current_tool_id = ""
    in_tool_use = False

    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            block_type = block.get("type")
            if block_type == "text":
                print("\n📝 [Text]:", end=" ")
            elif block_type == "tool_use":
                in_tool_use = True
                current_tool_name = block.get("name", "unknown")
                current_tool_id = block.get("id", "")
                current_tool_input = ""
                print(f"\n{GREEN}🖱️  [Tool Use: {current_tool_name}]{RESET}")

        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "text_delta":
                text = delta.get("text", "")
                text_content += text
                print(text, end="", flush=True)

            elif delta_type == "input_json_delta":
                # Accumulate tool input JSON
                partial_json = delta.get("partial_json", "")
                current_tool_input += partial_json

        elif chunk["type"] == "content_block_stop":
            if in_tool_use and current_tool_input:
                try:
                    tool_input = json.loads(current_tool_input)
                except json.JSONDecodeError:
                    tool_input = {"raw": current_tool_input}

                tool_use_blocks.append({
                    "name": current_tool_name,
                    "id": current_tool_id,
                    "input": tool_input
                })

                # Display tool action details
                action = tool_input.get("action", "unknown")
                print(f"   Action: {action}")
                if action in ("click", "mouse_move"):
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

                in_tool_use = False

    return text_content, tool_use_blocks


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 5 Computer Use (Streaming)")
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
    print(f"{MAGENTA}{BOLD}🔹 Computer Use — Desktop interaction (Streaming){RESET}")
    print("=" * 60)
    print(f"📝 Task: {prompt}")
    print(f"🖥️  Display: 1920x1080")
    print("-" * 50)

    text_content, tool_use_blocks = stream_with_computer_use(prompt)

    if tool_use_blocks:
        print(f"\n\n   {GREEN}✅ Model returned {len(tool_use_blocks)} computer use action(s){RESET}")
        for i, tool_block in enumerate(tool_use_blocks, 1):
            print(f"   Action {i}: {tool_block['input'].get('action', 'unknown')}")
        print("\n   In a real implementation, you would:")
        print("   1. Execute the action on the virtual desktop")
        print("   2. Capture a screenshot of the result")
        print("   3. Send the screenshot back as a tool_result")
        print("   4. Continue the conversation loop")
    else:
        print("\n\n   ℹ️  Model responded with text only (no tool_use block)")

    print("\n" + "=" * 60)
    print("✅ Computer use streaming demo completed!")
    print("💡 Tool type: computer_20251124")
    print("💡 Actions: click, type, key, screenshot, scroll, mouse_move, etc.")
    print("💡 Streaming allows real-time display of model reasoning before actions")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/computer-use.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
