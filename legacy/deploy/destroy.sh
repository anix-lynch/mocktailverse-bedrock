#!/bin/bash
# Mocktailverse AWS ETL Pipeline Teardown Script
# Safely removes all AWS resources

set -e

echo "🧹 Mocktailverse ETL Pipeline Teardown"
echo "======================================"

# Load AWS credentials
if [ -f ~/.config/secrets/global.env ]; then
    source ~/.config/secrets/global.env
else
    echo "❌ Error: ~/.config/secrets/global.env not found"
    exit 1
fi

STACK_NAME="mocktailverse-etl-stack"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo ""
echo "⚠️  WARNING: This will delete ALL resources!"
echo "   Stack: $STACK_NAME"
echo "   Region: $REGION"
echo "   Account: $ACCOUNT_ID"
echo ""
read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Teardown cancelled"
    exit 0
fi

# Empty S3 buckets before deletion
echo ""
echo "🗑️  Emptying S3 buckets..."
aws s3 rm s3://mocktailverse-raw-data-$ACCOUNT_ID --recursive --region $REGION || true
aws s3 rm s3://mocktailverse-processed-data-$ACCOUNT_ID --recursive --region $REGION || true
aws s3 rm s3://mocktailverse-scripts-$ACCOUNT_ID --recursive --region $REGION || true

# Delete CloudFormation stack
echo ""
echo "🚮 Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION

echo "⏳ Waiting for stack deletion (this takes ~3-5 minutes)..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION

echo ""
echo "✅ All resources deleted successfully!"
echo ""
echo "💰 Cost Impact: $0/month (all Free Tier resources removed)"
echo ""
