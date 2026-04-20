#!/usr/bin/env python3
"""
Advanced Amazon Bedrock Global CRIS streaming example using InvokeModelWithResponseStream API
Demonstrates Claude Opus 4.6 advanced features with streaming:
- Adaptive thinking with effort levels and streaming thinking blocks
- Compaction with streaming responses
- Real-time thinking visualization

Compaction is in beta and requires the anthropic_beta header.

Author: Navule Pavan Kumar Rao
Date: March 3, 2026
"""

import json
import boto3
from botocore.exceptions import ClientError

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Global CRIS model ID for Claude Opus 4.6
MODEL_ID = "global.anthropic.claude-opus-4-6-v1"


def demo_adaptive_thinking_stream():
    """
    Demonstrate adaptive thinking with streaming and effort control.
    
    With streaming, you can see Claude's thinking in real-time
    as it reasons through complex problems.
    
    Effort levels for Opus 4.6: low, medium, high, max
    Requires beta header: "effort-2025-11-24"
    
    Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
    """
    print("\n" + "=" * 60)
    print("🧠 DEMO 1: Adaptive Thinking with Streaming (effort='max')")
    print("=" * 60)
    
    # Complex prompt that benefits from extended thinking
    complex_prompt = """Analyze the trade-offs between using a monolithic architecture 
versus microservices for a startup building a real-time collaboration tool. 
Consider team size, deployment complexity, and scaling requirements."""

    print(f"\n📝 Prompt: {complex_prompt}")
    print("\n💬 Streaming Response (with thinking):")
    print("-" * 50)
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Effort beta header — required to use output_config.effort
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
        "anthropic_beta": ["effort-2025-11-24"],
        "max_tokens": 8000,
        # Adaptive thinking: Claude dynamically decides when/how much to think
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html
        "thinking": {
            "type": "adaptive"
        },
        # Effort parameter: guides how liberally Claude spends tokens
        # Opus 4.6 levels: "low", "medium", "high", "max"
        "output_config": {
            "effort": "max"
        },
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": complex_prompt}]
            }
        ]
    }
    
    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    # Track what we're currently streaming
    current_block_type = None
    thinking_content = ""
    text_content = ""
    
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        
        # Handle content block start
        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            current_block_type = block.get("type")
            if current_block_type == "thinking":
                print("\n🤔 [Claude's Thinking]:")
            elif current_block_type == "text":
                print("\n\n📝 [Response]:")
        
        # Handle content block delta
        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            delta_type = delta.get("type")
            
            if delta_type == "thinking_delta":
                thinking = delta.get("thinking", "")
                thinking_content += thinking
                # Stream thinking in real-time (dimmed for visual distinction)
                print(f"\033[90m{thinking}\033[0m", end="", flush=True)
            
            elif delta_type == "text_delta":
                text = delta.get("text", "")
                text_content += text
                print(text, end="", flush=True)
        
        # Handle message delta (contains usage info)
        elif chunk["type"] == "message_delta":
            pass  # Usage info available here
    
    print("\n" + "-" * 50)
    print(f"\n📊 Thinking length: {len(thinking_content)} characters")
    print(f"📊 Response length: {len(text_content)} characters")
    print("✅ Adaptive thinking streaming demo completed!")


def demo_effort_levels_stream():
    """
    Demonstrate adaptive thinking with effort='low' via streaming.
    
    Effort levels for Opus 4.6: low, medium, high, max
    Requires beta header: "effort-2025-11-24"
    
    Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html#effort-parameter-beta
    """
    print("\n" + "=" * 60)
    print("⚡ DEMO 2: Adaptive Thinking Streaming (effort='low')")
    print("=" * 60)
    
    prompt = "What are the key principles of clean code architecture?"
    
    print(f"\n🔹 Testing adaptive thinking with effort='low'")
    print("-" * 40)
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Effort beta header — required to use output_config.effort
        "anthropic_beta": ["effort-2025-11-24"],
        "max_tokens": 4000,
        # Adaptive thinking: Claude dynamically decides when/how much to think
        "thinking": {
            "type": "adaptive"
        },
        # Effort "low": Claude minimizes thinking, prioritizes speed
        "output_config": {
            "effort": "low"
        },
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
    
    has_thinking = False
    text_content = ""
    
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        
        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            if block.get("type") == "thinking":
                has_thinking = True
        
        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                text_content += text
                print(text, end="", flush=True)
    
    print(f"\n   Claude decided to think: {has_thinking}")
    print(f"   Response length: {len(text_content)} characters")
    
    print("\n✅ Adaptive thinking streaming demo completed!")


