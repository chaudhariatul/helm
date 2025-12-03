# MedHELM SageMaker Workshop - CloudFormation Deployment

This repository now includes a **production-ready CloudFormation template** for deploying a complete MedHELM workshop environment on AWS SageMaker.

## 📦 What's Included

Located in the `cloudformation/` directory:

- **CloudFormation Template** - Automated AWS infrastructure deployment
- **Workshop Notebooks** - 4 interactive Jupyter notebooks for learning MedHELM
- **Comprehensive Documentation** - Deployment guides, architecture overview, troubleshooting
- **Helper Scripts** - Validation and upload utilities

## 🚀 Quick Start

### 1. Navigate to CloudFormation Directory

```bash
cd cloudformation/
```

### 2. Review Documentation

- **README.md** - Quick start guide (start here!)
- **DEPLOYMENT_GUIDE.md** - Detailed deployment instructions
- **OVERVIEW.md** - Architecture and design details
- **CHECKLIST.md** - Step-by-step deployment checklist

### 3. Deploy to AWS

**Option A: AWS Console**
1. Open AWS CloudFormation Console
2. Create Stack → Upload `sagemaker-medhelm-domain.yaml`
3. Fill in parameters (VPC ID, Subnet IDs)
4. Create stack (~15 minutes)

**Option B: AWS CLI**
```bash
aws cloudformation create-stack \
  --stack-name medhelm-workshop \
  --template-body file://sagemaker-medhelm-domain.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-xxxxx \
    ParameterKey=SubnetIds,ParameterValue="subnet-xxxxx" \
  --capabilities CAPABILITY_NAMED_IAM
```

### 4. Access Your Environment

1. SageMaker Console → Domains
2. Select your domain → User profile
3. Launch → Code Editor
4. Upload workshop notebooks
5. Start learning!

## 🎯 What Gets Deployed

### Infrastructure
- ✅ SageMaker Domain with Code Editor
- ✅ IAM Execution Role with scoped permissions
- ✅ VPC Security Group with proper rules
- ✅ Automated lifecycle configuration

### Pre-installed Software
- ✅ Python 3.10 (MedHELM requirement)
- ✅ uv package manager
- ✅ pip, boto3, sagemaker (upgraded)
- ✅ crfm-helm[summarization,medhelm]
- ✅ Google Cloud SDK (gcloud)
- ✅ HELM repository (cloned)

### Workshop Materials
- ✅ 4 comprehensive Jupyter notebooks
- ✅ Environment verification scripts
- ✅ Pre-configured directory structure
- ✅ Sample evaluation examples

## 📚 Workshop Notebooks

1. **Introduction** - Setup verification and MedHELM overview
2. **Tiny Evaluation** - Run your first evaluation (10 instances)
3. **Exploring Scenarios** - MedHELM taxonomy and scenarios
4. **Custom Benchmarks** - Create custom evaluations

## 💰 Cost Estimate

**Typical Workshop Usage** (8 hrs/day, 20 days/month):
- Compute (ml.t3.medium): ~$50/month
- Storage (EFS): ~$5/month
- **Total**: ~$60/month

**Tip**: Stop Code Editor when not in use to reduce costs.

## 📖 Documentation Structure

```
cloudformation/
├── README.md                    ← Start here
├── DEPLOYMENT_GUIDE.md          ← Detailed instructions
├── OVERVIEW.md                  ← Architecture details
├── CHECKLIST.md                 ← Deployment checklist
├── FILE_STRUCTURE.txt           ← Visual file guide
└── SUMMARY.txt                  ← Package summary
```

## 🔒 Security Features

- VPC-only network access
- IAM authentication (no SSO required)
- Scoped IAM permissions
- Security group with self-referencing rules
- No hardcoded credentials
- CloudTrail integration

## 📋 Prerequisites

- AWS Account with appropriate permissions
- VPC with internet connectivity (NAT Gateway recommended)
- At least one subnet
- Basic familiarity with CloudFormation (helpful but not required)

## 🆘 Support

- **Deployment Issues**: See `cloudformation/DEPLOYMENT_GUIDE.md`
- **MedHELM Questions**: GitHub Issues (this repository)
- **AWS Infrastructure**: AWS Support Center

## 🔗 Resources

- **MedHELM Documentation**: https://crfm.stanford.edu/helm/medhelm/latest/
- **HELM GitHub**: https://github.com/stanford-crfm/helm
- **MedHELM Paper**: https://arxiv.org/abs/2505.23802
- **Stanford CRFM**: https://crfm.stanford.edu/

## ⚡ Features

- ✅ **Production-Ready**: Parameterized, secure, well-documented
- ✅ **Fully Automated**: Zero manual configuration required
- ✅ **Cost-Optimized**: Configurable instances, auto-scaling storage
- ✅ **Comprehensive**: Complete workshop environment in one deployment
- ✅ **Educational**: 4 interactive notebooks with examples

## 🎓 Learning Path

1. Deploy CloudFormation stack (15 minutes)
2. Access Code Editor (5 minutes)
3. Complete workshop notebooks (2-3 hours)
4. Run custom evaluations
5. Compare models on medical tasks

## 📊 Perfect For

- **Training Sessions** - Teach medical LLM evaluation
- **Proof of Concept** - Test MedHELM quickly
- **Research** - Academic medical AI research
- **Development** - Build custom medical benchmarks

## 🚀 Get Started Now

```bash
cd cloudformation/
cat README.md  # Read the quick start guide
```

Then deploy and start evaluating medical LLMs in under 30 minutes!

---

**Version**: 1.0.0  
**Created**: December 2024  
**License**: See repository LICENSE file

For detailed information, see the `cloudformation/` directory.
