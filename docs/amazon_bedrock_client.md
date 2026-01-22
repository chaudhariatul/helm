# Amazon Bedrock Client Documentation

## Overview

The AmazonBedrockClient provides comprehensive integration with AWS Bedrock API for Amazon Nova 2 models in the HELM framework. This client is specifically designed for medical AI benchmarking through MedHELM, with enhanced logging, retry logic, and error handling.

## Features

- **AWS Credential Management**: Supports multiple credential sources:
  - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - AWS credential files (~/.aws/credentials)
  - IAM roles (for EC2/ECS deployments)
  - Assumed roles via STS

- **Model ID Mapping**: Automatic translation between HELM model names and Bedrock model IDs:
  - `amazon/nova-lite-v1:0` → `us.amazon.nova-lite-v1:0`
  - `amazon/nova-pro-v1:0` → `us.amazon.nova-pro-v1:0`
  - `amazon/nova-2-lite-v1:0` → `us.amazon.nova-2-lite-v1:0`
  - `amazon/nova-2-pro-v1:0` → `us.amazon.nova-2-pro-v1:0`
  - `amazon/nova-2-sonic-v1:0` → `us.amazon.nova-2-sonic-v1:0`

- **Request Formatting**: Converts HELM requests to Bedrock API format with proper parameter mapping:
  - `temperature` → `inferenceConfig.temperature`
  - `top_p` → `inferenceConfig.topP`
  - `max_tokens` → `inferenceConfig.maxTokens`
  - `stop_sequences` → `inferenceConfig.stopSequences`

- **Response Parsing**: Extracts and formats response data:
  - Generated text
  - Token usage (input tokens, output tokens)
  - Finish reason (end_turn, max_tokens, stop_sequence, content_filtered)
  - Request latency and timing

- **Retry Logic**: Exponential backoff retry mechanism:
  - Maximum retries: 3 (configurable)
  - Base delay: 1 second (configurable)
  - Exponential backoff: delay = base_delay × 2^attempt
  - Total timeout: 120 seconds (configurable)
  - Smart retry: Distinguishes between retriable and non-retriable errors

- **Comprehensive Logging**: Detailed logging for monitoring and debugging:
  - Request parameters and timing
  - Response metadata and token usage
  - Error details and retry attempts
  - Latency measurements

## Setup Guide

### Prerequisites

1. **AWS Account**: You need an AWS account with access to Amazon Bedrock
2. **Model Access**: Enable Amazon Nova models in your AWS Bedrock console
3. **Python Environment**: Python 3.8+ with HELM installed
4. **AWS SDK**: Install boto3 (included in HELM AWS extras)

### Installation

Install HELM with AWS support:

```bash
pip install crfm-helm[aws]
```

Or for development:

```bash
cd helm
pip install -e .[aws]
```

### AWS Credentials Configuration

Choose one of the following methods:

#### Method 1: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"  # Optional, defaults to us-east-1
```

#### Method 2: AWS Credentials File

Create or edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key-id
aws_secret_access_key = your-secret-access-key

[bedrock]
aws_access_key_id = your-bedrock-access-key-id
aws_secret_access_key = your-bedrock-secret-access-key
```

Set the profile to use:

```bash
export AWS_PROFILE="bedrock"
```

#### Method 3: IAM Role (for EC2/ECS)

If running on AWS infrastructure, attach an IAM role with Bedrock permissions.

Required permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*:*:*"
    }
  ]
}
```

#### Method 4: Assumed Role

For cross-account access:

```bash
export BEDROCK_ASSUME_ROLE="arn:aws:iam::123456789012:role/BedrockAccessRole"
```

### Model Access

Enable Nova models in AWS Bedrock:

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access"
3. Request access to:
   - Amazon Nova 2 Lite
   - Amazon Nova 2 Pro
   - Amazon Nova 2 Sonic (optional)
4. Wait for approval (usually instant)

## Usage Examples

### Basic Usage

```python
from helm.common.cache_backend_config import SqliteCacheBackendConfig
from helm.common.request import Request
from helm.clients.amazon_bedrock_client import AmazonBedrockClient
from helm.tokenizers.auto_tokenizer import AutoTokenizer

# Initialize tokenizer
tokenizer = AutoTokenizer(credentials={}, cache_backend_config=SqliteCacheBackendConfig())
tokenizer_instance = tokenizer._get_tokenizer("huggingface/gpt2")

# Initialize cache
cache_config = SqliteCacheBackendConfig().get_cache_config("bedrock")

