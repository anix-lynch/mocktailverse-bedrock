#!/bin/bash
# Mocktailverse Fetch Lambda Deployment Script
# 🎯 PURPOSE: Deploy cocktail data collection Lambda to AWS
# 📊 FEATURES: TheCocktailDB API integration, data transformation, automated scheduling
# 🏗️ ARCHITECTURE: Lambda function → API calls → Data processing → AWS storage
# ⚡ SCALE: Handles 50+ recipes, event-driven execution, zero maintenance

set -e

# Configuration
FUNCTION_NAME="mocktailverse-fetch-cocktails"
HANDLER="fetch_cocktails.lambda_handler"
RUNTIME="python3.9"
MEMORY_SIZE=256
TIMEOUT=60
REGION=${AWS_REGION:-${AWS_DEFAULT_REGION:-"us-east-1"}}
ROLE_NAME="mocktailverse-lambda-role"  # Reuse existing role

# Load bucket configuration if available
if [ -f ".bucket_config" ]; then
    source .bucket_config
    RAW_BUCKET=${RAW_BUCKET:-"mocktailverse-raw"}
    PROCESSED_BUCKET=${PROCESSED_BUCKET:-"mocktailverse-processed"}
else
    RAW_BUCKET="mocktailverse-raw"
    PROCESSED_BUCKET="mocktailverse-processed"
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS Account: $ACCOUNT_ID"
print_status "Target Region: $REGION"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create deployment package
print_status "Creating Lambda deployment package..."

DEPLOY_DIR="$SCRIPT_DIR/lambda-fetch-deploy"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy Lambda function
cp "$PROJECT_ROOT/lambda/fetch_cocktails.py" "$DEPLOY_DIR/"

# Create requirements file
cat > $DEPLOY_DIR/requirements.txt << EOF
boto3==1.34.0
requests==2.31.0
EOF

# Install dependencies
print_status "Installing Lambda dependencies..."
cd $DEPLOY_DIR
pip install -r requirements.txt -t . --quiet

# Create zip package
zip -r ../fetch_deployment.zip . > /dev/null
cd ..

print_status "Deployment package created: fetch_deployment.zip"

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query Role.Arn --output text)

# Deploy Lambda function
print_status "Deploying Lambda function..."

if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
    print_status "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://fetch_deployment.zip \
        --region $REGION > /dev/null
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --memory-size $MEMORY_SIZE \
        --timeout $TIMEOUT \
        --environment Variables="{
            RAW_BUCKET=$RAW_BUCKET,
            PROCESSED_BUCKET=$PROCESSED_BUCKET,
            DYNAMODB_TABLE=mocktailverse-jobs
        }" \
        --region $REGION > /dev/null
else
    print_status "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --memory-size $MEMORY_SIZE \
        --timeout $TIMEOUT \
        --zip-file fileb://fetch_deployment.zip \
        --region $REGION \
        --environment Variables="{
            RAW_BUCKET=$RAW_BUCKET,
            PROCESSED_BUCKET=$PROCESSED_BUCKET,
            DYNAMODB_TABLE=mocktailverse-jobs
        }" \
        --description "Mocktailverse cocktail fetcher from TheCocktailDB API"
fi

# Clean up
rm -rf $DEPLOY_DIR
rm -f fetch_deployment.zip

print_status "Lambda function deployed successfully!"
echo ""
echo "Deployment Summary:"
echo "=================="
echo "Function Name: $FUNCTION_NAME"
echo "Runtime: $RUNTIME"
echo "Memory: ${MEMORY_SIZE}MB"
echo "Timeout: ${TIMEOUT}s"
echo ""
echo "Test the function:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"fetch_type\":\"random\",\"limit\":3}' response.json"

