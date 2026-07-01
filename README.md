# Amazon Bedrock Global Cross-Region Inference

Amazon Bedrock Global CRIS examples using Claude, Cohere, Amazon Nova, and TwelveLabs Pegasus models.

> Blog: [Access Anthropic Claude models in India on Amazon Bedrock with Global cross-Region inference](https://aws.amazon.com/blogs/machine-learning/access-anthropic-claude-models-in-india-on-amazon-bedrock-with-global-cross-region-inference/)

## Global Cross-Region Inference

Global cross-Region inference extends cross-Region inference beyond geographic boundaries, enabling the routing of inference requests to supported commercial AWS Regions worldwide, optimizing available resources and enabling higher model throughput.

## Examples

### Foundation Models - Simple Examples

| Model | Model ID | Converse | Converse Stream | Invoke Model | Invoke Model Stream |
|-------|----------|----------|-----------------|--------------|---------------------|
| Claude Haiku | `global.anthropic.claude-haiku` | [converse](global-cris/foundation_models/converse/simple_claude_haiku_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_haiku_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_haiku_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_haiku_invoke_model_stream_example.py) |
| Claude Opus | `global.anthropic.claude-opus` | [converse](global-cris/foundation_models/converse/simple_claude_opus_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_opus_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_opus_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_invoke_model_stream_example.py) |
| Claude Opus 4.6 | `global.anthropic.claude-opus-4-6-v1` | [converse](global-cris/foundation_models/converse/simple_claude_opus_4_6_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_opus_4_6_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_opus_4_6_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_4_6_invoke_model_stream_example.py) |
| Claude Opus 4.7 | `global.anthropic.claude-opus-4-7` | [converse](global-cris/foundation_models/converse/simple_claude_opus_4_7_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_opus_4_7_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_opus_4_7_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_4_7_invoke_model_stream_example.py) |
| Claude Opus 4.8 | `global.anthropic.claude-opus-4-8` | [converse](global-cris/foundation_models/converse/simple_claude_opus_4_8_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_opus_4_8_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_opus_4_8_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_4_8_invoke_model_stream_example.py) |
| Claude Sonnet | `global.anthropic.claude-sonnet` | [converse](global-cris/foundation_models/converse/simple_claude_sonnet_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_sonnet_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_sonnet_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_sonnet_invoke_model_stream_example.py) |
| Claude Sonnet 4.6 | `global.anthropic.claude-sonnet-4-6` | [converse](global-cris/foundation_models/converse/simple_claude_sonnet_4_6_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_sonnet_4_6_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_sonnet_4_6_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_sonnet_4_6_invoke_model_stream_example.py) |
| Claude Sonnet 5 | `global.anthropic.claude-sonnet-5` | [converse](global-cris/foundation_models/converse/simple_claude_sonnet_5_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_claude_sonnet_5_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_claude_sonnet_5_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_sonnet_5_invoke_model_stream_example.py) |
| Amazon Nova Lite | `global.amazon.nova-lite` | [converse](global-cris/foundation_models/converse/simple_nova_lite_converse_example.py) | [stream](global-cris/foundation_models/converse_stream/simple_nova_lite_converse_stream_example.py) | [invoke](global-cris/foundation_models/invoke_model/simple_nova_lite_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_nova_lite_invoke_model_stream_example.py) |
| TwelveLabs Pegasus | — | — | — | [invoke](global-cris/foundation_models/invoke_model/simple_pegasus_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/simple_pegasus_invoke_model_stream_example.py) |

### Foundation Models - Advanced Examples

Advanced examples demonstrate features like adaptive thinking with effort levels, compaction for long conversations, custom summarization, and pause after compaction. These features require the InvokeModel or InvokeModelWithResponseStream APIs (not Converse).

| Model | Feature | Invoke Model | Invoke Model Stream |
|-------|---------|--------------|---------------------|
| Claude Opus 4.6 | All features (monolithic) | [invoke](global-cris/foundation_models/invoke_model/advanced_claude_opus_4_6_invoke_model_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_claude_opus_4_6_invoke_model_stream_example.py) |
| Claude Opus 4.7 | Adaptive Thinking + Effort | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_7/advanced_adaptive_thinking_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_7/advanced_adaptive_thinking_stream_example.py) |
| Claude Opus 4.7 | Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_7/advanced_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_7/advanced_compaction_stream_example.py) |
| Claude Opus 4.7 | Custom Summarization | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_7/advanced_custom_summarization_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_7/advanced_custom_summarization_stream_example.py) |
| Claude Opus 4.7 | Pause After Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_7/advanced_pause_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_7/advanced_pause_compaction_stream_example.py) |
| Claude Opus 4.8 | Adaptive Thinking + Effort | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_8/advanced_adaptive_thinking_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_8/advanced_adaptive_thinking_stream_example.py) |
| Claude Opus 4.8 | Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_8/advanced_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_8/advanced_compaction_stream_example.py) |
| Claude Opus 4.8 | Custom Summarization | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_8/advanced_custom_summarization_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_8/advanced_custom_summarization_stream_example.py) |
| Claude Opus 4.8 | Pause After Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_opus_4_8/advanced_pause_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_opus_4_8/advanced_pause_compaction_stream_example.py) |
| Claude Sonnet 5 | Adaptive Thinking (always on) | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_sonnet_5/advanced_adaptive_thinking_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_sonnet_5/advanced_adaptive_thinking_stream_example.py) |
| Claude Sonnet 5 | Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_sonnet_5/advanced_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_sonnet_5/advanced_compaction_stream_example.py) |
| Claude Sonnet 5 | Custom Summarization | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_sonnet_5/advanced_custom_summarization_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_sonnet_5/advanced_custom_summarization_stream_example.py) |
| Claude Sonnet 5 | Pause After Compaction | [invoke](global-cris/foundation_models/invoke_model/advanced_examples/claude_sonnet_5/advanced_pause_compaction_example.py) | [stream](global-cris/foundation_models/invoke_model_with_response_stream/advanced_examples/claude_sonnet_5/advanced_pause_compaction_stream_example.py) |

