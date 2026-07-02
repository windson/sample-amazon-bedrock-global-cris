#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Fable 5 Custom Summarization (InvokeModel)

Demonstrates compaction with custom summarization instructions:
- Custom instructions completely replace the default summarization prompt
- Feeds documents to trigger compaction with custom summary logic
- Useful for coding assistants, customer support, research, data analysis

Claude Fable 5 is Anthropic's next-generation model for complex knowledge work
and coding, capable of sustained autonomous operation across multi-day tasks.

Compaction is in beta and requires the anthropic_beta header.
Compaction only works with InvokeModel (not Converse API during beta).
Minimum trigger threshold is 50,000 tokens (default: 150,000).

Note: Claude Fable 5 sampling constraints: temperature must be 1.0 or unset;
top_p must be >= 0.99 or unset; top_k is not supported.

Note: Claude Fable 5 has adaptive thinking ALWAYS ON — it cannot be disabled.

Note: Requires data retention opt-in (provider_data_share) before first invocation.

Note: The model may return stop_reason: 'refusal' for dual-use content (cyber/bio).

References:
- Compaction: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
- Claude Fable 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html
- Blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""



import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from common.colors import status_color, turn_header
from common.context_generator import generate_api_spec

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    config=Config(read_timeout=300)
)

# Global CRIS model ID for Claude Fable 5
MODEL_ID = "global.anthropic.claude-fable-5"

# Compaction trigger threshold in input tokens.
# The minimum allowed value is 50,000 tokens (default is 150,000).
COMPACTION_TRIGGER_THRESHOLD = 50000

# Custom summarization instructions for a coding assistant.
# These completely REPLACE the default summarization prompt.
CODING_ASSISTANT_INSTRUCTIONS = """Create a technical summary that preserves:
1. All code snippets with file paths
2. Technical decisions and reasoning
3. Outstanding tasks and bugs
4. Variable names and API contracts
5. Environment details and dependencies"""

# Conversation history shared across turns
messages = []


def chat(user_message: str):
    """Send a message with custom summarization compaction enabled."""
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Note: temperature must be 1.0 or unset; top_p must be >= 0.99 or unset; top_k is NOT supported
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Compaction beta header — required during beta period
        "anthropic_beta": ["compact-2026-01-12"],
        "max_tokens": 4096,
        "messages": messages,
        # Server-side compaction: auto-summarizes older context when approaching token limit
        "context_management": {
            "edits": [{
                "type": "compact_20260112",  # Beta compaction strategy identifier
                "trigger": {
                    "type": "input_tokens",
                    "value": COMPACTION_TRIGGER_THRESHOLD  # Minimum: 50,000 tokens
                },
                # Custom instructions completely REPLACE the default summarization prompt
                "instructions": CODING_ASSISTANT_INSTRUCTIONS
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


print("🌍 Amazon Bedrock Global CRIS - Claude Fable 5 Custom Summarization")
print("🚀 Model: Claude Fable 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📦 Compaction trigger threshold: {COMPACTION_TRIGGER_THRESHOLD:,} input tokens")
print("⚠️  Compaction is in beta — requires anthropic_beta header")
print("⚠️  Requires data retention opt-in (provider_data_share) before first invocation")
print("💡 Adaptive thinking is ALWAYS ON in Fable 5")

print("\n📝 Custom summarization instructions:")
for line in CODING_ASSISTANT_INSTRUCTIONS.strip().split("\n"):
    print(f"   {line}")

try:
    specs = [
        ("User Management Service", generate_api_spec("User Management Service", num_endpoints=30)),
        ("Payment Processing Service", generate_api_spec("Payment Processing Service", num_endpoints=30)),
        ("Inventory & Fulfillment Service", generate_api_spec("Inventory Fulfillment Service", num_endpoints=30)),
    ]

    prompts = [
        (specs[0][0], f"Review this API specification and analyze the architecture patterns and suggest scalability improvements:\n\n{specs[0][1]}"),
        (specs[1][0], f"Review this API specification and suggest performance optimizations:\n\n{specs[1][1]}"),
        (specs[2][0], f"Review this API specification and identify missing error handling:\n\n{specs[2][1]}"),
    ]

    print(f"\n🔹 Starting coding assistant conversation with custom summarization...")
    print(f"   Spec size: {len(specs[0][1]):,} characters per service")
    print("-" * 60)

    for i, (service_name, prompt) in enumerate(prompts, 1):
        print(f"\n{turn_header(i, f'Reviewing {service_name} ({len(prompt):,} chars)')}")
        response, compacted, usage = chat(prompt)
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        print(f"   Response: {response[:200]}...")
        print(f"   📦 Compaction triggered: {status_color(compacted)}")
        print(f"   🔢 Tokens: {input_tokens:,} in / {output_tokens:,} out")

        if compacted:
            print("   ✨ Custom summarization preserved code snippets and technical decisions")

    print("\n" + "-" * 60)
    print("✅ Custom summarization demo completed!")

    print("\n💡 Other custom summarization use cases:")
    use_cases = {
        "Customer Support": "Preserve: Customer details, issue history, resolution attempts, sentiment indicators",
        "Research Assistant": "Preserve: Sources cited, hypotheses explored, conclusions reached, open questions",
        "Data Analysis": "Preserve: Datasets referenced, transformations applied, insights discovered, pending analyses",
    }
    for use_case, instructions in use_cases.items():
        print(f"   • {use_case}: {instructions}")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
