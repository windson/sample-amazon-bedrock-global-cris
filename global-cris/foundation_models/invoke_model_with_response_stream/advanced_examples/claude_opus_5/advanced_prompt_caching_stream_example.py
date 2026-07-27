#!/usr/bin/env python3
"""
Amazon Bedrock Global CRIS - Claude Opus 5 Prompt Caching
(InvokeModelWithResponseStream)

Demonstrates prompt caching with streaming for reduced latency and cost:
- First call: cache WRITE (populates cache with system prompt + context)
- Second call: cache HIT (reuses cached content, lower latency and cost)

Prompt caching requirements for Claude Opus 5:
- Minimum 512 tokens per cache checkpoint
- Maximum 4 cache checkpoints per request
- TTL: 5 minutes (standard), 1 hour (extended with anthropic_beta)
- Cacheable fields: system, messages, tools

Note: Claude Opus 5 does not support temperature, top_p, or top_k
sampling parameters. Omit these entirely and use prompting to guide behavior.

Note: Claude Opus 5 does NOT require data retention opt-in
(zero data retention by default).

References:
- Prompt caching: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html
- Claude Opus 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html
- Blog: https://aws.amazon.com/blogs/machine-learning/introducing-claude-opus-5-on-aws-anthropics-most-capable-opus-model/

Author: Navule Pavan Kumar Rao
Date: July 24, 2026

Expected output:
=================
  - Call 1: cache_creation_input_tokens > 0 (cache WRITE)
  - Call 2: cache_read_input_tokens > 0 (cache HIT)
"""

import json
import time
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from common.colors import MAGENTA, BOLD, RESET, GREEN, ORANGE

# Initialize Bedrock client for India region (Mumbai)
bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    config=Config(read_timeout=300)
)

# Global CRIS model ID for Claude Opus 5
MODEL_ID = "global.anthropic.claude-opus-5"

# Large system prompt that benefits from caching (must be >= 512 tokens)
CACHED_SYSTEM_PROMPT = """You are an expert software architect specializing in distributed systems,
microservices, and cloud-native architectures. You have deep expertise in:

1. System Design Patterns:
   - Circuit breaker, bulkhead, saga, event sourcing, CQRS
   - Service mesh architectures (Istio, Linkerd, Envoy)
   - API gateway patterns (rate limiting, authentication, routing)
   - Database per service, shared database, polyglot persistence

2. Cloud Platforms:
   - AWS (ECS, EKS, Lambda, DynamoDB, Aurora, SQS, SNS, EventBridge)
   - Kubernetes orchestration and operator patterns
   - Serverless architectures and cold start optimization
   - Multi-region deployment and disaster recovery

3. Reliability Engineering:
   - SLOs, SLIs, and error budgets
   - Chaos engineering principles (Gremlin, Litmus)
   - Observability (distributed tracing, metrics, structured logging)
   - Incident management and postmortem culture

4. Data Architecture:
   - Event-driven architectures with Kafka, Kinesis
   - Data mesh and domain-driven design
   - Stream processing (Flink, Spark Streaming)
   - Data lake and lakehouse patterns (Delta Lake, Iceberg)

5. Security:
   - Zero trust architecture
   - Service-to-service authentication (mTLS, SPIFFE/SPIRE)
   - Secrets management (Vault, AWS Secrets Manager)
   - Supply chain security (SBOM, container signing)

6. Performance Engineering:
   - Capacity planning and load testing
   - Connection pooling and resource management
   - Caching strategies (write-through, write-behind, cache-aside)
   - CDN optimization and edge computing

When answering questions, provide detailed technical explanations with concrete
examples, trade-offs, and production-ready recommendations. Reference specific
AWS services and open-source tools where applicable. Structure responses with
clear sections and code examples when relevant.

Always consider: scalability, reliability, security, cost optimization,
operational excellence, and developer experience in your recommendations."""


