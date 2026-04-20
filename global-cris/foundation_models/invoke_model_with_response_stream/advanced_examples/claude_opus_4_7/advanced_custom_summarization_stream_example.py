#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 4.7 Custom Summarization
(InvokeModelWithResponseStream)

Demonstrates compaction with custom summarization instructions and streaming:
- Custom instructions completely replace the default summarization prompt
- Feeds documents to trigger compaction with custom summary logic
- Useful for coding assistants, customer support, research, data analysis

Compaction is in beta and requires the anthropic_beta header.
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
from common.colors import status_color, turn_header, GREEN, RESET
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


def chat_stream(user_message: str):
    """Send a message with custom summarization compaction and streaming."""
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
                },
                # Custom instructions completely REPLACE the default summarization prompt
                # Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-compaction.html#custom-summarization-instructions
                "instructions": CODING_ASSISTANT_INSTRUCTIONS
            }]
        }
    }

    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    text_content = ""
    has_compaction = False

    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk["type"] == "content_block_start":
            block = chunk.get("content_block", {})
            block_type = block.get("type")
            if block_type == "compaction":
                has_compaction = True
                print(f"   {GREEN}📦 [Compaction block detected — custom summarization applied]{RESET}")

        elif chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                text_content += text
                if len(text_content) <= 500:
                    print(text, end="", flush=True)
                elif len(text_content) - len(text) < 500:
                    print("\n   ... [truncated for readability] ...", flush=True)

    # Append assistant response to maintain conversation
    messages.append({
        "role": "assistant",
        "content": text_content
    })

    return text_content, has_compaction


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 4.7 Custom Summarization (Streaming)")
print("🚀 Model: Claude Opus 4.7 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print(f"📦 Compaction trigger threshold: {COMPACTION_TRIGGER_THRESHOLD:,} input tokens")
print("⚠️  Compaction is in beta — requires anthropic_beta header")

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
        (specs[0][0], f"Review this API specification and identify the top 5 security concerns:\n\n{specs[0][1]}"),
        (specs[1][0], f"Review this API specification and suggest performance optimizations:\n\n{specs[1][1]}"),
        (specs[2][0], f"Review this API specification and identify missing error handling:\n\n{specs[2][1]}"),
    ]

    print(f"\n🔹 Starting coding assistant conversation with custom summarization + streaming...")
    print(f"   Spec size: {len(specs[0][1]):,} characters per service")
    print("-" * 60)

    for i, (service_name, prompt) in enumerate(prompts, 1):
        print(f"\n{turn_header(i, f'Reviewing {service_name} ({len(prompt):,} chars)')}")
        print("-" * 40)
        response, compacted = chat_stream(prompt)
        print(f"\n   📦 Compaction triggered: {status_color(compacted)}")

        if compacted:
            print("   ✨ Custom summarization preserved code snippets and technical decisions")

    print("\n" + "-" * 60)
    print("✅ Custom summarization streaming demo completed!")

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
