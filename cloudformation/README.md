# MedHELM SageMaker Workshop - CloudFormation Template

This directory contains a production-ready CloudFormation template and supporting materials for deploying a SageMaker AI Domain configured for MedHELM workshops and evaluations.

## Contents

- **`sagemaker-medhelm-domain.yaml`** - Main CloudFormation template
- **`DEPLOYMENT_GUIDE.md`** - Comprehensive deployment and usage guide
- **`workshop-notebook-1-introduction.ipynb`** - Setup verification and introduction
- **`workshop-notebook-2-tiny-evaluation.ipynb`** - Running tiny evaluations
- **`workshop-notebook-3-scenarios.ipynb`** - Exploring MedHELM scenarios
- **`workshop-notebook-4-custom-benchmarks.ipynb`** - Creating custom benchmarks

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- VPC with internet access (via NAT Gateway or Internet Gateway)
- At least one subnet

### Deploy

1. **Via AWS Console**:
   ```
   1. Go to CloudFormation Console
   2. Create Stack → Upload sagemaker-medhelm-domain.yaml
   3. Fill in parameters (VPC ID, Subnet IDs)
   4. Create stack (takes ~10-15 minutes)
   ```

2. **Via AWS CLI**:
   ```bash
   aws cloudformation create-stack \
     --stack-name medhelm-workshop \
     --template-body file://sagemaker-medhelm-domain.yaml \
     --parameters \
       ParameterKey=VpcId,ParameterValue=vpc-xxxxx \
       ParameterKey=SubnetIds,ParameterValue="subnet-xxxxx" \
     --capabilities CAPABILITY_NAMED_IAM
   ```

### Access

After deployment:
1. Go to SageMaker Console → Domains
2. Select your domain → User profile
3. Launch → Code Editor
4. Upload workshop notebooks to `~/workshop-notebooks/`

## What's Included

### Pre-installed Software

- **Python 3.10** (required for MedHELM)
- **uv package manager** - Fast Python package installer
- **pip, setuptools, wheel** (upgraded)
- **boto3** - AWS SDK for Python
- **sagemaker** - SageMaker Python SDK
- **crfm-helm[summarization,medhelm]** - HELM framework with MedHELM extensions
- **Google Cloud SDK** - For accessing public benchmark data
- **Jupyter, pandas, matplotlib** - Workshop tools

### Pre-configured Environment

- **HELM repository** cloned to `~/helm/`
- **Benchmark output directory** at `~/benchmark_output/`
- **Workshop notebooks directory** at `~/workshop-notebooks/`
- **Python virtual environment** at `~/medhelm-env/`
- **Verification script** at `~/verify_setup.sh`

## Workshop Flow

Follow the notebooks in order:

1. **Introduction** - Verify setup, understand MedHELM
2. **Tiny Evaluation** - Run your first evaluation (10 instances)
3. **Scenarios** - Explore available scenarios and metrics
4. **Custom Benchmarks** - Create your own benchmarks

## Features

### SageMaker Domain Configuration

- **Auth Mode**: IAM (no SSO required)
- **Network**: VPC mode with configurable subnets
- **Instance Type**: Configurable (default: ml.t3.medium)
- **Storage**: Persistent EFS storage

### Lifecycle Configuration

Automatically sets up:
- Package installations
- Repository clones
- Environment configuration
- Directory structure
- Helper scripts and documentation

### Security

- IAM execution role with scoped permissions
- VPC-only network access
- Security groups with self-referencing rules
- No hardcoded credentials

### Production-Ready

- Parameterized for different environments
- Tagged resources for cost tracking
- Proper IAM policies
- Error handling in lifecycle scripts
- Comprehensive logging

## Cost Estimate

Approximate costs (us-east-1):

| Component | Cost |
|-----------|------|
| Code Editor (ml.t3.medium) | ~$0.30/hour |
| EFS Storage (10 GB) | ~$3/month |
| Data Transfer | Variable |

**Tip**: Stop Code Editor when not in use to reduce costs.

## Customization

### Change Instance Type

Edit the template or pass parameter:
```bash
--parameters ParameterKey=CodeEditorInstanceType,ParameterValue=ml.m5.large
```

Available: `ml.t3.medium`, `ml.t3.large`, `ml.m5.large`, `ml.m5.xlarge`, etc.

### Add More Users

Add additional `AWS::SageMaker::UserProfile` resources to the template.

### Modify Lifecycle Config

Edit the `StudioLifecycleConfigContent` section to:
- Install additional packages
- Clone different repositories
- Configure custom settings

## Troubleshooting

### Lifecycle Configuration Failed

Check logs:
```bash
cat /var/log/lifecycle-config.log
```

### Cannot Access Internet

Verify:
- VPC has NAT Gateway or Internet Gateway
- Security group allows outbound traffic
- Subnet routing table is correct

### helm-run Not Found

Activate environment:
```bash
source ~/medhelm-env/bin/activate
```

See `DEPLOYMENT_GUIDE.md` for more troubleshooting tips.

## Documentation

- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **MedHELM Docs**: https://crfm.stanford.edu/helm/medhelm/latest/
- **HELM GitHub**: https://github.com/stanford-crfm/helm
- **AWS SageMaker**: https://docs.aws.amazon.com/sagemaker/

## Support

- **MedHELM/HELM Issues**: https://github.com/stanford-crfm/helm/issues
- **AWS Support**: Through AWS Support Center
- **This Template**: See troubleshooting section

## License

This CloudFormation template is part of the HELM project. See the main repository LICENSE file.

## References

- MedHELM Paper: https://arxiv.org/abs/2505.23802
- Stanford CRFM: https://crfm.stanford.edu/
- HELM Leaderboard: https://crfm.stanford.edu/helm/

---

**Version**: 1.0.0
**Last Updated**: December 2024
