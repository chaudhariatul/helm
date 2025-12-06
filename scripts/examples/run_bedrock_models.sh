#!/bin/bash

# Example script for running HELM benchmarks with AWS Bedrock models
# This demonstrates the correct way to set the AWS_REGION environment variable

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}HELM Bedrock Model Runner${NC}"
echo "================================"
echo ""

# Check if AWS credentials are configured
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}Warning: AWS CLI not found. Credentials will be checked using boto3.${NC}"
else
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}Error: AWS credentials are not configured or invalid.${NC}"
        echo "Please configure your AWS credentials using one of these methods:"
        echo "  1. Run 'aws configure' to set up AWS CLI credentials"
        echo "  2. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
        echo "  3. Use an IAM role (if running on EC2)"
        exit 1
    fi
    echo -e "${GREEN}✓ AWS credentials verified${NC}"
fi

# Set default region if not already set
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    echo -e "${YELLOW}No AWS region set. Using default: us-west-2${NC}"
    export AWS_REGION=us-west-2
else
    echo -e "${GREEN}✓ AWS region: ${AWS_REGION:-$AWS_DEFAULT_REGION}${NC}"
fi

echo ""
echo "================================"
echo ""

# Function to run a benchmark
run_benchmark() {
    local model=$1
    local subject=$2
    local max_instances=${3:-5}
    
    echo -e "${GREEN}Running benchmark:${NC}"
    echo "  Model: $model"
    echo "  Subject: $subject"
    echo "  Max instances: $max_instances"
    echo ""
    
    helm-run \
        --run-entries "mmlu:subject=$subject,model=$model" \
        --suite quick-test \
        --max-eval-instances "$max_instances"
}

# Main execution
# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [model] [subject] [max_instances]"
    echo ""
    echo "Examples:"
    echo "  $0 amazon/nova-pro-v1:0 clinical_knowledge 5"
    echo "  $0 amazon/nova-lite-v1:0 anatomy 10"
    echo "  $0 amazon/titan-text-express-v1 high_school_biology 3"
    echo ""
    echo "Running default example..."
    echo ""
    run_benchmark "amazon/nova-pro-v1:0" "clinical_knowledge" 5
else
    MODEL=${1:-amazon/nova-pro-v1:0}
    SUBJECT=${2:-clinical_knowledge}
    MAX_INSTANCES=${3:-5}
    
    run_benchmark "$MODEL" "$SUBJECT" "$MAX_INSTANCES"
fi

echo ""
echo -e "${GREEN}Benchmark completed!${NC}"
