#!/bin/bash
# Script to help upload workshop notebooks to SageMaker Code Editor

set -e

echo "=========================================="
echo "MedHELM Workshop Notebook Upload Helper"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "workshop-notebook-1-introduction.ipynb" ]; then
    echo "Error: Workshop notebooks not found in current directory."
    echo "Please run this script from the cloudformation/ directory."
    exit 1
fi

echo "This script will help you upload workshop notebooks to your SageMaker environment."
echo ""
echo "You have two options:"
echo ""
echo "Option 1: Manual Upload (Recommended)"
echo "  1. Access your SageMaker Code Editor"
echo "  2. Create directory: mkdir -p ~/workshop-notebooks"
echo "  3. Upload notebooks via the File Browser"
echo ""
echo "Option 2: Using AWS CLI and S3"
echo "  1. Upload notebooks to S3"
echo "  2. Download from S3 in Code Editor"
echo ""

read -p "Would you like to upload notebooks to S3? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipping S3 upload. Use manual upload method."
    exit 0
fi

# Ask for S3 bucket
read -p "Enter your S3 bucket name (e.g., my-bucket): " BUCKET_NAME

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: Bucket name cannot be empty."
    exit 1
fi

# Optional prefix
read -p "Enter S3 prefix/folder (press Enter for root): " S3_PREFIX

if [ -n "$S3_PREFIX" ]; then
    S3_PATH="s3://${BUCKET_NAME}/${S3_PREFIX}/workshop-notebooks/"
else
    S3_PATH="s3://${BUCKET_NAME}/workshop-notebooks/"
fi

echo ""
echo "Uploading notebooks to: $S3_PATH"
echo ""

# Upload notebooks
for notebook in workshop-notebook-*.ipynb; do
    echo "Uploading: $notebook"
    aws s3 cp "$notebook" "${S3_PATH}${notebook}"
done

echo ""
echo "✓ Upload complete!"
echo ""
echo "To download in Code Editor, run:"
echo ""
echo "  mkdir -p ~/workshop-notebooks"
echo "  cd ~/workshop-notebooks"
echo "  aws s3 sync $S3_PATH ."
echo ""
