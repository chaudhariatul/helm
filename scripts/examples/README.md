# HELM Examples

This directory contains example scripts and documentation for using HELM with various model providers.

## AWS Bedrock Examples

If you're getting the error `botocore.exceptions.NoRegionError: You must specify a region` when running HELM with Amazon Bedrock models, see:

### Quick Start
- **[BEDROCK_QUICKSTART.md](BEDROCK_QUICKSTART.md)** - Fast resolution guide for the NoRegionError

### Scripts
- **[run_bedrock_models.sh](run_bedrock_models.sh)** - Convenience script to run HELM benchmarks with proper AWS configuration
- **[bedrock_client_usage.py](bedrock_client_usage.py)** - Configuration checker and troubleshooting guide
- **[test_region_config.py](test_region_config.py)** - Test script to verify region configuration logic

### Usage Examples

#### Quick Fix for NoRegionError

The common error:
```bash
# ❌ WRONG - Don't use ! prefix
!AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

The fix:
```bash
# ✅ CORRECT - Remove ! and use proper syntax
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5
```

#### Using the Convenience Script

```bash
# Run with defaults (nova-pro-v1:0, clinical_knowledge, 5 instances)
./scripts/examples/run_bedrock_models.sh

# Run with custom parameters
./scripts/examples/run_bedrock_models.sh amazon/nova-lite-v1:0 anatomy 10
```

#### Check Your Configuration

```bash
# Run configuration checker
python scripts/examples/bedrock_client_usage.py

# Run region configuration tests
python scripts/examples/test_region_config.py
```

## Other Examples

- **[auto_client_usage.py](auto_client_usage.py)** - Example of using HELM client programmatically
- **[request_json_schema.py](request_json_schema.py)** - Request schema examples
- **[server_service_usage.py](server_service_usage.py)** - HELM server service examples

## Documentation

For complete setup instructions, see:
- [AWS Bedrock Quick Start](BEDROCK_QUICKSTART.md)
- [Credentials Documentation](../../docs/credentials.md)
- [HELM Tutorial](../../docs/tutorial.md)

## Common Issues

### NoRegionError: You must specify a region

**Cause:** AWS_REGION environment variable not set

**Solution:**
```bash
export AWS_REGION=us-west-2
```

### NoCredentialsError: Unable to locate credentials

**Cause:** AWS credentials not configured

**Solution:**
```bash
aws configure
```

### AccessDeniedException

**Cause:** Insufficient IAM permissions

**Solution:** Ensure your IAM user/role has `bedrock:InvokeModel` permission

## Getting Help

1. Read [BEDROCK_QUICKSTART.md](BEDROCK_QUICKSTART.md) for AWS Bedrock issues
2. Check [docs/credentials.md](../../docs/credentials.md) for credential setup
3. Run diagnostic scripts to identify configuration issues
4. Review error messages carefully - they often indicate exactly what's wrong

## Contributing

When adding new examples:
1. Include clear documentation and comments
2. Add error handling and helpful error messages
3. Update this README with links to your example
4. Test thoroughly before committing
