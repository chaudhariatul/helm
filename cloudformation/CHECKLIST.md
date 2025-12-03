# MedHELM SageMaker Deployment Checklist

Use this checklist to ensure successful deployment of your MedHELM workshop environment.

## Pre-Deployment Checklist

### AWS Account Setup
- [ ] AWS account with admin access (or CloudFormation/SageMaker/IAM permissions)
- [ ] AWS CLI installed and configured (optional, for CLI deployment)
- [ ] Appropriate AWS region selected (e.g., us-east-1, us-west-2)

### Network Prerequisites
- [ ] VPC exists in target region
- [ ] VPC has internet connectivity:
  - [ ] Option A: NAT Gateway in private subnet (recommended)
  - [ ] Option B: Internet Gateway for public subnet
- [ ] At least one subnet available
- [ ] Subnet routing table allows outbound traffic

### Service Quotas
- [ ] SageMaker domains quota (default: 1 per region)
- [ ] SageMaker notebooks quota (default: varies by instance type)
- [ ] VPC security groups quota

### Cost Management
- [ ] Budget alerts configured (recommended: $100/month threshold)
- [ ] Cost allocation tags enabled
- [ ] Understand pricing (see OVERVIEW.md for estimates)

## Deployment Checklist

### Prepare Parameters
- [ ] VPC ID identified: `vpc-_________________`
- [ ] Subnet ID(s) identified: `subnet-_________________`
- [ ] Domain name decided (default: `medhelm-workshop-domain`)
- [ ] User profile name decided (default: `medhelm-user`)
- [ ] Instance type selected (default: `ml.t3.medium`)

### Deploy CloudFormation Stack

#### Option 1: AWS Console
- [ ] Navigate to CloudFormation Console
- [ ] Click "Create stack" → "With new resources"
- [ ] Upload `sagemaker-medhelm-domain.yaml`
- [ ] Enter stack name: `___________________`
- [ ] Fill in all required parameters
- [ ] Add tags (optional but recommended):
  - [ ] `Project: MedHELM`
  - [ ] `Environment: Workshop`
- [ ] Acknowledge IAM resource creation
- [ ] Click "Create stack"

#### Option 2: AWS CLI
- [ ] Template file location verified
- [ ] Parameters file prepared (optional)
- [ ] Command prepared with correct values
- [ ] Run deployment command
- [ ] Monitor stack creation

### Monitor Deployment
- [ ] Stack creation started (status: CREATE_IN_PROGRESS)
- [ ] Monitor "Events" tab for progress
- [ ] Wait for completion (~15 minutes)
- [ ] Stack status: CREATE_COMPLETE
- [ ] Review "Outputs" tab for resource ARNs

### Verify Deployment
- [ ] Navigate to SageMaker Console
- [ ] Verify domain exists in "Domains" section
- [ ] Verify user profile exists
- [ ] Check security group created
- [ ] Check IAM role created

## Post-Deployment Checklist

### First Access
- [ ] Navigate to SageMaker Console → Domains
- [ ] Click on domain name
- [ ] Click on user profile name
- [ ] Click "Launch" → "Code Editor"
- [ ] Wait for Code Editor to launch (3-5 minutes on first launch)
- [ ] Code Editor opens successfully

### Environment Verification
- [ ] Open terminal in Code Editor
- [ ] Run verification script: `./verify_setup.sh`
- [ ] Check Python version: `python --version` (should be 3.10.x)
- [ ] Check virtual environment exists: `ls -la ~/medhelm-env/`
- [ ] Activate environment: `source ~/medhelm-env/bin/activate`
- [ ] Verify HELM installed: `helm-run --help`
- [ ] Verify boto3 installed: `python -c "import boto3; print(boto3.__version__)"`
- [ ] Verify sagemaker installed: `python -c "import sagemaker; print(sagemaker.__version__)"`
- [ ] Check gcloud installed: `gcloud --version`
- [ ] Check uv installed: `uv --version`

### Directory Structure
- [ ] HELM repository exists: `ls -la ~/helm/`
- [ ] Benchmark output directory exists: `ls -la ~/benchmark_output/`
- [ ] Workshop notebooks directory exists: `ls -la ~/workshop-notebooks/`
- [ ] README exists: `ls -la ~/README_MEDHELM.md`

### Upload Workshop Notebooks
- [ ] Create directory (if not exists): `mkdir -p ~/workshop-notebooks`
- [ ] Upload notebook 1: `workshop-notebook-1-introduction.ipynb`
- [ ] Upload notebook 2: `workshop-notebook-2-tiny-evaluation.ipynb`
- [ ] Upload notebook 3: `workshop-notebook-3-scenarios.ipynb`
- [ ] Upload notebook 4: `workshop-notebook-4-custom-benchmarks.ipynb`

### Configure API Keys (if needed)
- [ ] OpenAI API key set (if using OpenAI models)
  ```bash
  export OPENAI_API_KEY="your-key"
  echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
  ```
- [ ] Anthropic API key set (if using Anthropic models)
  ```bash
  export ANTHROPIC_API_KEY="your-key"
  echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
  ```
- [ ] Other API keys as needed

