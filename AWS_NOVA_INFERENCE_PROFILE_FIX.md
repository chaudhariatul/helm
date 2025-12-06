# AWS Amazon Nova Inference Profile Fix ✓

## Problem

When running HELM benchmarks with Amazon Nova models, users encountered two errors:

### Error 1: NoRegionError (FIXED ✓)
```
botocore.exceptions.NoRegionError: You must specify a region.
```

**Cause:** Incorrect command syntax using `!` prefix  
**Fix:** Remove `!` and use proper bash syntax (See [AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md))

### Error 2: ValidationException with Nova Models (FIXED ✓)
```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling 
the Converse operation: Invocation of model ID amazon.nova-pro-v1:0 with on-demand throughput 
isn't supported. Retry your request with the ID or ARN of an inference profile that contains 
this model.
```

**Cause:** Amazon Nova models require cross-region inference profile IDs instead of direct model IDs  
**Fix:** Updated model configurations to use inference profile IDs

## Solution

### What Changed

The HELM configuration has been updated to automatically use inference profile IDs for all Amazon Nova models:

| Model | Old Model ID | New Inference Profile ID |
|-------|-------------|--------------------------|
| amazon/nova-pro-v1:0 | amazon.nova-pro-v1:0 | us.amazon.nova-pro-v1:0 |
| amazon/nova-lite-v1:0 | amazon.nova-lite-v1:0 | us.amazon.nova-lite-v1:0 |
| amazon/nova-micro-v1:0 | amazon.nova-micro-v1:0 | us.amazon.nova-micro-v1:0 |

### How It Works

**Before:** The BedrockNovaClient converted model names like `amazon/nova-pro-v1:0` to `amazon.nova-pro-v1:0`, which AWS Bedrock rejected for on-demand throughput.

**After:** The configuration now specifies `bedrock_model_id: us.amazon.nova-pro-v1:0`, which uses the US cross-region inference profile that AWS Bedrock requires.

## Usage

### Corrected Command

Now you can run HELM with Nova models using the proper command:

```bash
# Export the region (recommended)
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Or use inline syntax
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### Quick Test Script

Create a test script to verify the fix:

```bash
cat > test_nova_fix.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing Amazon Nova with Inference Profile Fix"
echo "================================================"
echo ""

# Check AWS region
if [ -z "$AWS_REGION" ]; then
    echo "Setting AWS_REGION to us-west-2..."
    export AWS_REGION=us-west-2
fi
echo "✓ AWS_REGION: $AWS_REGION"

# Check AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi
echo "✓ AWS credentials configured"

echo ""
echo "Running HELM with Amazon Nova Pro (with inference profile)..."
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

echo ""
echo "✓ Success! Amazon Nova models now work with inference profiles"
EOF

chmod +x test_nova_fix.sh
./test_nova_fix.sh
```

## Technical Details

### Inference Profiles Explained

**What are inference profiles?**
- Cross-region inference profiles allow AWS Bedrock to route requests across multiple regions
- They provide higher throughput and better availability
- They are required for certain models (like Nova) when using on-demand throughput

**Profile ID Format:**
- US regions: `us.amazon.nova-pro-v1:0`
- EU regions: `eu.amazon.nova-pro-v1:0` (when available)
- Asia regions: `ap.amazon.nova-pro-v1:0` (when available)

**Why US prefix for all regions?**
The `us.` prefix doesn't mean the model only works in US regions. It's a cross-region inference profile that:
- Can be called from any region where Nova is available
- Automatically routes to the best available region within the geography
- Provides higher throughput than single-region model IDs

### Code Changes

**File:** `src/helm/config/model_deployments.yaml`

**Before:**
```yaml
- name: amazon/nova-pro-v1:0
  model_name: amazon/nova-pro-v1:0
  tokenizer_name: huggingface/gpt2
  max_sequence_length: 300000
  client_spec:
    class_name: "helm.clients.bedrock_client.BedrockNovaClient"
```

**After:**
```yaml
- name: amazon/nova-pro-v1:0
  model_name: amazon/nova-pro-v1:0
  tokenizer_name: huggingface/gpt2
  max_sequence_length: 300000
  client_spec:
    class_name: "helm.clients.bedrock_client.BedrockNovaClient"
    args:
      bedrock_model_id: us.amazon.nova-pro-v1:0
```

### How BedrockNovaClient Handles Inference Profiles

The `BedrockNovaClient` class in `src/helm/clients/bedrock_client.py` already supported the `bedrock_model_id` parameter:

```python
def __init__(
    self,
    cache_config: CacheConfig,
    tokenizer: Tokenizer,
    tokenizer_name: str,
    assumed_role: Optional[str] = None,
    region: Optional[str] = None,
    bedrock_model_id: Optional[str] = None,  # ← Supports inference profile IDs
):
    ...
    self.bedrock_model_id = bedrock_model_id

def convert_request_to_raw_request(self, request: Request) -> Dict:
    model_id = request.model.replace("/", ".")
    messages = self._get_messages_from_request(request)
    
    return {
        "modelId": self.bedrock_model_id or model_id,  # ← Uses inference profile if provided
        "inferenceConfig": {...},
        "messages": messages,
    }