# Create client
client = AmazonBedrockClient(
    cache_config=cache_config,
    tokenizer=tokenizer_instance,
    tokenizer_name="huggingface/gpt2",
)

# Make a request
request = Request(
    model="amazon/nova-2-lite-v1:0",
    prompt="What is the capital of France?",
    temperature=0.0,
    max_tokens=50,
    top_p=1.0,
)

result = client.make_request(request)
print(result.completions[0].text)
```

### Medical Question Answering

```python
# Medical knowledge question
request = Request(
    model="amazon/nova-2-pro-v1:0",
    prompt="""Question: What is the primary function of hemoglobin in red blood cells?
A) Transport oxygen
B) Fight infections
C) Clot blood
D) Produce antibodies

Answer: """,
    temperature=0.0,
    max_tokens=100,
)

result = client.make_request(request)
print(f"Answer: {result.completions[0].text}")
```

### Clinical Note Generation

```python
# Generate clinical impression
request = Request(
    model="amazon/nova-2-pro-v1:0",
    prompt="""Patient Information:
- Age: 45, Male
- Chief Complaint: Chest pain for 2 hours
- Vitals: BP 150/95, HR 98, Temp 37.2°C
- History: Smoker, family history of heart disease

Generate a clinical impression:""",
    temperature=0.3,
    max_tokens=300,
)

result = client.make_request(request)
print(f"Clinical Impression:\n{result.completions[0].text}")
```

### Using Messages Format

```python
# Multi-turn conversation
request = Request(
    model="amazon/nova-2-lite-v1:0",
    messages=[
        {"role": "user", "content": "I have a headache and fever."},
        {"role": "assistant", "content": "I understand. Can you tell me more about your symptoms?"},
        {"role": "user", "content": "The headache is severe and I've had a fever of 38.5°C for 2 days."},
    ],
    temperature=0.5,
    max_tokens=200,
)

result = client.make_request(request)
print(f"Response: {result.completions[0].text}")
```

### Advanced Configuration

```python
# Custom retry and timeout settings
client = AmazonBedrockClient(
    cache_config=cache_config,
    tokenizer=tokenizer_instance,
    tokenizer_name="huggingface/gpt2",
    region="us-west-2",
    max_retries=5,          # More retries
    base_delay=2.0,         # Longer base delay
    timeout=300,            # 5-minute timeout
)

# With stop sequences
request = Request(
    model="amazon/nova-2-lite-v1:0",
    prompt="List three symptoms of diabetes:",
    temperature=0.7,
    max_tokens=200,
    stop_sequences=["\n\n", "Question:"],
)

result = client.make_request(request)
```

## Running MedHELM Benchmarks

### Single Benchmark

```bash
helm-run \
  --run-entries medcalc_bench:model=amazon/nova-2-pro-v1:0,model_deployment=amazon/nova-2-pro-v1:0 \
  --suite medhelm \
  --max-eval-instances 100
```

### All Nova 2 MedHELM Benchmarks

```bash
helm-run \
  --conf-paths src/helm/benchmark/presentation/run_entries_nova2_medhelm.conf \
  --suite medhelm \
  --max-eval-instances 100
```

### Specific Categories

```bash
# Clinical Decision Support only
helm-run \
  --run-entries medcalc_bench:model=amazon/nova-2-pro-v1:0 \
  --run-entries head_qa:model=amazon/nova-2-pro-v1:0 \
  --run-entries medbullets:model=amazon/nova-2-pro-v1:0 \
  --suite medhelm
```

## Model Capabilities

### Amazon Nova 2 Lite

- **Context Window**: 1,000,000 tokens
- **Best For**: 
  - Fast, cost-effective reasoning
  - Everyday medical workloads
  - Patient communication
  - Simple clinical note generation
- **Strengths**:
  - Low latency
  - Cost-effective
  - Good for high-volume applications
- **Limitations**:
  - Less complex reasoning than Pro
  - May struggle with complex multi-step problems

### Amazon Nova 2 Pro

- **Context Window**: 1,000,000 tokens
- **Best For**:
  - Complex agentic tasks
  - Multi-document analysis
  - Advanced clinical decision support
  - Complex medical research tasks
- **Strengths**:
  - Extended thinking capabilities
  - Better reasoning for complex problems
  - More accurate for specialized medical tasks
- **Limitations**:
  - Higher cost than Lite
  - Slightly higher latency

### Amazon Nova 2 Sonic

- **Context Window**: 300,000 tokens
- **Best For**:
  - Ultra-low latency applications
  - Real-time interactions
  - Simple queries
- **Strengths**:
  - Fastest response times
  - Good for conversational interfaces
- **Limitations**:
  - Shorter context window
  - Less suitable for complex reasoning

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `Failed to initialize Bedrock client: Unable to locate credentials`

**Solution**: Ensure AWS credentials are properly configured (see Setup Guide).

#### 2. Model Access Denied

**Error**: `AccessDeniedException: You don't have access to the model with the specified model ID`

