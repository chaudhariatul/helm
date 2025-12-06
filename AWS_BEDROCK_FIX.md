# AWS Bedrock Errors - ALL FIXED ✓

## Two Errors Fixed

### Error 1: NoRegionError - FIXED ✓
### Error 2: ValidationException with Nova Models - FIXED ✓

See [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md) for details on both fixes.

---

## Error 1: NoRegionError Fix

If you're getting `botocore.exceptions.NoRegionError: You must specify a region` when running HELM with Amazon Nova Pro or other AWS Bedrock models:

### ❌ WRONG (What Was Causing Error 1)

```bash
!AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Problem:** The `!` prefix is only for Jupyter notebooks. In bash/shell, it prevents the environment variable from being set properly.

### ✅ CORRECT (Error 1 Fix)

Choose one of these methods:

**Method 1: Export First (Recommended for multiple commands)**
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Method 2: Inline (For single commands)**
```bash
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Method 3: Use the Convenience Script**
```bash
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

---

## Error 2: ValidationException with Nova Models Fix

If you got the region working but now see:

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling 
the Converse operation: Invocation of model ID amazon.nova-pro-v1:0 with on-demand throughput 
isn't supported. Retry your request with the ID or ARN of an inference profile that contains 
this model.
```

**This is now FIXED!** The model configurations have been updated to use inference profile IDs automatically.

**What changed:** Amazon Nova models now use cross-region inference profiles (`us.amazon.nova-pro-v1:0`) instead of direct model IDs.

**You don't need to do anything different** - just use the model name as usual: `amazon/nova-pro-v1:0`

See [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md) for complete technical details.

## Testing Both Fixes

Run this test script to verify both fixes work:
```bash
./test_nova_inference_profile.sh
```

Or run an actual benchmark:
```bash
./run_nova_with_fixes.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

## Documentation

### Quick References
- **[AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)** - Complete fix documentation for both errors
- **[BEDROCK_QUICKSTART.md](scripts/examples/BEDROCK_QUICKSTART.md)** - Fast troubleshooting guide
- **[FIX_SUMMARY.md](FIX_SUMMARY.md)** - Documentation of Error 1 fix

### Credentials Setup
- **[docs/credentials.md](docs/credentials.md)** - Full AWS Bedrock setup instructions (see "AWS Bedrock" section)

### Helper Scripts
- **[run_nova_with_fixes.sh](run_nova_with_fixes.sh)** - Convenience script with both fixes applied
- **[test_nova_inference_profile.sh](test_nova_inference_profile.sh)** - Test both fixes
- **[run_bedrock_models.sh](scripts/examples/run_bedrock_models.sh)** - Alternative convenience script
- **[bedrock_client_usage.py](scripts/examples/bedrock_client_usage.py)** - Configuration checker and troubleshooting tool
- **[test_region_config.py](scripts/examples/test_region_config.py)** - Test region configuration logic

## Checking Your Configuration

Run the configuration checker to diagnose issues:
```bash
python3 scripts/examples/bedrock_client_usage.py
```

Or run the region configuration tests:
```bash
python3 scripts/examples/test_region_config.py
```

## Common AWS Regions for Bedrock

- `us-west-2` - US West (Oregon) - **Recommended** (most models available)
- `us-east-1` - US East (N. Virginia)
- `eu-central-1` - Europe (Frankfurt)
- `ap-northeast-1` - Asia Pacific (Tokyo)

## Interactive Fix Script

Run the interactive script to see all correction options:
```bash
./CORRECTED_COMMAND.sh
```

## Complete Setup (First Time Users)

### 1. Configure AWS Credentials

```bash
# Option A: Use AWS CLI (recommended)
aws configure

# Option B: Set environment variables
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here
```

### 2. Set AWS Region

```bash
export AWS_REGION=us-west-2
```

### 3. Verify Configuration

```bash
# Check region is set
echo $AWS_REGION

# Run configuration checker
python3 scripts/examples/bedrock_client_usage.py
```

### 4. Run HELM Benchmark

```bash
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

## Available Amazon Bedrock Models

### Amazon Nova Models
- `amazon/nova-pro-v1:0` - Best performance
- `amazon/nova-lite-v1:0` - Faster, cost-effective
- `amazon/nova-micro-v1:0` - Smallest, fastest

### Amazon Titan Models
- `amazon/titan-text-express-v1` - Express version
- `amazon/titan-text-lite-v1` - Lite version

## Troubleshooting

### NoRegionError (Error 1)
**Solution:** Set AWS_REGION environment variable
```bash
export AWS_REGION=us-west-2
```

### ValidationException with Nova (Error 2)
**Solution:** Already fixed! Model configurations now use inference profiles automatically.
If you still see this error:
1. Verify you have the latest configuration
2. Run `./test_nova_inference_profile.sh` to check
3. See [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md) for details

### NoCredentialsError
**Solution:** Configure AWS credentials
```bash
aws configure
```

### AccessDeniedException
**Solution:** Ensure IAM permissions for Bedrock
- Required: `bedrock:InvokeModel` permission
- Use policy: `AmazonBedrockFullAccess` or equivalent

## Example Commands

```bash
# Amazon Nova Pro
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Amazon Nova Lite
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-lite-v1:0 --suite quick-test --max-eval-instances 10

# Amazon Titan Text Express
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=computer_science,model=amazon/titan-text-express-v1 --suite quick-test --max-eval-instances 5
```

## What Changed

1. **Updated documentation** - Added comprehensive AWS Bedrock setup to `docs/credentials.md`
2. **Created helper scripts** - Scripts to validate configuration and run benchmarks
3. **Added quick start guide** - Fast reference for fixing NoRegionError
4. **Created test scripts** - Verify region configuration works correctly

## Summary

**Both Fixes Applied:**

1. **Error 1 - NoRegionError:** Remove the `!` prefix from your command.
   - ❌ `!AWS_REGION=us-west-2 helm-run ...`
   - ✅ `AWS_REGION=us-west-2 helm-run ...`

2. **Error 2 - ValidationException:** Model configurations updated to use inference profiles.
   - ❌ Old: Direct model ID `amazon.nova-pro-v1:0`
   - ✅ New: Inference profile `us.amazon.nova-pro-v1:0` (automatic)

**Complete Working Command:**
```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

The `!` prefix is only for Jupyter notebooks, not for bash/shell terminals.
Amazon Nova models now automatically use cross-region inference profiles.

---

**For detailed information, see:**
- Complete Fix Guide: [AWS_NOVA_INFERENCE_PROFILE_FIX.md](AWS_NOVA_INFERENCE_PROFILE_FIX.md)
- Quick Start: [scripts/examples/BEDROCK_QUICKSTART.md](scripts/examples/BEDROCK_QUICKSTART.md)
- Error 1 Details: [FIX_SUMMARY.md](FIX_SUMMARY.md)
- Credentials Setup: [docs/credentials.md](docs/credentials.md)