def stream_with_prompt_caching(user_message: str):
    """
    Stream a response from Claude Opus 5 with prompt caching enabled.

    The system prompt is marked with cache_control to enable caching.
    First call creates the cache; subsequent calls read from cache.

    Args:
        user_message: The user's question.

    Returns:
        Tuple of (response_text, usage_dict).
    """
    # Note: temperature, top_p, top_k are NOT supported on Claude Opus 5
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        # System prompt with cache_control marker
        "system": [
            {
                "type": "text",
                "text": CACHED_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_message}]
            }
        ]
    }

    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json"
    )

    text_content = ""
    usage_info = {}

    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                text_content += text
                # Cap visible output to keep terminal readable
                if len(text_content) <= 300:
                    print(text, end="", flush=True)
                elif len(text_content) - len(text) < 300:
                    print("\n   ... [truncated for readability] ...", flush=True)

        elif chunk["type"] == "message_delta":
            # Capture usage from message_delta event
            usage_info = chunk.get("usage", usage_info)

        elif chunk["type"] == "message_start":
            # Capture initial usage info (includes cache metrics)
            message = chunk.get("message", {})
            usage_info = message.get("usage", usage_info)

    return text_content, usage_info


print("🌍 Amazon Bedrock Global CRIS - Claude Opus 5 Prompt Caching (Streaming)")
print("🚀 Model: Claude Opus 5 (Global CRIS)")
print("📍 Source Region: ap-south-1 (India)")
print("⚠️  Note: temperature, top_p, and top_k are not supported")
print("💡 Prompt caching: min 512 tokens per checkpoint, max 4 checkpoints")
print("💡 TTL: 5 min standard, 1 hr extended")

try:
    # =========================================================================
    # Call 1: Cache WRITE — first call populates the cache
    # =========================================================================
    question_1 = "How would you design a circuit breaker pattern for a payment service?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 Call 1: Cache WRITE (first call populates cache){RESET}")
    print("=" * 60)
    print(f"📝 Question: {question_1}")
    print("-" * 50)

    start_time = time.time()
    response_text, usage = stream_with_prompt_caching(question_1)
    elapsed_1 = time.time() - start_time

    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    print(f"\n\n   ⏱️  Latency: {elapsed_1:.2f}s")
    print(f"   🔢 Input tokens: {input_tokens:,}")
    print(f"   🔢 Output tokens: {output_tokens:,}")
    print(f"   📦 Cache creation tokens: {GREEN}{cache_creation:,}{RESET}" if cache_creation > 0
          else f"   📦 Cache creation tokens: {ORANGE}{cache_creation:,}{RESET}")
    print(f"   📦 Cache read tokens: {cache_read:,}")

    # =========================================================================
    # Call 2: Cache HIT — same system prompt reuses cached content
    # =========================================================================
    question_2 = "What are the best practices for implementing saga pattern in microservices?"

    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}🔹 Call 2: Cache HIT (reuses cached system prompt){RESET}")
    print("=" * 60)
    print(f"📝 Question: {question_2}")
    print("-" * 50)

    # Brief pause to ensure cache is available
    time.sleep(1)

    start_time = time.time()
    response_text, usage = stream_with_prompt_caching(question_2)
    elapsed_2 = time.time() - start_time

    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    print(f"\n\n   ⏱️  Latency: {elapsed_2:.2f}s")
    print(f"   🔢 Input tokens: {input_tokens:,}")
    print(f"   🔢 Output tokens: {output_tokens:,}")
    print(f"   📦 Cache creation tokens: {cache_creation:,}")
    print(f"   📦 Cache read tokens: {GREEN}{cache_read:,}{RESET}" if cache_read > 0
          else f"   📦 Cache read tokens: {ORANGE}{cache_read:,}{RESET}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"{MAGENTA}{BOLD}📊 Summary{RESET}")
    print("=" * 60)
    if elapsed_1 > 0 and elapsed_2 > 0:
        speedup = ((elapsed_1 - elapsed_2) / elapsed_1) * 100
        print(f"   ⏱️  Call 1 (cache write): {elapsed_1:.2f}s")
        print(f"   ⏱️  Call 2 (cache hit):   {elapsed_2:.2f}s")
        if speedup > 0:
            print(f"   🚀 Latency improvement:  {speedup:.1f}%")

    print("\n✅ Prompt caching streaming demo completed!")
    print("💡 Cache WRITE: cache_creation_input_tokens > 0")
    print("💡 Cache HIT: cache_read_input_tokens > 0")
    print("💡 Cost savings: cached tokens charged at reduced rate")
    print("📚 Docs: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html")

except ClientError as e:
    print(f"\n❌ AWS Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