def demo_compaction_stream():
    """
    Demonstrate compaction with streaming responses.
    
    Compaction works with streaming - you'll see the compaction
    block in the stream when it triggers.
    """
    print("\n" + "=" * 60)
    print("📦 DEMO 3: Compaction with Streaming")
    print("=" * 60)
    
    print("\n💡 Compaction is in beta - requires anthropic_beta header")
    
    messages = []
    
    def chat_stream(user_message: str, trigger_threshold: int = 100000):
        """Send a message with compaction and streaming."""
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "anthropic_beta": ["compact-2026-01-12"],
            "max_tokens": 4096,
            "messages": messages,
            "context_management": {
                "edits": [{
                    "type": "compact_20260112",
                    "trigger": {
                        "type": "input_tokens",
                        "value": trigger_threshold
                    }
                }]
            }
        }
        
        streaming_response = bedrock.invoke_model_with_response_stream(
            modelId=MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        response_content = []
        text_content = ""
        has_compaction = False
        
        for event in streaming_response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            
            if chunk["type"] == "content_block_start":
                block = chunk.get("content_block", {})
                block_type = block.get("type")
                if block_type == "compaction":
                    has_compaction = True
                    print("   📦 [Compaction block detected]")
                response_content.append({"type": block_type})
            
            elif chunk["type"] == "content_block_delta":
                delta = chunk.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    text_content += text
                    print(text, end="", flush=True)
        
        # Append assistant response to maintain conversation
        messages.append({
            "role": "assistant",
            "content": text_content
        })
        
        return text_content, has_compaction
    
    # Multi-turn conversation
    print("\n🔹 Starting multi-turn conversation with compaction + streaming...")
    
    prompts = [
        "Design a caching strategy for a high-traffic API.",
        "Now add cache invalidation patterns for data consistency.",
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n   Turn {i}: {prompt}")
        print("-" * 40)
        response, compacted = chat_stream(prompt)
        print(f"\n   Compaction triggered: {compacted}")
    
    print("\n✅ Compaction streaming demo completed!")


def demo_thinking_visualization():
    """
    Demonstrate real-time thinking visualization with formatting.
    
    Shows how to display Claude's thinking process in a user-friendly way.
    """
    print("\n" + "=" * 60)
    print("🎨 DEMO 4: Real-time Thinking Visualization")
    print("=" * 60)
    
    prompt = """A user reports that their Lambda function times out intermittently 
when connecting to RDS. The function works fine most of the time but fails 
during traffic spikes. Diagnose the issue and propose solutions."""

    print(f"\n📝 Prompt: {prompt}")
    print("\n💬 Streaming with formatted thinking:")
    print("-" * 50)
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8000,
        "thinking": {
            "type": "adaptive"
        },
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
    
    current_block_type = None
    thinking_lines = 0
    
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        
        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            current_block_type = block.get("type")
            if current_block_type == "thinking":
                print("\n┌─ 🤔 Claude's Reasoning Process ─────────────────────┐")
            elif current_block_type == "text":
                if thinking_lines > 0:
                    print("\n└─────────────────────────────────────────────────────┘")
                print("\n┌─ 📝 Final Response ──────────────────────────────────┐\n")
        
        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            
            if delta.get("type") == "thinking_delta":
                thinking = delta.get("thinking", "")
                # Format thinking with line prefix
                for char in thinking:
                    if char == '\n':
                        thinking_lines += 1
                        print()
                        print("│ ", end="")
                    else:
                        print(f"\033[90m{char}\033[0m", end="", flush=True)
            
            elif delta.get("type") == "text_delta":
                text = delta.get("text", "")
                print(text, end="", flush=True)
        
        elif chunk["type"] == "message_stop":
            print("\n└─────────────────────────────────────────────────────┘")
    
    print("\n✅ Thinking visualization demo completed!")


def main():
    """Run all streaming demos."""
    print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.6 Advanced Streaming")
    print("🚀 Model: Claude Opus 4.6 (Global CRIS)")
    print("📍 Source Region: ap-south-1 (India)")
    
    try:
        demo_adaptive_thinking_stream()
        demo_effort_levels_stream()
        demo_compaction_stream()
        demo_thinking_visualization()
        
        print("\n" + "=" * 60)
        print("🎉 All streaming demos completed successfully!")
        print("=" * 60)
        print("\n📚 Key takeaways:")
        print("   • Streaming shows thinking in real-time via thinking_delta events")
        print("   • Use content_block_start to detect thinking vs text blocks")
        print("   • Compaction blocks appear in stream when triggered")
        print("   • Format thinking output for better user experience")
        
    except ClientError as e:
        print(f"\n❌ AWS Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