### Google Cloud SDK Configuration (Optional)
- [ ] Authenticate gcloud (for private buckets): `gcloud auth login`
- [ ] Or disable auth (for public buckets): `gcloud config set auth/disable_credentials true`
- [ ] Test access: `gsutil ls gs://crfm-helm-public/medhelm/`

## First Evaluation Checklist

### Setup
- [ ] Activate virtual environment: `source ~/medhelm-env/bin/activate`
- [ ] Navigate to work directory: `cd ~`
- [ ] Verify API keys are set (if using commercial models)

### Run Tiny Evaluation
- [ ] Set environment variables:
  ```bash
  export OUTPUT_PATH="./benchmark_output"
  export RUN_ENTRIES="pubmed_qa:model=openai/gpt-3.5-turbo"
  export SUITE="test-suite"
  export MAX_EVAL_INSTANCES=10
  ```
- [ ] Run evaluation:
  ```bash
  helm-run \
    --run-entries $RUN_ENTRIES \
    --suite $SUITE \
    --max-eval-instances $MAX_EVAL_INSTANCES \
    --output-path $OUTPUT_PATH
  ```
- [ ] Evaluation completes without errors
- [ ] Results generated in `~/benchmark_output/runs/test-suite/`

### Create Summary
- [ ] Download schema (if not exists):
  ```bash
  wget -O schema_medhelm.yaml \
    https://raw.githubusercontent.com/stanford-crfm/helm/v0.5.7/src/helm/benchmark/static/schema_medhelm.yaml
  ```
- [ ] Run summarization:
  ```bash
  helm-summarize \
    --suite $SUITE \
    --schema schema_medhelm.yaml \
    --output-path $OUTPUT_PATH
  ```
- [ ] Summary completes without errors

### View Results
- [ ] Launch server:
  ```bash
  helm-server \
    --suite $SUITE \
    --output-path $OUTPUT_PATH
  ```
- [ ] Note the URL displayed
- [ ] Access leaderboard in browser
- [ ] Results display correctly

## Workshop Readiness Checklist

### For Workshop Facilitator
- [ ] All notebooks uploaded and tested
- [ ] Example evaluations run successfully
- [ ] API keys prepared for participants (if shared)
- [ ] Workshop agenda prepared
- [ ] Troubleshooting guide reviewed
- [ ] Backup instance type identified (in case of capacity issues)

### For Workshop Participants
- [ ] AWS access credentials provided
- [ ] Workshop notebook links shared
- [ ] API keys distributed (if applicable)
- [ ] Introduction materials prepared
- [ ] Support contact information shared

## Troubleshooting Checklist

### If Lifecycle Configuration Fails
- [ ] Check log: `cat /var/log/lifecycle-config.log`
- [ ] Check internet connectivity from Code Editor
- [ ] Verify NAT Gateway is working
- [ ] Re-run installations manually if needed

### If helm-run Not Found
- [ ] Check if virtual environment exists: `ls ~/medhelm-env/`
- [ ] Activate environment: `source ~/medhelm-env/bin/activate`
- [ ] Check PATH: `echo $PATH`
- [ ] Reinstall if needed: `pip install crfm-helm`

### If gcloud Not Working
- [ ] Check installation: `which gcloud`
- [ ] Check PATH: `echo $PATH | grep google-cloud-sdk`
- [ ] Reinstall if needed (see lifecycle script)

### If Out of Memory
- [ ] Stop Code Editor
- [ ] Update stack with larger instance type
- [ ] Restart Code Editor
- [ ] Or reduce max-eval-instances in evaluations

## Cleanup Checklist

### When Done with Workshop
- [ ] Save any important results to S3
- [ ] Export notebooks if modified
- [ ] Note any custom configurations
- [ ] Stop Code Editor application

### To Reduce Costs
- [ ] Stop Code Editor when not in use (data persists)
- [ ] Clean up old benchmark outputs: `rm -rf ~/benchmark_output/old-suite/`
- [ ] Clear cache: `rm -rf ~/.cache/helm/`

### To Delete Everything
- [ ] Backup any important data
- [ ] Navigate to CloudFormation Console
- [ ] Select stack
- [ ] Click "Delete"
- [ ] Confirm deletion
- [ ] Wait for DELETE_COMPLETE status
- [ ] Verify all resources deleted

## Reference Documentation

- [ ] Read `README.md` for quick start
- [ ] Review `DEPLOYMENT_GUIDE.md` for details
- [ ] Check `OVERVIEW.md` for architecture
- [ ] Consult `SUMMARY.txt` for package info

## Support Resources

- [ ] Bookmark MedHELM docs: https://crfm.stanford.edu/helm/medhelm/latest/
- [ ] Bookmark HELM GitHub: https://github.com/stanford-crfm/helm
- [ ] Note AWS Support contact information
- [ ] Join HELM community discussions (if available)

---

**Tip**: Print this checklist or keep it open during deployment to track progress.

**Completion Time**: 
- Pre-deployment: 15-30 minutes
- Deployment: 15-20 minutes
- Post-deployment: 15-30 minutes
- First evaluation: 5-10 minutes
- **Total**: ~1 hour for complete setup

---

**Version**: 1.0.0
**Last Updated**: December 2024