**Solution**: Enable the model in AWS Bedrock Console under "Model access".

#### 3. Rate Limiting

**Error**: `ThrottlingException: Rate exceeded`

**Solution**: The client will automatically retry with exponential backoff. If the issue persists, request a quota increase in AWS Service Quotas.

#### 4. Region Issues

**Error**: `Could not connect to the endpoint URL`

**Solution**: Ensure the specified region has Bedrock available and the model is enabled:

```python
client = AmazonBedrockClient(
    cache_config=cache_config,
    tokenizer=tokenizer,
    tokenizer_name="huggingface/gpt2",
    region="us-east-1",  # or "us-west-2"
)
```

#### 5. Timeout Errors

**Error**: `Request timeout after X seconds`

**Solution**: Increase timeout for complex requests:

```python
client = AmazonBedrockClient(
    cache_config=cache_config,
    tokenizer=tokenizer,
    tokenizer_name="huggingface/gpt2",
    timeout=300,  # 5 minutes
)
```

### Debug Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- Request parameters
- Response metadata
- Retry attempts
- Token usage
- Latency measurements

## Testing

### Unit Tests

Run unit tests:

```bash
pytest src/helm/clients/test_amazon_bedrock_client.py -v
```

### Integration Tests

Run integration tests (requires AWS credentials):

```bash
# Set environment variable to enable integration tests
export SKIP_INTEGRATION_TESTS=0

# Run integration tests
pytest src/helm/clients/test_amazon_bedrock_client_integration.py -v -s
```

**Note**: Integration tests make real API calls and may incur costs.

## Performance Optimization

### 1. Caching

The client automatically caches responses. Use persistent cache for production:

```python
from helm.common.cache_backend_config import SqliteCacheBackendConfig

cache_config = SqliteCacheBackendConfig(
    cache_path="path/to/cache.db"
).get_cache_config("bedrock")
```

### 2. Batch Processing

For multiple requests, use concurrent execution:

```python
from concurrent.futures import ThreadPoolExecutor

def process_request(prompt):
    request = Request(model="amazon/nova-2-lite-v1:0", prompt=prompt, max_tokens=100)
    return client.make_request(request)

prompts = ["Question 1", "Question 2", "Question 3"]
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_request, prompts))
```

### 3. Model Selection

- Use **Nova 2 Lite** for high-volume, cost-sensitive applications
- Use **Nova 2 Pro** for complex reasoning tasks
- Use **Nova 2 Sonic** for real-time, latency-sensitive applications

### 4. Parameter Tuning

- **Temperature**: Lower (0.0-0.3) for consistent, factual responses; Higher (0.7-1.0) for creative tasks
- **Max Tokens**: Set as low as possible to reduce cost and latency
- **Top P**: Use 1.0 for maximum diversity, lower values (0.8-0.95) for more focused responses

## Cost Estimation

Approximate costs (as of January 2026):

- **Nova 2 Lite**: $0.06 per 1M input tokens, $0.24 per 1M output tokens
- **Nova 2 Pro**: $0.80 per 1M input tokens, $3.20 per 1M output tokens
- **Nova 2 Sonic**: $0.02 per 1M input tokens, $0.08 per 1M output tokens

Example calculation for MedHELM benchmark:
```
10,000 questions × 500 tokens avg (prompt + response) = 5M tokens
Nova 2 Lite: ~$0.30 - $1.20
Nova 2 Pro: ~$4.00 - $16.00
```

## Best Practices

1. **Always use caching** to avoid duplicate API calls
2. **Set appropriate max_tokens** to control costs
3. **Use temperature=0.0** for reproducible results in benchmarking
4. **Monitor token usage** in production deployments
5. **Handle errors gracefully** with proper error checking
6. **Use appropriate model** for the task complexity
7. **Enable logging** for debugging and monitoring
8. **Test with small batches** before running full benchmarks

## Support

For issues and questions:

- **HELM Issues**: https://github.com/stanford-crfm/helm/issues
- **AWS Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **AWS Support**: AWS Console → Support Center

## References

- [Amazon Nova Models Blog Post](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-2/)
- [AWS Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [MedHELM Documentation](https://crfm.stanford.edu/helm/medhelm/)
- [HELM Documentation](https://crfm.stanford.edu/helm/)