```

The fix simply leverages this existing functionality by configuring the `bedrock_model_id` parameter in the YAML configuration.

## Regional Considerations

### Using Nova in Different Regions

The `us.amazon.nova-pro-v1:0` inference profile works from any region, but you still need to:

1. **Set AWS_REGION environment variable** to specify your API endpoint region:
   ```bash
   export AWS_REGION=us-west-2  # or us-east-1, eu-central-1, etc.
   ```

2. **Ensure Nova is available** in your region. Check availability:
   - [AWS Bedrock Model Availability](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)

### Common Regions for Nova

| Region | Code | Nova Availability |
|--------|------|-------------------|
| US West (Oregon) | us-west-2 | ✓ Available |
| US East (N. Virginia) | us-east-1 | ✓ Available |
| EU (Frankfurt) | eu-central-1 | Check AWS docs |
| Asia Pacific (Tokyo) | ap-northeast-1 | Check AWS docs |

### Custom Inference Profiles

If you need to use a specific regional profile or application inference profile:

**Option 1: Environment Variable Override (Coming Soon)**
```bash
export BEDROCK_MODEL_ID="arn:aws:bedrock:us-west-2:123456789:inference-profile/my-custom-profile"
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Option 2: Custom Model Deployment (Current Method)**
Add to `model_deployments.yaml`:
```yaml
- name: my-org/custom-nova-pro
  model_name: amazon/nova-pro-v1:0
  tokenizer_name: huggingface/gpt2
  max_sequence_length: 300000
  client_spec:
    class_name: "helm.clients.bedrock_client.BedrockNovaClient"
    args:
      bedrock_model_id: arn:aws:bedrock:us-west-2:123456789:inference-profile/my-custom-profile
```

Then use: `model=my-org/custom-nova-pro`

## Troubleshooting

### Error: ValidationException - Model not supported
```
ValidationException: Invocation of model ID ... with on-demand throughput isn't supported
```

**Solution:** This error should no longer occur with the fix. If it does:
1. Ensure you're using the latest HELM version with the fix
2. Verify the model configuration in `model_deployments.yaml`
3. Check that you're using the correct model name: `amazon/nova-pro-v1:0`

### Error: NoRegionError
```
botocore.exceptions.NoRegionError: You must specify a region
```

**Solution:** Set the AWS_REGION environment variable:
```bash
export AWS_REGION=us-west-2
```

See [AWS_BEDROCK_FIX.md](AWS_BEDROCK_FIX.md) for details.

### Error: ResourceNotFoundException
```
ResourceNotFoundException: The inference profile identifier ... could not be found
```

**Possible Causes:**
1. Nova models not available in your region
2. Incorrect inference profile ID
3. AWS account doesn't have access to Nova models

**Solutions:**
1. Use a region where Nova is available (us-west-2 or us-east-1)
2. Verify the inference profile ID is correct
3. Check AWS Bedrock model access in your account

### Error: AccessDeniedException
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

**Solution:** Ensure IAM permissions:
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
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/amazon.nova-*",
        "arn:aws:bedrock:*:*:inference-profile/*"
      ]
    }
  ]
}
```

## Verification

### Quick Verification Steps

1. **Check the configuration is updated:**
   ```bash
   grep -A 5 "amazon/nova-pro-v1:0" src/helm/config/model_deployments.yaml
   ```
   
   Should show:
   ```yaml
   client_spec:
     class_name: "helm.clients.bedrock_client.BedrockNovaClient"
     args:
       bedrock_model_id: us.amazon.nova-pro-v1:0
   ```

2. **Test the model:**
   ```bash
   export AWS_REGION=us-west-2
   helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
   ```

3. **Verify no ValidationException:**
   - The command should run without the ValidationException error
   - You should see normal HELM benchmark progress output

## Summary

### Both Errors Fixed ✓

1. **NoRegionError (Error 1):**
   - ❌ Wrong: `!AWS_REGION=us-west-2 helm-run ...`
   - ✓ Fixed: `AWS_REGION=us-west-2 helm-run ...`

2. **ValidationException (Error 2):**
   - ❌ Wrong: Using model ID `amazon.nova-pro-v1:0`
   - ✓ Fixed: Using inference profile ID `us.amazon.nova-pro-v1:0`

### Complete Working Command

```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### Files Changed

- **Modified:** `src/helm/config/model_deployments.yaml`
  - Added `bedrock_model_id` parameter for all Nova models
  - Uses cross-region inference profile IDs

- **Created:** `AWS_NOVA_INFERENCE_PROFILE_FIX.md` (this file)
  - Complete documentation of the inference profile fix
  - Regional considerations and troubleshooting

## Resources

### Documentation
- [AWS Bedrock Fix](AWS_BEDROCK_FIX.md) - Region configuration fix
- [Bedrock Quick Start](scripts/examples/BEDROCK_QUICKSTART.md) - Fast troubleshooting
- [HELM Credentials](docs/credentials.md) - AWS setup guide

### AWS Documentation
- [Cross-Region Inference](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
- [Nova Models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html)
- [Inference Profile Support](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)

### Helper Scripts
- `scripts/examples/run_bedrock_models.sh` - Convenience script
- `scripts/examples/bedrock_client_usage.py` - Configuration checker

---

**Status:** ✅ FIXED AND READY TO USE

Both errors are now resolved. Users can run HELM benchmarks with Amazon Nova models successfully.
