#!/usr/bin/env python3
"""
Advanced Amazon Bedrock Global CRIS example using InvokeModel API
Demonstrates Claude Opus 4.6 advanced features with Global CRIS:
- Adaptive thinking with effort levels (low, medium, high, max)
- Compaction for long-running conversations
- Custom summarization instructions
- Pause after compaction

Compaction is in beta and requires the anthropic_beta header.
Compaction only works with InvokeModel (not Converse API during beta).

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


def demo_adaptive_thinking():
    """
    Demonstrate adaptive thinking with different effort levels.
    
    Effort levels (when supported):
    - low: Prioritizes speed, minimal thinking
    - medium: Balanced, may skip thinking for simple queries
    - high: Default, reliable deep reasoning
    - max: Exhaustive analysis, Opus 4.6 exclusive
    
    Note: The effort parameter may not be available during initial rollout.
    When omitted, adaptive thinking defaults to high effort.
    """
    print("\n" + "=" * 60)
    print("🧠 DEMO 1: Adaptive Thinking")
    print("=" * 60)
    
    # Complex prompt that benefits from extended thinking
    complex_prompt = """What are the key trade-offs between using DynamoDB 
versus Aurora PostgreSQL for a high-traffic e-commerce application?"""

    print(f"\n📝 Complex Prompt: {complex_prompt}")
    
    # Adaptive thinking (defaults to high effort)
    print("\n🔹 Testing adaptive thinking (defaults to high effort)")
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "thinking": {
            "type": "adaptive"
        },
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": complex_prompt}]
            }
        ]
    }
    
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    model_response = json.loads(response["body"].read())
    
    # Check if Claude chose to think
    has_thinking = any(
        block["type"] == "thinking" for block in model_response["content"]
    )
    print(f"   Claude decided to think: {has_thinking}")
    
    # Handle both thinking and text blocks
    for block in model_response["content"]:
        if block["type"] == "thinking":
            print(f"\n   [Claude's reasoning]:\n   {block['thinking']}")
        elif block["type"] == "text":
            print(f"\n   [Response]:\n   {block['text']}")
    
    # Display token usage
    if "usage" in model_response:
        usage = model_response["usage"]
        print(f"\n   🔢 Token Usage: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out")
    
    # Simple query - Claude may skip thinking
    print("\n🔹 Testing simple query (Claude may skip thinking)")
    
    simple_prompt = "What is the capital of France?"
    
    request_body["messages"] = [
        {"role": "user", "content": [{"type": "text", "text": simple_prompt}]}
    ]
    request_body["max_tokens"] = 2048
    
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    model_response = json.loads(response["body"].read())
    has_thinking = any(
        block["type"] == "thinking" for block in model_response["content"]
    )
    print(f"   Prompt: {simple_prompt}")
    print(f"   Claude decided to think: {has_thinking}")
    
    # Extract text response
    for block in model_response["content"]:
        if block["type"] == "text":
            print(f"   Response: {block['text']}")
            break
    
    print("\n✅ Adaptive thinking demo completed!")


def demo_compaction():
    """
    Demonstrate compaction for long-running conversations.
    
    Compaction automatically summarizes older context when approaching
    the context window limit, enabling longer agent sessions.
    """
    print("\n" + "=" * 60)
    print("📦 DEMO 2: Compaction for Long Conversations")
    print("=" * 60)
    
    print("\n💡 Compaction is in beta - requires anthropic_beta header")
    print("💡 Only works with InvokeModel (not Converse API during beta)")
    
    messages = []
    
    def chat(user_message: str, trigger_threshold: int = 100000):
        """Send a message with compaction enabled."""
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
        
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        model_response = json.loads(response["body"].read())
        
        # Append assistant response to maintain conversation
        messages.append({
            "role": "assistant",
            "content": model_response["content"]
        })
        
        # Check for compaction
        has_compaction = any(
            block.get("type") == "compaction"
            for block in model_response["content"]
        )
        
        # Extract text response
        text_response = ""
        for block in model_response["content"]:
            if block["type"] == "text":
                text_response = block["text"]
                break
        
        return text_response, has_compaction, model_response.get("usage", {})
    
    # Simulate a multi-turn conversation
    print("\n🔹 Starting multi-turn conversation with compaction enabled...")
    
    prompts = [
        "Design the database schema for an e-commerce platform with users, products, orders, and reviews.",
        "Now add the authentication and authorization system with role-based access control.",
        "Add a recommendation engine that suggests products based on user behavior."
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n   Turn {i}: {prompt}")
        response, compacted, usage = chat(prompt)
        print(f"   Response: {response}")
        print(f"   Compaction triggered: {compacted}")
        print(f"   Usage: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out")
    
    print("\n✅ Compaction demo completed!")
    print("💡 In real usage, compaction triggers when input_tokens exceeds threshold")


def demo_custom_summarization():
    """
    Demonstrate compaction with custom summarization instructions.
    
    Custom instructions completely replace the default summarization prompt.
    Use this for specialized workflows that need specific context preserved.
    """
    print("\n" + "=" * 60)
    print("📝 DEMO 3: Compaction with Custom Summarization")
    print("=" * 60)
    
    print("\n💡 Custom instructions replace the default summarization prompt")
    print("💡 Useful for: coding assistants, customer support, research, etc.")
    
    # Example: Coding assistant with custom summarization
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "anthropic_beta": ["compact-2026-01-12"],
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Help me build a REST API with FastAPI for a todo application."
            }
        ],
        "context_management": {
            "edits": [{
                "type": "compact_20260112",
                "trigger": {
                    "type": "input_tokens",
                    "value": 50000
                },
                "instructions": """Create a technical summary that preserves:
