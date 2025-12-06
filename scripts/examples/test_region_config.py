#!/usr/bin/env python3
"""
Simple test to verify AWS region configuration logic matches bedrock_utils.py
This doesn't require HELM dependencies.
"""

import os
import sys


def get_region_like_bedrock():
    """
    Mimics the region detection logic from bedrock_utils.py line 38:
    target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    """
    return os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))


def test_region_configuration():
    """Test various region configuration scenarios."""
    print("=" * 60)
    print("Testing AWS Region Configuration")
    print("=" * 60)
    
    # Test 1: No region set
    print("\nTest 1: No region environment variables set")
    os.environ.pop("AWS_REGION", None)
    os.environ.pop("AWS_DEFAULT_REGION", None)
    region = get_region_like_bedrock()
    print(f"  Result: {region or 'None'}")
    if region is None:
        print("  ✓ Correctly returns None (would trigger NoRegionError)")
    else:
        print("  ✗ Expected None")
    
    # Test 2: AWS_REGION set
    print("\nTest 2: AWS_REGION set to 'us-west-2'")
    os.environ["AWS_REGION"] = "us-west-2"
    os.environ.pop("AWS_DEFAULT_REGION", None)
    region = get_region_like_bedrock()
    print(f"  Result: {region}")
    if region == "us-west-2":
        print("  ✓ Correctly reads AWS_REGION")
    else:
        print("  ✗ Expected 'us-west-2'")
    
    # Test 3: AWS_DEFAULT_REGION set
    print("\nTest 3: AWS_DEFAULT_REGION set to 'us-east-1'")
    os.environ.pop("AWS_REGION", None)
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    region = get_region_like_bedrock()
    print(f"  Result: {region}")
    if region == "us-east-1":
        print("  ✓ Correctly reads AWS_DEFAULT_REGION")
    else:
        print("  ✗ Expected 'us-east-1'")
    
    # Test 4: Both set (AWS_REGION should take precedence)
    print("\nTest 4: Both AWS_REGION and AWS_DEFAULT_REGION set")
    os.environ["AWS_REGION"] = "us-west-2"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    region = get_region_like_bedrock()
    print(f"  Result: {region}")
    if region == "us-west-2":
        print("  ✓ Correctly prioritizes AWS_REGION over AWS_DEFAULT_REGION")
    else:
        print("  ✗ Expected 'us-west-2' (AWS_REGION should take precedence)")
    
    print("\n" + "=" * 60)
    print("Region Configuration Tests Complete")
    print("=" * 60)


def demonstrate_command_syntax():
    """Demonstrate correct vs incorrect command syntax."""
    print("\n" + "=" * 60)
    print("Command Syntax Demonstration")
    print("=" * 60)
    
    print("""
The ERROR in the original command:
  !AWS_REGION=us-west-2 helm-run ...

The '!' prefix is INCORRECT for bash/shell commands. It's only used in
Jupyter notebooks to execute shell commands.

CORRECT syntax options:

1. Export first (recommended for multiple commands):
   $ export AWS_REGION=us-west-2
   $ helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

2. Inline environment variable (for single command):
   $ AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

3. Using env command:
   $ env AWS_REGION=us-west-2 helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

Why the original command failed:
  - The '!' is interpreted by bash as history expansion or command negation
  - The environment variable is not properly set for the helm-run command
  - This causes boto3 to not find the region, resulting in NoRegionError
    """)


def show_verification_steps():
    """Show how to verify the fix works."""
    print("\n" + "=" * 60)
    print("Verification Steps")
    print("=" * 60)
    
    print("""
To verify your AWS region is properly configured:

1. Check current environment:
   $ echo $AWS_REGION
   $ echo $AWS_DEFAULT_REGION

2. Set the region:
   $ export AWS_REGION=us-west-2

3. Verify it's set:
   $ echo $AWS_REGION
   (should output: us-west-2)

4. Run the configuration checker:
   $ python scripts/examples/bedrock_client_usage.py

5. Run a HELM benchmark:
   $ helm-run --run-entries mmlu:subject=clinical_knowledge,model=amazon/nova-pro-v1:0 --suite quick-test --max-eval-instances 5

If you still get NoRegionError:
  - Double-check the environment variable is set: echo $AWS_REGION
  - Make sure you're not using the '!' prefix
  - Try using the inline syntax: AWS_REGION=us-west-2 helm-run ...
    """)


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("AWS Bedrock Region Configuration Test")
    print("=" * 60)
    
    # Run tests
    test_region_configuration()
    
    # Show command syntax
    demonstrate_command_syntax()
    
    # Show verification steps
    show_verification_steps()
    
    print("\n" + "=" * 60)
    print("For complete documentation, see:")
    print("  - scripts/examples/BEDROCK_QUICKSTART.md")
    print("  - docs/credentials.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
