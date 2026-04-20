#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 4.7 Compaction (InvokeModel)

Demonstrates compaction for long-running conversations:
- Feeds documents to accumulate context
- Compaction triggers when input tokens exceed the configured threshold
- Shows billing breakdown with usage.iterations

Compaction is in beta and requires the anthropic_beta header.
Compaction only works with InvokeModel (not Converse API during beta).
Minimum trigger threshold is 50,000 tokens (default: 150,000).

Note: Claude Opus 4.7 no longer supports temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

References:
- Compaction: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
- Claude Opus 4.7 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html
- Blog: https://aws.amazon.com/blogs/aws/introducing-anthropics-claude-opus-4-7-model-in-amazon-bedrock/

Author: Navule Pavan Kumar Rao
Date: April 20, 2026
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

# Global CRIS model ID for Claude Opus 4.7
MODEL_ID = "global.anthropic.claude-opus-4-7"

# Compaction trigger threshold in input tokens.
# The minimum allowed value is 50,000 tokens (default is 150,000).
COMPACTION_TRIGGER_THRESHOLD = 50000

# Conversation history shared across turns
messages = []


def chat(user_message: str):
    """Send a message with compaction enabled and return the response."""
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 4.7
    # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html#sampling-parameters-no-longer-supported
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        # Compaction beta header — required during beta period
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
        "anthropic_beta": ["compact-2026-01-12"],
        "max_tokens": 4096,
        "messages": messages,
        # Server-side compaction: auto-summarizes older context when approaching token limit
        # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html
        "context_management": {
            "edits": [{
                "type": "compact_20260112",  # Beta compaction strategy identifier
                "trigger": {
                    "type": "input_tokens",
                    "value": COMPACTION_TRIGGER_THRESHOLD  # Minimum: 50,000 tokens
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


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.7 Compaction")
print("🚀 Model: Claude Opus 4.7 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📦 Compaction trigger threshold: {COMPACTION_TRIGGER_THRESHOLD:,} input tokens")
print("⚠️  Compaction is in beta — requires anthropic_beta header")

try:
    specs = [
        ("User Management Service", generate_api_spec("User Management Service", num_endpoints=30)),
        ("Payment Processing Service", generate_api_spec("Payment Processing Service", num_endpoints=30)),
        ("Inventory & Fulfillment Service", generate_api_spec("Inventory Fulfillment Service", num_endpoints=30)),
    ]

    prompts = [
        (specs[0][0], f"Review this API specification and identify the top 5 security concerns:\n\n{specs[0][1]}"),
        (specs[1][0], f"Review this API specification and suggest performance optimizations:\n\n{specs[1][1]}"),
        (specs[2][0], f"Review this API specification and identify missing error handling:\n\n{specs[2][1]}"),
    ]

    print(f"\n🔹 Starting multi-turn conversation...")
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

        # Show billing breakdown when iterations are present
        iterations = usage.get("iterations", [])
        if iterations:
            print("   💰 Billing breakdown (usage.iterations):")
            for iteration in iterations:
                iter_type = iteration.get("type", "unknown")
                iter_in = iteration.get("input_tokens", 0)
                iter_out = iteration.get("output_tokens", 0)
                print(f"      • {iter_type}: {iter_in:,} in / {iter_out:,} out")
            total_in = sum(it.get("input_tokens", 0) for it in iterations)
            total_out = sum(it.get("output_tokens", 0) for it in iterations)
            print(f"      Total billed: {total_in:,} in / {total_out:,} out")

    print("\n" + "-" * 60)
    print("✅ Compaction demo completed!")
    print("\n💡 Billing note:")
    print("   Top-level usage fields DON'T include compaction iteration costs.")
    print("   Always sum across usage.iterations for accurate billing totals.")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
