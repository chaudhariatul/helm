#!/usr/bin/env python3
"""
Example script demonstrating how to use HELM with AWS Bedrock models programmatically.

This script shows:
1. How to properly configure AWS region for Bedrock models
2. How to use the Bedrock client directly
3. Common pitfalls and solutions

Usage:
    # Set region via environment variable
    AWS_REGION=us-west-2 python bedrock_client_usage.py
    
    # Or export first
    export AWS_REGION=us-west-2
    python bedrock_client_usage.py
"""

import os
import sys


def check_aws_configuration():
    """Check if AWS credentials and region are properly configured."""
    print("Checking AWS configuration...")
    print("-" * 50)
    
    # Check for AWS credentials
    has_access_key = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
    has_secret_key = bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
    has_profile = bool(os.environ.get("AWS_PROFILE"))
    
    print(f"AWS_ACCESS_KEY_ID set: {has_access_key}")
    print(f"AWS_SECRET_ACCESS_KEY set: {has_secret_key}")
    print(f"AWS_PROFILE set: {has_profile}")
    
    # Check for region configuration
    aws_region = os.environ.get("AWS_REGION")
    aws_default_region = os.environ.get("AWS_DEFAULT_REGION")
    
    print(f"AWS_REGION: {aws_region or 'Not set'}")
    print(f"AWS_DEFAULT_REGION: {aws_default_region or 'Not set'}")
    print("-" * 50)
    
    # Determine if configuration is valid
    has_credentials = has_access_key and has_secret_key or has_profile
    has_region = aws_region or aws_default_region
    
    if not has_credentials:
        print("\n❌ WARNING: AWS credentials not found!")
        print("   Configure credentials using one of these methods:")
        print("   1. Run 'aws configure'")
        print("   2. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("   3. Use AWS_PROFILE environment variable with configured profile")
        print()
    
    if not has_region:
        print("\n❌ ERROR: AWS region not configured!")
        print("   You must set AWS_REGION or AWS_DEFAULT_REGION:")
        print("   - export AWS_REGION=us-west-2")
        print("   - or run: AWS_REGION=us-west-2 python script.py")
        print()
        print("   Common regions for Bedrock:")
        print("   - us-east-1 (US East - N. Virginia)")
        print("   - us-west-2 (US West - Oregon)")
        print("   - eu-central-1 (Europe - Frankfurt)")
        print()
        return False
    
    print("\n✓ Configuration looks good!")
    print(f"  Using region: {aws_region or aws_default_region}")
    return True


def demonstrate_bedrock_client_creation():
    """Demonstrate how to create a Bedrock client with proper region configuration."""
    print("\n" + "=" * 50)
    print("Creating Bedrock Client")
    print("=" * 50)
    
    try:
        from helm.clients.bedrock_utils import get_bedrock_client, get_bedrock_client_v1
        
        # Method 1: Using get_bedrock_client (for older Bedrock models)
        print("\n1. Creating client with get_bedrock_client()...")
        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
        
        if region:
            try:
                client = get_bedrock_client(region=region)
                print(f"   ✓ Client created successfully for region: {region}")
                print(f"   Endpoint: {client._endpoint}")
            except Exception as e:
                print(f"   ❌ Error creating client: {e}")
        
        # Method 2: Using get_bedrock_client_v1 (for Nova and newer models)
        print("\n2. Creating client with get_bedrock_client_v1()...")
        if region:
            try:
                client_v1 = get_bedrock_client_v1(region=region)
                print(f"   ✓ Client created successfully for region: {region}")
            except Exception as e:
                print(f"   ❌ Error creating client: {e}")
        
    except ImportError as e:
        print(f"\n❌ Could not import Bedrock utilities: {e}")
        print("   Make sure you have installed the AWS dependencies:")
        print("   pip install boto3 botocore")


def show_common_errors():
    """Show common errors and their solutions."""
    print("\n" + "=" * 50)
    print("Common Errors and Solutions")
    print("=" * 50)
    
    print("""
1. botocore.exceptions.NoRegionError: You must specify a region.
   
   CAUSE: AWS_REGION or AWS_DEFAULT_REGION environment variable not set.
   
   SOLUTION:
   ✓ export AWS_REGION=us-west-2
   ✓ AWS_REGION=us-west-2 helm-run ...
   ✗ !AWS_REGION=us-west-2 helm-run ...  (WRONG - don't use ! prefix)

2. botocore.exceptions.NoCredentialsError: Unable to locate credentials
   
   CAUSE: AWS credentials not configured.
   
   SOLUTION:
   - Run 'aws configure' and enter your credentials
   - Or set environment variables:
     export AWS_ACCESS_KEY_ID=your_key
     export AWS_SECRET_ACCESS_KEY=your_secret

3. botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
   
   CAUSE: IAM permissions insufficient for Bedrock access.
   
   SOLUTION:
   - Ensure your IAM user/role has bedrock:InvokeModel permission
   - Policy example: AmazonBedrockFullAccess or custom policy

4. Model not available in region
   
   CAUSE: Not all Bedrock models are available in all regions.
   
   SOLUTION:
   - Check model availability: https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html
   - Try a different region (us-west-2 has most models)
""")


def show_correct_command_examples():
    """Show correct command examples for running HELM with Bedrock models."""
    print("\n" + "=" * 50)
    print("Correct Command Examples")
    print("=" * 50)
    
    print("""
# Method 1: Export region first (recommended for multiple commands)
export AWS_REGION=us-west-2
helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Method 2: Inline environment variable (for single command)
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Method 3: Using env command
env AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Example with different models:

# Amazon Nova Pro (latest)
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=anatomy,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

# Amazon Nova Lite
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=high_school_biology,model=amazon/nova-lite-v1:0 --suite quick-test --max-eval-instances 5

# Amazon Titan Text Express
AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=computer_science,model=amazon/titan-text-express-v1 --suite quick-test --max-eval-instances 5

# Using the convenience script
./scripts/examples/run_bedrock_models.sh amazon/nova-pro-v1:0 clinical_knowledge 5
""")


def main():
    """Main function."""
    print("=" * 50)
    print("HELM AWS Bedrock Configuration Guide")
    print("=" * 50)
    
    # Check configuration
    is_configured = check_aws_configuration()
    
    # If properly configured, demonstrate client creation
    if is_configured:
        demonstrate_bedrock_client_creation()
    
    # Show common errors
    show_common_errors()
    
    # Show correct command examples
    show_correct_command_examples()
    
    print("\n" + "=" * 50)
    print("For more information, see: docs/credentials.md")
    print("=" * 50)


if __name__ == "__main__":
    main()
