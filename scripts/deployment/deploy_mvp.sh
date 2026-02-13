#!/bin/bash

# MVP Deployment Script - One command to deploy everything
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Run: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-"us-east-1"}
print_status "AWS Account: $ACCOUNT_ID | Region: $REGION"

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

# Step 1: S3 Buckets
print_status "Setting up S3 buckets..."
cd "$(dirname "$0")/scripts" && ./s3_setup.sh && cd - > /dev/null

# Step 2: DynamoDB Table
print_status "Checking DynamoDB table..."
if ! aws dynamodb describe-table --table-name mocktailverse-jobs &> /dev/null; then
    print_status "Creating DynamoDB table..."
    aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json
    aws dynamodb wait table-exists --table-name mocktailverse-jobs
else
    print_warn "DynamoDB table already exists"
fi

# Step 3: Deploy Lambda Functions
print_status "Deploying Lambda functions..."
cd "$(dirname "$0")/scripts" && ./deploy_lambda.sh && cd - > /dev/null
cd "$(dirname "$0")/scripts" && ./deploy_fetch_lambda.sh && cd - > /dev/null

# Step 4: Quick Test
print_status "Running quick test..."
echo '{"fetch_type":"mocktails","limit":1}' > /tmp/test_payload.json
aws lambda invoke \
  --function-name mocktailverse-fetch-cocktails \
  --payload file:///tmp/test_payload.json \
  /tmp/test_response.json &> /dev/null

if [ $? -eq 0 ]; then
    print_status "Test passed! Lambda is working."
    rm -f /tmp/test_payload.json /tmp/test_response.json
else
    print_warn "Test failed, but deployment completed"
fi

print_status "MVP Deployment Complete!"
echo ""
echo "Quick Commands:"
echo "  Test fetch: aws lambda invoke --function-name mocktailverse-fetch-cocktails --payload '{\"fetch_type\":\"mocktails\",\"limit\":3}' response.json"
echo "  Check DynamoDB: aws dynamodb scan --table-name mocktailverse-jobs --limit 5"
echo "  Check S3: aws s3 ls s3://mocktailverse-processed/ --recursive"