### Embeddings Models

| Model | Model ID | Example |
|-------|----------|---------|
| Cohere Embed | `global.cohere.embed` | [invoke](global-cris/embeddings_models/simple_cohere_embed_example.py) |

### Application Inference Profiles

| Use Case | Example |
|----------|---------|
| Multi-tenant workloads with isolated throughput and cost tracking | [invoke](application-inference-profile/multi_tenant_inference_profile_example.py) |

## Model Notes

| Model | Context | Max Output | Reasoning | Sampling Params | Key Difference |
|-------|---------|------------|-----------|-----------------|----------------|
| Claude Opus 4.6 | 1M | 128K | Adaptive thinking | `temperature`, `top_p`, `top_k` supported | Monolithic advanced example |
| Claude Opus 4.7 | 1M | 128K | Adaptive thinking | **Not supported** | Adds `xhigh` effort level |
| Claude Opus 4.8 | 1M | 128K | Adaptive thinking | **Not supported** | Deepest reasoning, long autonomous tasks |
| Claude Sonnet 4.6 | 1M | 128K | — | `temperature`, `top_p`, `top_k` supported | Balanced speed and intelligence |
| Claude Sonnet 5 | 1M | 128K | **Always ON** (cannot disable) | **Not supported** | Near-Opus intelligence at Sonnet pricing |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e global-cris/foundation_models/   # Shared utilities for advanced examples
```

### Environment Configuration (for Pegasus examples)

The TwelveLabs Pegasus video model examples require S3 bucket configuration:

```bash
cp .env.example .env
# Edit .env with your S3 bucket name and AWS region
```

## Benefits of Global Cross-Region Inference

- **Enhanced throughput during peak demand** -- Automatically routes requests to AWS Regions with available capacity, handling traffic spikes without manual intervention.
- **Cost-efficiency** -- Approximately 10% savings on input and output token pricing compared to geographic cross-Region inference.
- **Streamlined monitoring** -- CloudWatch and CloudTrail record log entries in your source Region, maintaining centralized observability.
- **On-demand quota flexibility** -- Workloads dynamically route across the AWS global infrastructure, accessing a much larger pool of resources.

## References

- [Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html)
- [Increase throughput with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html#cross-region-inference-comparison)
- [Claude Opus 4.8 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html)
- [Claude Sonnet 5 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html)
- [Claude Opus 4.8 on AWS (Blog)](https://aws.amazon.com/blogs/machine-learning/claude-opus-4-8-is-now-available-on-aws/)
- [Claude Sonnet 5 on AWS (Blog)](https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-on-aws-anthropics-most-capable-sonnet-model/)

## Security

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## Responsible AI

Implement safeguards customized to your application requirements and responsible AI policies using [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)

## Disclaimer

The sample code; software libraries; command line tools; proofs of concept; templates; or other related technology (including any of the foregoing that are provided by our personnel) is provided to you as AWS Content under the AWS Customer Agreement, or the relevant written agreement between you and AWS (whichever applies). You are responsible for testing, securing, and optimizing the AWS Content, such as sample code, as appropriate for production grade use based on your specific quality control practices and standards. You should not use this AWS Content in your production accounts, or on production or other critical data. Deploying AWS Content may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
