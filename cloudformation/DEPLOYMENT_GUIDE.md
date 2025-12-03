# MedHELM SageMaker Domain Deployment Guide

This guide provides step-by-step instructions for deploying a production-ready SageMaker AI Domain configured for MedHELM workshops and evaluations.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Deployment Steps](#deployment-steps)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Using the Environment](#using-the-environment)
7. [Troubleshooting](#troubleshooting)
8. [Cost Optimization](#cost-optimization)
9. [Security Considerations](#security-considerations)

## Overview

This CloudFormation template provisions:

- **SageMaker AI Domain** with IAM authentication
- **Code Editor Environment** pre-configured with:
  - Python 3.10 (required for MedHELM)
  - uv package manager
  - pip, boto3, sagemaker (upgraded)
  - crfm-helm[summarization,medhelm]
  - Google Cloud SDK (for accessing public benchmarks)
- **Pre-cloned HELM repository** from GitHub
- **Workshop Jupyter notebooks** for hands-on training
- **Benchmark output directory** with optional data downloads

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **VPC with Internet Access**:
   - At least one subnet (preferably private with NAT Gateway)
   - Internet Gateway or NAT Gateway for outbound connectivity
3. **AWS CLI** installed and configured (optional, for CLI deployment)
4. **Appropriate IAM Permissions**:
   - CloudFormation: CreateStack, UpdateStack, DeleteStack
   - SageMaker: CreateDomain, CreateUserProfile
   - IAM: CreateRole, AttachRolePolicy
   - EC2: CreateSecurityGroup, AuthorizeSecurityGroup
   - VPC: DescribeVpcs, DescribeSubnets

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Region                            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    VPC                                  │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │           Subnet (Private + NAT)                │    │ │
│  │  │                                                  │    │ │
│  │  │  ┌────────────────────────────────────┐        │    │ │
│  │  │  │   SageMaker Domain                │        │    │ │
│  │  │  │                                    │        │    │ │
│  │  │  │  ┌──────────────────────────┐    │        │    │ │
│  │  │  │  │   User Profile           │    │        │    │ │
│  │  │  │  │                          │    │        │    │ │
│  │  │  │  │  ┌────────────────┐    │    │        │    │ │
│  │  │  │  │  │ Code Editor    │    │    │        │    │ │
│  │  │  │  │  │ - Python 3.10  │    │    │        │    │ │
│  │  │  │  │  │ - uv, pip      │    │    │        │    │ │
│  │  │  │  │  │ - crfm-helm    │    │    │        │    │ │
│  │  │  │  │  │ - gcloud SDK   │    │    │        │    │ │
│  │  │  │  │  └────────────────┘    │    │        │    │ │
│  │  │  │  └──────────────────────────┘    │        │    │ │
│  │  │  └────────────────────────────────────┘        │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Steps

### Option 1: AWS Console Deployment

1. **Navigate to CloudFormation Console**:
   - Go to AWS Console → CloudFormation
   - Choose your desired region

2. **Create Stack**:
   - Click "Create stack" → "With new resources"
   - Select "Upload a template file"
   - Upload `sagemaker-medhelm-domain.yaml`
   - Click "Next"

3. **Specify Stack Details**:
   - **Stack name**: `medhelm-workshop-stack` (or your choice)
   - **Parameters**:
     - `DomainName`: Name for your SageMaker domain (default: `medhelm-workshop-domain`)
     - `UserProfileName`: Name for the user profile (default: `medhelm-user`)
     - `VpcId`: Select your VPC
     - `SubnetIds`: Select one or more subnets (private with NAT recommended)
     - `CodeEditorInstanceType`: Choose instance size (default: `ml.t3.medium`)
   - Click "Next"

4. **Configure Stack Options**:
   - Add tags (optional):
     - Key: `Project`, Value: `MedHELM`
     - Key: `Environment`, Value: `Workshop`
   - Click "Next"

5. **Review and Create**:
   - Review all settings
   - Check "I acknowledge that AWS CloudFormation might create IAM resources"
   - Click "Create stack"

6. **Monitor Creation**:
   - Stack creation takes approximately 10-15 minutes
   - Monitor the "Events" tab for progress
   - Wait for status: `CREATE_COMPLETE`

### Option 2: AWS CLI Deployment

```bash
# Set variables
STACK_NAME="medhelm-workshop-stack"
VPC_ID="vpc-xxxxxxxxx"  # Replace with your VPC ID
SUBNET_IDS="subnet-xxxxxxxx,subnet-yyyyyyyy"  # Replace with your subnet IDs
REGION="us-east-1"  # Replace with your region

# Deploy stack
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://sagemaker-medhelm-domain.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=$VPC_ID \
    ParameterKey=SubnetIds,ParameterValue=\"$SUBNET_IDS\" \
    ParameterKey=CodeEditorInstanceType,ParameterValue=ml.t3.medium \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Monitor stack creation
aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $REGION

# Get outputs
aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs'
```

## Post-Deployment Configuration

### 1. Access SageMaker Domain

After deployment completes:

1. Navigate to SageMaker Console
2. Go to "Domains" in the left sidebar
3. Click on your domain (e.g., `medhelm-workshop-domain`)
4. Click on the user profile (e.g., `medhelm-user`)
5. Click "Launch" → "Code Editor"

### 2. Verify Installation

Once Code Editor launches, open a terminal and run:

```bash
# Verify setup
./verify_setup.sh

# Or check individual components
python --version  # Should show Python 3.10.x
pip list | grep helm
gcloud --version
uv --version
```

### 3. Upload Workshop Notebooks

The workshop notebooks are available in the `cloudformation/` directory:

1. In Code Editor, navigate to `~/workshop-notebooks/`
2. Upload the following notebooks:
   - `workshop-notebook-1-introduction.ipynb`
   - `workshop-notebook-2-tiny-evaluation.ipynb`
   - `workshop-notebook-3-scenarios.ipynb`
   - `workshop-notebook-4-custom-benchmarks.ipynb`

Alternatively, download them directly in Code Editor:

```bash
cd ~/workshop-notebooks/
curl -O https://raw.githubusercontent.com/stanford-crfm/helm/main/docs/medhelm.md
# Add more curl commands for notebooks as needed
```

### 4. Configure API Keys (if needed)

If using commercial LLM APIs:

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"

# Add to .bashrc for persistence
echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.bashrc
```

### 5. Download Benchmark Data (Optional)

To download pre-computed MedHELM benchmark results:

```bash
# Authenticate with Google Cloud (for private buckets)
gcloud auth login

# Download benchmark outputs
export OUTPUT_PATH="~/benchmark_output"
export GCS_PATH="gs://crfm-helm-public/medhelm/benchmark_output"
gcloud storage rsync -r $GCS_PATH $OUTPUT_PATH
```

## Using the Environment

### Quick Start

1. **Activate Python Environment**:
   ```bash
   source ~/medhelm-env/bin/activate
   ```

2. **Run Tiny Evaluation**:
   ```bash
   export OUTPUT_PATH="./benchmark_output"
   export RUN_ENTRIES="pubmed_qa:model=openai/gpt-3.5-turbo"
   export SUITE="test-suite"
   export MAX_EVAL_INSTANCES=10

   helm-run \
     --run-entries $RUN_ENTRIES \
     --suite $SUITE \
     --max-eval-instances $MAX_EVAL_INSTANCES \
     --output-path $OUTPUT_PATH
   ```

3. **Create Summary**:
   ```bash
   helm-summarize \
     --auto-generate-schema \
     --suite $SUITE \
     --output-path $OUTPUT_PATH
   ```

4. **Launch Leaderboard**:
   ```bash
   helm-server \
     --suite $SUITE \
     --output-path $OUTPUT_PATH
   ```

### Workshop Flow

Follow the notebooks in order:

1. **Introduction** (`workshop-notebook-1-introduction.ipynb`):
   - Verify environment setup
   - Understand MedHELM framework
   - Check AWS configuration

2. **Tiny Evaluation** (`workshop-notebook-2-tiny-evaluation.ipynb`):
   - Run first evaluation
   - Understand output structure
   - Create and view results

3. **Exploring Scenarios** (`workshop-notebook-3-scenarios.ipynb`):
   - Learn about available scenarios
   - Run multiple scenarios
   - Compare results

4. **Custom Benchmarks** (`workshop-notebook-4-custom-benchmarks.ipynb`):
   - Create custom prompt templates
   - Build custom datasets
   - Run custom evaluations

## Troubleshooting

### Common Issues

#### 1. Lifecycle Configuration Fails

**Symptom**: Code Editor launches but tools are not installed

**Solution**:
```bash
# Check lifecycle log
cat /var/log/lifecycle-config.log

# Re-run installation manually
cd ~
curl -LsSf https://astral.sh/uv/install.sh | sh
pip install --upgrade "crfm-helm[summarization,medhelm]"
```

#### 2. Cannot Access Internet

**Symptom**: Package installation fails with network errors

**Solution**:
- Verify VPC has NAT Gateway or Internet Gateway
- Check security group allows outbound traffic
- Verify subnet routing table

#### 3. helm-run Command Not Found

**Symptom**: `helm-run: command not found`

**Solution**:
```bash
# Activate virtual environment
source ~/medhelm-env/bin/activate

# Verify installation
pip list | grep helm

# Reinstall if needed
pip install --upgrade crfm-helm
```

#### 4. Google Cloud SDK Authentication

**Symptom**: Cannot download benchmark data

**Solution**:
```bash
# For public buckets, disable auth
gcloud config set auth/disable_credentials true

# For private buckets, authenticate
gcloud auth login
```

#### 5. Out of Memory Errors

**Symptom**: Kernel dies or OOM errors during evaluation

**Solution**:
- Use smaller `max-eval-instances`
- Choose larger instance type
- Use smaller models
- Clear cache: `rm -rf ~/.cache/helm`

### Getting Help

- **MedHELM Documentation**: https://crfm.stanford.edu/helm/medhelm/latest/
- **HELM GitHub Issues**: https://github.com/stanford-crfm/helm/issues
- **AWS Support**: For infrastructure issues

## Cost Optimization

### Estimated Costs

Approximate monthly costs (us-east-1):

| Component | Configuration | Cost/Month |
|-----------|--------------|------------|
| Code Editor (ml.t3.medium) | 8 hrs/day, 20 days | ~$50 |
| Code Editor (ml.m5.large) | 8 hrs/day, 20 days | ~$100 |
| EFS Storage | 10 GB | ~$3 |
| Data Transfer | 100 GB | ~$9 |

**Total**: $60-120/month (depending on usage)

### Cost Reduction Tips

1. **Stop Code Editor When Not in Use**:
   - Code Editor auto-saves
   - Stop app to avoid compute charges
   - Storage persists

2. **Use Spot Instances** (for training):
   - Not applicable to Code Editor
   - Use for batch evaluations

3. **Choose Appropriate Instance Sizes**:
   - Start with `ml.t3.medium`
   - Scale up only if needed
   - Monitor utilization

4. **Clean Up Unused Data**:
   ```bash
   # Remove old benchmark outputs
   rm -rf ~/benchmark_output/old-suite
   
   # Clear cache
   rm -rf ~/.cache/helm
   ```

5. **Set Up Budget Alerts**:
   - AWS Budgets → Create budget
   - Set threshold (e.g., $100/month)
   - Receive email alerts

## Security Considerations

### IAM Best Practices

1. **Least Privilege**:
   - Review execution role permissions
   - Remove unnecessary policies
   - Use condition keys where applicable

2. **API Key Management**:
   - Never commit API keys to git
   - Use AWS Secrets Manager for production
   - Rotate keys regularly

3. **Network Security**:
   - Use VPC mode (already configured)
   - Restrict security group rules
   - Use private subnets with NAT

### Data Protection

1. **Sensitive Data**:
   - Do not use real patient data without proper authorization
   - Use de-identified or synthetic data
   - Follow HIPAA compliance if applicable

2. **Encryption**:
   - EFS volumes encrypted at rest (SageMaker default)
   - Use SSL/TLS for API calls
   - Enable CloudTrail logging

3. **Access Control**:
   - Use IAM authentication
   - Implement MFA for console access
   - Regular access reviews

### Compliance

For healthcare applications:

- **HIPAA**: Ensure BAA with AWS if handling PHI
- **GDPR**: Implement data retention policies
- **SOC 2**: Use appropriate AWS services
- **HITRUST**: Follow framework requirements

## Cleanup

To avoid ongoing charges:

### Option 1: Delete via Console

1. Go to CloudFormation Console
2. Select the stack
3. Click "Delete"
4. Confirm deletion

### Option 2: Delete via CLI

```bash
aws cloudformation delete-stack \
  --stack-name medhelm-workshop-stack \
  --region us-east-1

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name medhelm-workshop-stack \
  --region us-east-1
```

### Manual Cleanup (if needed)

If stack deletion fails:

1. Delete SageMaker apps manually
2. Delete user profiles
3. Delete domain
4. Delete security groups
5. Retry stack deletion

## Additional Resources

- **MedHELM Paper**: https://arxiv.org/abs/2505.23802
- **HELM Documentation**: https://crfm.stanford.edu/helm/
- **SageMaker Documentation**: https://docs.aws.amazon.com/sagemaker/
- **AWS CloudFormation**: https://docs.aws.amazon.com/cloudformation/

## Support

For issues specific to:
- **MedHELM/HELM**: Open issue on GitHub
- **AWS Infrastructure**: Contact AWS Support
- **This Template**: Check troubleshooting section above

---

**Last Updated**: December 2024
**Template Version**: 1.0.0
