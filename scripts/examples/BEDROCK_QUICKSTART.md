# AWS Bedrock Quick Start Guide

This guide helps you quickly resolve the common `botocore.exceptions.NoRegionError: You must specify a region` error when running HELM benchmarks with Amazon Bedrock models.

## The Problem

If you see this error:

```
botocore.exceptions.NoRegionError: You must specify a region.
```

It means the AWS region environment variable is not properly set.

## The Solution

### ❌ INCORRECT (Common Mistake)

```bash
# DON'T use the ! prefix - this is only for Jupyter notebooks
!AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

### ✅ CORRECT Methods

#### Method 1: Export First (Recommended)

```bash
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Advantages:**
- Region persists for all commands in the session
- Cleaner command lines
- Easy to verify: `echo $AWS_REGION`

#### Method 2: Inline Environment Variable

```bash
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

**Advantages:**
- Sets region only for that specific command
- Good for scripts or one-off commands
- No shell state changes

#### Method 3: Use the Provided Script

```bash
# Run with defaults (nova-pro-v1:0, clinical_knowledge, 5 instances)
./scripts/examples/run_bedrock_models.sh

# Run with custom parameters
./scripts/examples/run_bedrock_models.sh amazon/nova-lite-v1:0 anatomy 10
```

**Advantages:**
- Handles region configuration automatically
- Validates AWS credentials
- Provides helpful error messages

## Complete Setup

### Step 1: Configure AWS Credentials

Choose one of these methods:

```bash
# Option A: AWS CLI (Recommended)
aws configure

# Option B: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Option C: AWS Profile
export AWS_PROFILE=your_profile_name
```

### Step 2: Set AWS Region

```bash
export AWS_REGION=us-west-2
```

Common regions for Bedrock:
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon) - **Recommended** (most models available)
- `eu-central-1` - Europe (Frankfurt)
- `ap-northeast-1` - Asia Pacific (Tokyo)

### Step 3: Run HELM Benchmark

```bash
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

## Available Amazon Bedrock Models

### Amazon Nova Models (Latest)

```bash
# Nova Pro - Best performance
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Nova Lite - Faster, more cost-effective
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-lite-v1:0 --suite quick-test --max-eval-instances 5

# Nova Micro - Smallest, fastest
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=computer_science,model=amazon/nova-micro-v1:0 --suite quick-test --max-eval-instances 5
```

### Amazon Titan Models

```bash
# Titan Text Express
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=high_school_biology,model=amazon/titan-text-express-v1 --suite quick-test --max-eval-instances 5

# Titan Text Lite
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=high_school_chemistry,model=amazon/titan-text-lite-v1 --suite quick-test --max-eval-instances 5
```

## Testing Your Configuration

Run the configuration checker:

```bash
python scripts/examples/bedrock_client_usage.py
```

This will:
- Check if AWS credentials are configured
- Verify region is set
- Show common errors and solutions
- Display example commands

## Troubleshooting

### Error: "NoRegionError: You must specify a region"

**Solution:** Set the AWS_REGION environment variable

```bash
export AWS_REGION=us-west-2
```

### Error: "NoCredentialsError: Unable to locate credentials"

**Solution:** Configure AWS credentials

```bash
aws configure
```

### Error: "AccessDeniedException"

**Solution:** Ensure your IAM user/role has Bedrock permissions

Required IAM permissions:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

Example policy:

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
            "Resource": "*"
        }
    ]
}
```

### Error: "Could not connect to the endpoint URL"

**Causes:**
1. Model not available in selected region
2. Network connectivity issues
3. Incorrect endpoint

**Solution:** Try a different region (us-west-2 recommended)

```bash
export AWS_REGION=us-west-2
```

## Additional Resources

- **Full Documentation:** See `docs/credentials.md` for comprehensive setup instructions
- **Model Documentation:** [AWS Bedrock Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- **Region Availability:** [Model Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)
- **AWS CLI Setup:** [Installing AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Quick Command Reference

```bash
# Export region (do this once per session)
export AWS_REGION=us-west-2

# Run benchmark
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Or combine in one line
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Check configuration
python scripts/examples/bedrock_client_usage.py

# Use convenience script
./scripts/examples/run_bedrock_models.sh amazon/nova-pro-v1:0 clinical_knowledge 5
```

## Summary

The key fix for the `NoRegionError` is simple:

1. **Remove the `!` prefix** from your command
2. **Set AWS_REGION** using `export` or inline
3. **Use `us-west-2`** for best model availability

That's it! You should now be able to run HELM benchmarks with Amazon Bedrock models successfully.
