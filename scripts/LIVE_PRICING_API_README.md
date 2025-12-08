# Live Pricing API Cost Calculator

## Overview

The Live Pricing API Cost Calculator is a tool that calculates model invocation costs using **live pricing data** fetched from AWS Pricing APIs and other pricing sources, instead of relying on static JSON files. This ensures you always have the most current pricing information for your cost estimates.

## Features

✅ **Live Pricing Data**: Fetches current pricing from AWS Bedrock Pricing API  
✅ **Intelligent Caching**: Reduces API calls by caching pricing for 60 minutes (configurable)  
✅ **Graceful Fallback**: Can fallback to static pricing if live pricing is unavailable  
✅ **Error Handling**: Provides informative error messages when pricing data is unavailable  
✅ **Comparison Mode**: Compare live pricing with static pricing data  
✅ **All Models Supported**: Works with all Bedrock models and can be extended for other providers  

## Quick Start

### Basic Usage

Calculate the cost for a model invocation:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000
```

Output:
```
Cost: $0.0240
(using aws_pricing_api)
```

### Detailed Breakdown

Show detailed cost breakdown with pricing information:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --verbose
```

### Show Model Pricing

Display detailed pricing information for a specific model:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --show-pricing
```

### Compare with Static Pricing

Compare live pricing with static pricing data:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --compare
```

### Force Refresh Pricing

Bypass cache and fetch fresh pricing data:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --no-cache
```

### Fallback to Static Pricing

Use static pricing as fallback if live pricing fails:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --fallback
```

### Show Supported Providers

See which providers support live pricing APIs:

```bash
python scripts/calculate_model_cost_live.py --show-providers
```

## Installation & Prerequisites

### Required Dependencies

The tool requires `boto3` for AWS API access:

```bash
pip install boto3
```

This is already included in the project dependencies (`pyproject.toml`).

### AWS Credentials Configuration

For Bedrock models, you need AWS credentials configured. Choose one method:

#### Method 1: AWS CLI Configuration (Recommended)

```bash
aws configure
```

Provide your AWS Access Key ID, Secret Access Key, and default region.

#### Method 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Method 3: IAM Role (for EC2/ECS)

If running on AWS infrastructure, use IAM roles for automatic credential management.

### Required AWS Permissions

