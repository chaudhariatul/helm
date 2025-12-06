#!/bin/bash
# Test script to verify Amazon Nova inference profile fix

set -e

echo "============================================================"
echo "Amazon Nova Inference Profile Fix - Verification Test"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Test 1: Check model_deployments.yaml configuration"
echo "---------------------------------------------------"

for model in "nova-pro-v1:0" "nova-lite-v1:0" "nova-micro-v1:0"; do
    echo -n "Checking amazon/${model}... "
    if grep -A 8 "name: amazon/${model}" src/helm/config/model_deployments.yaml | grep -q "bedrock_model_id: us.amazon.${model}"; then
        echo -e "${GREEN}✓ PASS${NC} - Using inference profile ID"
    else
        echo -e "${RED}✗ FAIL${NC} - Not using inference profile ID"
        exit 1
    fi
done

echo ""
echo "Test 2: Verify AWS environment configuration"
echo "---------------------------------------------"

# Check AWS region
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - No AWS region set"
    echo "Setting AWS_REGION=us-west-2 for testing..."
    export AWS_REGION=us-west-2
else
    REGION=${AWS_REGION:-$AWS_DEFAULT_REGION}
    echo -e "${GREEN}✓ PASS${NC} - AWS region set to: $REGION"
fi

# Check AWS credentials (optional - don't fail if not configured)
echo -n "Checking AWS credentials... "
if command -v aws >/dev/null 2>&1 && aws sts get-caller-identity >/dev/null 2>&1; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}✓ PASS${NC} - AWS credentials configured (Account: $ACCOUNT_ID)"
    CREDS_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ SKIP${NC} - AWS credentials not configured (run 'aws configure')"
    CREDS_AVAILABLE=false
fi

echo ""
echo "Test 3: Verify BedrockNovaClient supports bedrock_model_id"
echo "-----------------------------------------------------------"

if grep -q "bedrock_model_id: Optional\[str\] = None" src/helm/clients/bedrock_client.py; then
    echo -e "${GREEN}✓ PASS${NC} - BedrockNovaClient accepts bedrock_model_id parameter"
else
    echo -e "${RED}✗ FAIL${NC} - BedrockNovaClient missing bedrock_model_id parameter"
    exit 1
fi

if grep -q '"modelId": self.bedrock_model_id or model_id' src/helm/clients/bedrock_client.py; then
    echo -e "${GREEN}✓ PASS${NC} - BedrockNovaClient uses bedrock_model_id when provided"
else
    echo -e "${RED}✗ FAIL${NC} - BedrockNovaClient not using bedrock_model_id"
    exit 1
fi

echo ""
echo "Test 4: Configuration details"
echo "------------------------------"

echo ""
echo "Nova Pro configuration:"
grep -A 8 "name: amazon/nova-pro-v1:0" src/helm/config/model_deployments.yaml | grep -A 3 "client_spec:"

echo ""
echo "============================================================"
echo -e "${GREEN}✓ All configuration tests passed!${NC}"
echo "============================================================"
echo ""

if [ "$CREDS_AVAILABLE" = true ]; then
    echo "Next steps:"
    echo "  1. Run a quick test:"
    echo "     AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5"
    echo ""
    echo "  2. Or use the convenience script:"
    echo "     ./scripts/examples/run_bedrock_models.sh amazon/nova-pro-v1:0 clinical_knowledge 5"
else
    echo "To test with actual AWS calls:"
    echo "  1. Configure AWS credentials:"
    echo "     aws configure"
    echo ""
    echo "  2. Then run a benchmark:"
    echo "     AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5"
fi

echo ""
echo "For more information, see:"
echo "  - AWS_NOVA_INFERENCE_PROFILE_FIX.md - Complete fix documentation"
echo "  - AWS_BEDROCK_FIX.md - Region configuration fix"
echo ""
