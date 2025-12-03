#!/bin/bash
# Script to validate the CloudFormation template

set -e

TEMPLATE_FILE="sagemaker-medhelm-domain.yaml"

echo "=========================================="
echo "CloudFormation Template Validation"
echo "=========================================="
echo ""

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file not found: $TEMPLATE_FILE"
    exit 1
fi

echo "Validating template: $TEMPLATE_FILE"
echo ""

# Validate with AWS CLI
if command -v aws &> /dev/null; then
    echo "Running AWS CloudFormation validation..."
    if aws cloudformation validate-template --template-body "file://${TEMPLATE_FILE}" > /dev/null 2>&1; then
        echo "✓ Template is valid!"
        
        # Show template summary
        echo ""
        echo "Template Summary:"
        aws cloudformation validate-template --template-body "file://${TEMPLATE_FILE}" --query '{Description:Description,Parameters:Parameters[*].ParameterKey}' --output table
    else
        echo "✗ Template validation failed!"
        aws cloudformation validate-template --template-body "file://${TEMPLATE_FILE}"
        exit 1
    fi
else
    echo "Warning: AWS CLI not found. Skipping AWS validation."
    echo "Install AWS CLI for full validation: https://aws.amazon.com/cli/"
fi

echo ""
echo "=========================================="
echo "Template Structure Check"
echo "=========================================="
echo ""

# Check for required sections
required_sections=("AWSTemplateFormatVersion" "Description" "Parameters" "Resources" "Outputs")
for section in "${required_sections[@]}"; do
    if grep -q "^${section}:" "$TEMPLATE_FILE"; then
        echo "✓ $section section found"
    else
        echo "✗ $section section missing"
    fi
done

echo ""
echo "=========================================="
echo "Resources Count"
echo "=========================================="
echo ""

# Count resources
resource_count=$(grep -c "^  [A-Z].*:$" "$TEMPLATE_FILE" || true)
echo "Total resources defined: $resource_count"

# List resource types
echo ""
echo "Resource types:"
grep "Type: AWS::" "$TEMPLATE_FILE" | sed 's/^[ \t]*/  /' | sort | uniq -c

echo ""
echo "Validation complete!"
