# Amazon Bedrock Global cross-Region inference

Amazon Bedrock Global CRIS examples using Claude, Cohere, Amazon Nova, and TwelveLabs Pegasus models.

> Blog: [Access Anthropic Claude models in India on Amazon Bedrock with Global cross-Region inference](https://aws.amazon.com/blogs/machine-learning/access-anthropic-claude-models-in-india-on-amazon-bedrock-with-global-cross-region-inference/)

## Global cross-Region inference

Global cross-Region inference extends cross-Region inference beyond geographic boundaries, enabling the routing of inference requests to supported commercial AWS Regions worldwide, optimizing available resources and enabling higher model throughput.

## Project Structure

```text
.
├── application-inference-profile
│   └── multi_tenant_inference_profile_example.py
├── global-cris
│   ├── embeddings_models
│   │   └── simple_cohere_embed_example.py
│   └── foundation_models
│       ├── converse
│       │   ├── simple_claude_haiku_converse_example.py
│       │   ├── simple_claude_opus_converse_example.py
│       │   ├── simple_claude_opus_4_6_converse_example.py
│       │   ├── simple_claude_sonnet_converse_example.py
│       │   ├── simple_claude_sonnet_4_6_converse_example.py
│       │   └── simple_nova_lite_converse_example.py
│       ├── converse_stream
│       │   ├── simple_claude_haiku_converse_stream_example.py
│       │   ├── simple_claude_opus_converse_stream_example.py
│       │   ├── simple_claude_opus_4_6_converse_stream_example.py
│       │   ├── simple_claude_sonnet_converse_stream_example.py
│       │   ├── simple_claude_sonnet_4_6_converse_stream_example.py
│       │   └── simple_nova_lite_converse_stream_example.py
│       ├── invoke_model
│       │   ├── simple_claude_haiku_invoke_model_example.py
│       │   ├── simple_claude_opus_invoke_model_example.py
│       │   ├── simple_claude_opus_4_6_invoke_model_example.py
│       │   ├── advanced_claude_opus_4_6_invoke_model_example.py
│       │   ├── simple_claude_sonnet_invoke_model_example.py
│       │   ├── simple_claude_sonnet_4_6_invoke_model_example.py
│       │   ├── simple_nova_lite_invoke_model_example.py
│       │   └── simple_pegasus_invoke_model_example.py
│       ├── invoke_model_with_response_stream
│       │   ├── simple_claude_haiku_invoke_model_stream_example.py
│       │   ├── simple_claude_opus_invoke_model_stream_example.py
│       │   ├── simple_claude_opus_4_6_invoke_model_stream_example.py
│       │   ├── advanced_claude_opus_4_6_invoke_model_stream_example.py
│       │   ├── simple_claude_sonnet_invoke_model_stream_example.py
│       │   ├── simple_claude_sonnet_4_6_invoke_model_stream_example.py
│       │   ├── simple_nova_lite_invoke_model_stream_example.py
│       │   └── simple_pegasus_invoke_model_stream_example.py
│       └── utils.py
├── .env.example
└── requirements.txt
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration (for Pegasus examples)

The TwelveLabs Pegasus video model examples require S3 bucket configuration:

```bash
cp .env.example .env
# Edit .env with your S3 bucket name and AWS region
```

## Run Examples

### Global Cross-Region Inference (System-Defined Profiles)

Global endpoints route requests worldwide for optimal throughput and resilience.

#### Converse API

```bash
python global-cris/foundation_models/converse/simple_claude_haiku_converse_example.py
python global-cris/foundation_models/converse/simple_claude_opus_converse_example.py
python global-cris/foundation_models/converse/simple_claude_opus_4_6_converse_example.py
python global-cris/foundation_models/converse/simple_claude_sonnet_converse_example.py
python global-cris/foundation_models/converse/simple_claude_sonnet_4_6_converse_example.py
python global-cris/foundation_models/converse/simple_nova_lite_converse_example.py
```

#### Converse Stream API

```bash
python global-cris/foundation_models/converse_stream/simple_claude_haiku_converse_stream_example.py
python global-cris/foundation_models/converse_stream/simple_claude_opus_converse_stream_example.py
python global-cris/foundation_models/converse_stream/simple_claude_opus_4_6_converse_stream_example.py
python global-cris/foundation_models/converse_stream/simple_claude_sonnet_converse_stream_example.py
python global-cris/foundation_models/converse_stream/simple_claude_sonnet_4_6_converse_stream_example.py
python global-cris/foundation_models/converse_stream/simple_nova_lite_converse_stream_example.py
```

#### Invoke Model API

```bash
python global-cris/foundation_models/invoke_model/simple_claude_haiku_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_claude_opus_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_claude_opus_4_6_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_claude_sonnet_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_claude_sonnet_4_6_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_nova_lite_invoke_model_example.py
python global-cris/foundation_models/invoke_model/simple_pegasus_invoke_model_example.py
```

#### Invoke Model with Response Stream API

```bash
python global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_haiku_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_opus_4_6_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_sonnet_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_claude_sonnet_4_6_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_nova_lite_invoke_model_stream_example.py
python global-cris/foundation_models/invoke_model_with_response_stream/simple_pegasus_invoke_model_stream_example.py
```

#### Claude Opus 4.6 Advanced Features

These examples demonstrate Opus 4.6 exclusive features: adaptive thinking with effort levels, compaction for long conversations, custom summarization, and pause after compaction.

```bash
# InvokeModel with adaptive thinking, compaction, custom summarization
python global-cris/foundation_models/invoke_model/advanced_claude_opus_4_6_invoke_model_example.py

# Streaming with adaptive thinking visualization and compaction
python global-cris/foundation_models/invoke_model_with_response_stream/advanced_claude_opus_4_6_invoke_model_stream_example.py
```

#### Embeddings

```bash
python global-cris/embeddings_models/simple_cohere_embed_example.py
```

### Application Inference Profiles

Application inference profiles enable multi-tenant workloads with isolated throughput and cost tracking per tenant.

```bash
python application-inference-profile/multi_tenant_inference_profile_example.py
```

## Benefits of global cross-Region inference

Global cross-Region inference for Anthropic's Claude Sonnet 4.5 delivers multiple advantages over traditional geographic cross-Region inference profiles:

- **Enhanced throughput during peak demand** – Global cross-Region inference provides improved resilience during periods of peak demand by automatically routing requests to AWS Regions with available capacity. This dynamic routing happens seamlessly without additional configuration or intervention from developers. Unlike traditional approaches that might require complex client-side load balancing between AWS Regions, global cross-Region inference handles traffic spikes automatically. This is particularly important for business-critical applications where downtime or degraded performance can have significant financial or reputational impacts.
- **Cost-efficiency** – Global cross-Region inference for Anthropic's Claude Sonnet 4.5 offers approximately 10% savings on both input and output token pricing compared to geographic cross-Region inference. The price is calculated based on the AWS Region from which the request is made (source AWS Region). This means organizations can benefit from improved resilience with even lower costs. This pricing model makes global cross-Region inference a cost-effective solution for organizations looking to optimize their generative AI deployments. By improving resource utilization and enabling higher throughput without additional costs, it helps organizations maximize the value of their investment in Amazon Bedrock.
- **Streamlined monitoring** – When using global cross-Region inference, CloudWatch and CloudTrail continue to record log entries in your source AWS Region, simplifying observability and management. Even though your requests are processed across different AWS Regions worldwide, you maintain a centralized view of your application's performance and usage patterns through your familiar AWS monitoring tools.
- **On-demand quota flexibility** – With global cross-Region inference, your workloads are no longer limited by individual Regional capacity. Instead of being restricted to the capacity available in a specific AWS Region, your requests can be dynamically routed across the AWS global infrastructure. This provides access to a much larger pool of resources, making it less complicated to handle high-volume workloads and sudden traffic spikes.

## References

- [Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html)
- [Increase throughput with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html#cross-region-inference-comparison)
- [Amazon Bedrock now supports Global Cross-Region inference for Anthropic Claude Sonnet 4](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-bedrock-global-cross-region-inference-anthropic-claude-sonnet-4/)

## Security

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## Responsible AI

Implement safeguards customized to your application requirements and responsible AI policies using [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)

## Disclaimer

The sample code; software libraries; command line tools; proofs of concept; templates; or other related technology (including any of the foregoing that are provided by our personnel) is provided to you as AWS Content under the AWS Customer Agreement, or the relevant written agreement between you and AWS (whichever applies).  You are responsible for testing, securing, and optimizing the AWS Content, such as sample code, as appropriate for production grade use based on your specific quality control practices and standards.  You should not use this AWS Content in your production accounts, or on production or other critical data. Deploying AWS Content may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
