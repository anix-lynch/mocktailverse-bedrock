#!/bin/bash
# Deploy all Lambda functions for Mocktailverse GenAI Platform

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }

REGION=${AWS_DEFAULT_REGION:-us-west-2}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

print_status "Deploying to AWS Account: $ACCOUNT_ID | Region: $REGION"

# Lambda functions to deploy
FUNCTIONS=("ingest" "embed" "search" "rag")

for FUNC in "${FUNCTIONS[@]}"; do
    print_status "Deploying $FUNC Lambda..."
    
    cd "lambdas/$FUNC"
    
    # Create deployment package
    rm -rf package deployment.zip
    mkdir -p package
    
    # Install dependencies
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt -t package/ --quiet
    fi
    
    # Copy handler
    cp handler.py package/
    
    # Create zip
    cd package
    zip -r ../deployment.zip . > /dev/null
    cd ..
    
    # Deploy or update Lambda
    FUNCTION_NAME="mocktailverse-$FUNC"
    
    if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
        print_status "Updating existing function: $FUNCTION_NAME"
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://deployment.zip \
            --region $REGION > /dev/null
    else
        print_warn "Function $FUNCTION_NAME not found. Run Terraform first to create infrastructure."
    fi
    
    # Cleanup
    rm -rf package deployment.zip
    
    cd ../..
done

print_status "All Lambda functions deployed successfully!"
