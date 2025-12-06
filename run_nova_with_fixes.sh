#!/bin/bash
# Convenience script to run HELM with Amazon Nova models
# This script applies both fixes:
#   1. Proper AWS_REGION configuration (no ! prefix)
#   2. Automatic inference profile usage (configured in model_deployments.yaml)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}HELM Amazon Nova Benchmark Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse arguments
MODEL=${1:-amazon/nova-pro-v1:0}
SUBJECT=${2:-clinical_knowledge}
MAX_INSTANCES=${3:-5}
REGION=${AWS_REGION:-us-west-2}

# Display configuration
echo "Configuration:"
echo "  Model:         $MODEL"
echo "  Subject:       $SUBJECT"
echo "  Max Instances: $MAX_INSTANCES"
echo "  AWS Region:    $REGION"
echo ""

# Check AWS credentials
echo -n "Checking AWS credentials... "
if ! command -v aws >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ WARNING${NC} - AWS CLI not installed"
    echo "Continuing anyway (boto3 may use other credential methods)"
elif ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo -e "${RED}✗ FAILED${NC}"
    echo ""
    echo "AWS credentials not configured. Please run:"
    echo "  aws configure"
    echo ""
    echo "Or set environment variables:"
    echo "  export AWS_ACCESS_KEY_ID=your_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret"
    exit 1
else
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    echo -e "${GREEN}✓ OK${NC} (Account: $ACCOUNT_ID)"
fi

# Set AWS region
echo -n "Setting AWS region... "
export AWS_REGION=$REGION
echo -e "${GREEN}✓ OK${NC} (Region: $AWS_REGION)"
echo ""

# Show which inference profile will be used
echo -e "${BLUE}Inference Profile Information:${NC}"
case $MODEL in
    amazon/nova-pro-v1:0)
        echo "  Using inference profile: us.amazon.nova-pro-v1:0"
        ;;
    amazon/nova-lite-v1:0)
        echo "  Using inference profile: us.amazon.nova-lite-v1:0"
        ;;
    amazon/nova-micro-v1:0)
        echo "  Using inference profile: us.amazon.nova-micro-v1:0"
        ;;
    *)
        echo "  Model: $MODEL"
        ;;
esac
echo ""

# Display the command being run
echo -e "${BLUE}Running Command:${NC}"
echo "  helm-run --run-entries mmlu:subject=$SUBJECT,model=$MODEL --suite quick-test --max-eval-instances $MAX_INSTANCES"
echo ""
echo "Press Ctrl+C to cancel..."
sleep 2

# Run HELM
helm-run --run-entries mmlu:subject=$SUBJECT,model=$MODEL --suite quick-test --max-eval-instances $MAX_INSTANCES

echo ""
echo -e "${GREEN}✓ Benchmark completed successfully!${NC}"