1. All code snippets with file paths
2. Technical decisions and reasoning
3. Outstanding tasks and bugs
4. Variable names and API contracts
5. Environment details and dependencies"""
            }]
        }
    }
    
    print("\n🔹 Custom summarization for coding assistant:")
    print("   - Preserves code snippets with file paths")
    print("   - Keeps technical decisions and reasoning")
    print("   - Tracks outstanding tasks and bugs")
    print("   - Maintains variable names and API contracts")
    
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    model_response = json.loads(response["body"].read())
    
    for block in model_response["content"]:
        if block["type"] == "text":
            print(f"\n   Response: {block['text']}")
            break
    
    # Other use case examples
    print("\n🔹 Other custom summarization use cases:")
    
    use_cases = {
        "Customer Support": "Preserve: Customer details, issue history, resolution attempts, sentiment indicators",
        "Research Assistant": "Preserve: Sources cited, hypotheses explored, conclusions reached, open questions",
        "Data Analysis": "Preserve: Datasets referenced, transformations applied, insights discovered, pending analyses"
    }
    
    for use_case, instructions in use_cases.items():
        print(f"   • {use_case}: {instructions}")
    
    print("\n✅ Custom summarization demo completed!")


def demo_pause_after_compaction():
    """
    Demonstrate pause_after_compaction for advanced workflows.
    
    When enabled, the API returns with stop_reason: "compaction" after
    generating the summary, allowing you to inspect or modify before continuing.
    """
    print("\n" + "=" * 60)
    print("⏸️  DEMO 4: Pause After Compaction")
    print("=" * 60)
    
    print("\n💡 pause_after_compaction returns control after summarization")
    print("💡 Useful for: injecting context, preserving specific messages")
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "anthropic_beta": ["compact-2026-01-12"],
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Let's design a microservices architecture."
            }
        ],
        "context_management": {
            "edits": [{
                "type": "compact_20260112",
                "trigger": {
                    "type": "input_tokens",
                    "value": 50000
                },
                "pause_after_compaction": True
            }]
        }
    }
    
    print("\n🔹 Request configured with pause_after_compaction: True")
    
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    model_response = json.loads(response["body"].read())
    stop_reason = model_response.get("stop_reason", "")
    
    print(f"   Stop reason: {stop_reason}")
    
    # In real usage, when compaction triggers:
    print("\n🔹 When compaction triggers with pause enabled:")
    print("   1. API returns with stop_reason: 'compaction'")
    print("   2. You can inspect the compaction summary")
    print("   3. Inject additional context if needed:")
    print('      messages.append({"role": "user", "content": "[Remember: user prefers async patterns]"})')
    print("   4. Continue the request")
    
    for block in model_response["content"]:
        if block["type"] == "text":
            print(f"\n   Response: {block['text']}")
            break
    
    print("\n✅ Pause after compaction demo completed!")


def demo_billing_with_compaction():
    """
    Demonstrate proper billing tracking with compaction.
    
    When compaction triggers, the usage.iterations array contains
    the full breakdown including compaction costs.
    """
    print("\n" + "=" * 60)
    print("💰 DEMO 5: Billing Tracking with Compaction")
    print("=" * 60)
    
    print("\n⚠️  Important billing note:")
    print("   Top-level usage fields DON'T include compaction iteration costs!")
    print("   Sum across usage.iterations for accurate billing totals.")
    
    print("\n🔹 Example response structure with compaction:")
    example_usage = {
        "usage": {
            "input_tokens": 45000,
            "output_tokens": 1234,
            "iterations": [
                {
                    "type": "compaction",
                    "input_tokens": 180000,
                    "output_tokens": 3500
                },
                {
                    "type": "message",
                    "input_tokens": 23000,
                    "output_tokens": 1000
                }
            ]
        }
    }
    
    print(f"   {json.dumps(example_usage, indent=4)}")
    
    print("\n🔹 Correct billing calculation:")
    print("   Top-level input_tokens (45,000) EXCLUDES compaction (180,000)")
    print("   Total actual input: 180,000 + 23,000 = 203,000 tokens")
    
    print("\n🔹 Code to calculate accurate totals:")
    print("""
    def calculate_total_usage(response):
        usage = response.get("usage", {})
        iterations = usage.get("iterations", [])
        
        if iterations:
            # Sum across all iterations for accurate totals
            total_input = sum(i.get("input_tokens", 0) for i in iterations)
            total_output = sum(i.get("output_tokens", 0) for i in iterations)
        else:
            # No compaction, top-level fields are accurate
            total_input = usage.get("input_tokens", 0)
            total_output = usage.get("output_tokens", 0)
        
        return total_input, total_output
    """)
    
    print("\n✅ Billing tracking demo completed!")


def main():
    """Run all demos."""
    print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.6 Advanced Features")
    print("🚀 Model: Claude Opus 4.6 (Global CRIS)")
    print("📍 Source Region: ap-south-1 (India)")
    
    try:
        demo_adaptive_thinking()
        demo_compaction()
        demo_custom_summarization()
        demo_pause_after_compaction()
        demo_billing_with_compaction()
        
        print("\n" + "=" * 60)
        print("🎉 All demos completed successfully!")
        print("=" * 60)
        print("\n📚 Key takeaways:")
        print("   • Use adaptive thinking with effort levels instead of budget_tokens")
        print("   • Compaction requires beta header: anthropic_beta: ['compact-2026-01-12']")
        print("   • Compaction only works with InvokeModel during beta")
        print("   • Custom summarization replaces (not supplements) default prompt")
        print("   • Sum usage.iterations for accurate billing with compaction")
        
    except ClientError as e:
        print(f"\n❌ AWS Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