The AWS credentials need the following IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "pricing:GetProducts",
        "pricing:DescribeServices"
      ],
      "Resource": "*"
    }
  ]
}
```

## Supported Models

### AWS Bedrock Models (Live Pricing Available)

All AWS Bedrock models support live pricing via AWS Pricing API:

**Amazon Nova Models:**
- `amazon/nova-premier-v1:0`
- `amazon/nova-pro-v1:0`
- `amazon/nova-lite-v1:0`
- `amazon/nova-micro-v1:0`
- `amazon/nova-2-pro-v1:0`
- `amazon/nova-2-lite-v1:0`
- `amazon/nova-2-sonic-v1:0`

**Amazon Titan Models:**
- `amazon/titan-text-lite-v1`
- `amazon/titan-text-express-v1`

**Third-Party Models on Bedrock:**
- `anthropic/*` (Claude models on Bedrock)
- `meta/*` (Llama models on Bedrock)
- `mistralai/*` (Mistral models on Bedrock)
- `cohere/*` (Cohere models on Bedrock)
- `ai21/*` (AI21 models on Bedrock)

### Other Models (Static Pricing Fallback)

For models without public pricing APIs, the tool can fallback to static pricing:

- OpenAI models (`openai/*`)
- Anthropic models (direct API, not Bedrock)
- Google models (`google/*`)

Use the `--fallback` flag to enable automatic fallback to static pricing.

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--model` | `-m` | Model name (e.g., amazon/nova-pro-v1:0) |
| `--input-tokens` | `-i` | Number of input tokens |
| `--output-tokens` | `-o` | Number of output tokens |
| `--no-cache` | | Bypass cache and fetch fresh pricing |
| `--cache-ttl` | | Cache time-to-live in minutes (default: 60) |
| `--verbose` | `-v` | Show detailed cost breakdown |
| `--compare` | `-c` | Compare live pricing with static pricing |
| `--fallback` | `-f` | Use static pricing as fallback if live pricing fails |
| `--show-providers` | | Show supported pricing providers |
| `--show-pricing` | `-p` | Show detailed pricing for the specified model |

## Python API Usage

You can also use the live pricing functionality in your Python code:

```python
import sys
sys.path.insert(0, 'src')

from helm.benchmark.model_pricing_api import LivePricingClient, format_cost

# Initialize client
client = LivePricingClient()

# Fetch live pricing
pricing = client.get_live_pricing("amazon/nova-pro-v1:0")

if pricing:
    # Calculate cost
    cost = pricing.calculate_cost(input_tokens=10000, output_tokens=5000)
    print(f"Cost: {format_cost(cost)}")
    print(f"Source: {pricing.source}")
    print(f"Input rate: ${pricing.input_price_per_million}/1M tokens")
else:
    print("Live pricing not available")
```

### Advanced Python Usage

```python
from helm.benchmark.model_pricing_api import (
    LivePricingClient,
    PricingAPIError,
    calculate_cost_live,
)

# Initialize with custom cache TTL
client = LivePricingClient(cache_ttl_minutes=120)

try:
    # Fetch pricing without cache
    pricing = client.get_live_pricing("amazon/nova-lite-v1:0", use_cache=False)
    
    if pricing:
        print(f"Input: ${pricing.input_price_per_million}/1M")
        print(f"Output: ${pricing.output_price_per_million}/1M")
        print(f"Fetched at: {pricing.fetched_at}")
        
        # Calculate cost
        cost = pricing.calculate_cost(5000, 2000)
        print(f"Total cost: ${cost:.6f}")
        
except PricingAPIError as e:
    print(f"API Error: {e}")
    # Handle error or fallback to static pricing
```

### Clear Cache

```python
client = LivePricingClient()

# Clear cache for specific model
client.clear_cache("amazon/nova-pro-v1:0")

# Clear all cache
client.clear_cache()
```

## Error Handling

The tool provides clear, informative error messages for various failure scenarios:

### 1. Pricing API Unavailable

**Error:**
```
WARNING: Live pricing not available for 'openai/gpt-4o'
```

**Reason:** The model's provider doesn't offer a public pricing API.

**Solution:** Use the `--fallback` flag to use static pricing.

### 2. AWS Credentials Not Configured

**Error:**
```
ERROR: Pricing API error: Failed to initialize AWS Pricing API client: ...
```

**Reason:** AWS credentials are not configured or invalid.

**Solution:** Configure AWS credentials using `aws configure` or environment variables.

### 3. Insufficient Permissions

**Error:**
```
ERROR: AWS Pricing API returned error: AccessDeniedException - ...
```

**Reason:** AWS credentials lack required permissions.

**Solution:** Add the `pricing:GetProducts` permission to your IAM user/role.

### 4. Network Connectivity Issues

**Error:**
```
ERROR: Failed to connect to AWS services: ...
```

**Reason:** Network connectivity problems or AWS API unavailable.

**Solution:** Check internet connection, verify AWS service status, or use `--fallback`.

### 5. Model Not Found

**Error:**
```
WARNING: Could not find complete pricing data for 'model-name' in AWS Pricing API
```

**Reason:** The model doesn't exist or pricing data is incomplete.

**Solution:** Verify the model name is correct or use static pricing.

## Caching Behavior

The tool implements intelligent caching to reduce API calls:

- **Default TTL:** 60 minutes
- **Cache Location:** In-memory (not persisted)
- **Cache Key:** Model name
- **Bypass Cache:** Use `--no-cache` flag
- **Custom TTL:** Use `--cache-ttl <minutes>`

### When Cache is Used

```bash
# First call - fetches from API
python scripts/calculate_model_cost_live.py --model amazon/nova-pro-v1:0 -i 1000 -o 500

# Second call within 60 minutes - uses cache
python scripts/calculate_model_cost_live.py --model amazon/nova-pro-v1:0 -i 2000 -o 1000
```

### Force Refresh

```bash
# Always fetches fresh pricing
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 -i 1000 -o 500 --no-cache
```

## Comparison with Static Pricing

The `--compare` flag shows differences between live and static pricing:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 100000 \
  --output-tokens 50000 \
  --compare
```

Example output:
```
======================================================================
PRICING COMPARISON: Live API vs Static Data
======================================================================

Model: amazon/nova-pro-v1:0
Input tokens: 100,000
Output tokens: 50,000

----------------------------------------------------------------------

LIVE PRICING (from API):
  Input rate:  $0.800000 per 1M tokens
  Output rate: $3.200000 per 1M tokens
  Total cost:  $0.2400
  Source:      aws_pricing_api

----------------------------------------------------------------------

STATIC PRICING (from JSON file):
  Input rate:  $0.800000 per 1M tokens
  Output rate: $3.200000 per 1M tokens
  Total cost:  $0.2400
  Source:      static JSON

----------------------------------------------------------------------

DIFFERENCE:
  Absolute: $0.0000 (same)
  Relative: 0.00% (same)
======================================================================
```

## Use Cases

### 1. Real-Time Cost Estimation

Get accurate, up-to-date pricing for cost estimation:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-pro-v1:0 \
  --input-tokens 50000 \
  --output-tokens 25000 \
  --verbose
```

### 2. Pricing Validation

Verify that static pricing data is still accurate:

```bash
python scripts/calculate_model_cost_live.py \
  --model amazon/nova-lite-v1:0 \
  --input-tokens 10000 \
  --output-tokens 5000 \
  --compare
```

### 3. Automated Cost Monitoring

Integrate into scripts for automated cost tracking:

```python
from helm.benchmark.model_pricing_api import LivePricingClient

client = LivePricingClient()
models = ["amazon/nova-micro-v1:0", "amazon/nova-lite-v1:0", "amazon/nova-pro-v1:0"]

for model in models:
    pricing = client.get_live_pricing(model)
    if pricing:
        cost = pricing.calculate_cost(10000, 5000)
        print(f"{model}: ${cost:.4f}")
```

### 4. Budget Planning

Calculate costs for different usage scenarios:

```bash
# Low usage
python scripts/calculate_model_cost_live.py -m amazon/nova-pro-v1:0 -i 1000 -o 500

# Medium usage
python scripts/calculate_model_cost_live.py -m amazon/nova-pro-v1:0 -i 100000 -o 50000

# High usage
python scripts/calculate_model_cost_live.py -m amazon/nova-pro-v1:0 -i 1000000 -o 500000
```

## Troubleshooting

### Issue: boto3 Not Found

**Error:** `ModuleNotFoundError: No module named 'boto3'`

**Solution:**
```bash
pip install boto3
```

### Issue: Pricing Always Returns None

**Problem:** Live pricing always returns None even for Bedrock models.

**Possible Causes:**
1. AWS credentials not configured
2. Missing IAM permissions
3. boto3 not installed
4. Wrong AWS region

**Debug Steps:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Test AWS CLI access
aws pricing describe-services --service-code AmazonBedrock --region us-east-1

# Verify boto3 installation
python -c "import boto3; print(boto3.__version__)"
```

### Issue: AccessDeniedException

**Error:** `AccessDeniedException: User is not authorized to perform: pricing:GetProducts`

**Solution:** Add IAM permissions:
```json
{
  "Effect": "Allow",
  "Action": ["pricing:GetProducts", "pricing:DescribeServices"],
  "Resource": "*"
}
```

### Issue: Slow Performance

**Problem:** Each request takes a long time.

**Solution:**
1. Enable caching (default behavior)
2. Increase cache TTL: `--cache-ttl 120`
3. Pre-fetch pricing for commonly used models

## Extending to Other Providers

The tool is designed to be extensible. To add support for other pricing APIs:

### 1. Add Provider Method

Edit `src/helm/benchmark/model_pricing_api.py`:

```python
def _fetch_custom_provider_pricing(self, model_name: str) -> Optional[LiveModelPricing]:
    """Fetch pricing for CustomProvider models."""
    # Implement API call
    response = requests.get(f"https://api.customprovider.com/pricing/{model_name}")
    data = response.json()
    
    return LiveModelPricing(
        model_name=model_name,
        input_price_per_million=data['input_price'],
        output_price_per_million=data['output_price'],
        source="custom_provider_api",
        fetched_at=datetime.now().isoformat()
    )
```

### 2. Update get_live_pricing()

Add routing logic:

```python
def get_live_pricing(self, model_name: str, use_cache: bool = True) -> Optional[LiveModelPricing]:
    # ... existing code ...
    
    elif model_name.startswith('customprovider/'):
        pricing = self._fetch_custom_provider_pricing(model_name)
    
    # ... rest of code ...
```

## Comparison with Static Calculator

| Feature | Live Pricing Tool | Static Pricing Tool |
|---------|------------------|---------------------|
| **Data Source** | Live APIs | JSON file |
| **Accuracy** | Always current | May be outdated |
| **Speed** | Slower (API calls) | Fast (local file) |
| **Requirements** | AWS credentials, boto3 | None |
| **Offline Support** | No (requires API) | Yes |
| **Cost** | Free (within AWS limits) | Free |
| **Best For** | Production, critical estimates | Development, quick checks |

### When to Use Which?

**Use Live Pricing Tool when:**
- You need guaranteed current pricing
- Building production cost estimation systems
- Validating static pricing accuracy
- Working with recently launched models

**Use Static Pricing Tool when:**
- Working offline
- Need fast responses
- AWS credentials unavailable
- Pricing changes are not critical

## FAQ

### Q: Does this tool make charges to my AWS account?

**A:** The tool only reads pricing data using the AWS Pricing API, which is free. It does not invoke any models or incur usage charges.

### Q: How often should I refresh the cache?

**A:** Default 60 minutes is suitable for most use cases. AWS pricing changes are infrequent (weeks/months), so even daily updates are usually sufficient.

### Q: Can I use this without AWS credentials?

**A:** For non-Bedrock models, potentially yes (if other APIs don't require auth). For Bedrock models, AWS credentials are required. Use `--fallback` to use static pricing instead.

### Q: Is the pricing API rate-limited?

**A:** Yes, AWS Pricing API has rate limits. The caching mechanism helps stay within limits. For high-volume usage, consider increasing cache TTL.

### Q: What if my model isn't supported?

**A:** The tool will inform you that live pricing is unavailable. Use `--fallback` to use static pricing, or contribute by adding support for your model's pricing API.

### Q: How accurate is live pricing vs static?

**A:** Live pricing is always current. Static pricing depends on when it was last updated. Use `--compare` to check differences.

## Contributing

To contribute support for additional pricing APIs:

1. Implement a new `_fetch_<provider>_pricing()` method
2. Add routing logic in `get_live_pricing()`
3. Update `get_supported_providers()`
4. Add tests
5. Update documentation

## Support

For issues or questions:

1. Check this documentation
2. Review error messages carefully
3. Verify AWS credentials and permissions
4. Try with `--fallback` flag
5. Check AWS service health status

## See Also

- [Model Cost Calculator Quick Start](../COST_CALCULATOR_QUICKSTART.md) - Static pricing calculator
- [Model Cost Calculator README](MODEL_COST_CALCULATOR_README.md) - Detailed static pricing docs
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) - Official pricing page
- [AWS Pricing API Documentation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html)
