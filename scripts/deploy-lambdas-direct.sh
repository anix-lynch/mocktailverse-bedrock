#!/bin/bash
# Create Lambda functions directly with AWS CLI

set -e

GREEN='\033[0;32m'
NC='\033[0m'
print_status() { echo -e "${GREEN}[✓]${NC} $1"; }

REGION=us-west-2
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/mocktailverse-lambda-role"

# Create IAM role if it doesn't exist
if ! aws iam get-role --role-name mocktailverse-lambda-role &> /dev/null; then
    print_status "Creating IAM role..."
    
    aws iam create-role \
        --role-name mocktailverse-lambda-role \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' > /dev/null
    
    # Attach policies
    aws iam attach-role-policy \
        --role-name mocktailverse-lambda-role \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    aws iam put-role-policy \
        --role-name mocktailverse-lambda-role \
        --policy-name mocktailverse-lambda-policy \
        --policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:*", "dynamodb:*", "bedrock:InvokeModel", "lambda:InvokeFunction"],
                    "Resource": "*"
                }
            ]
        }'
    
    sleep 10  # Wait for role to propagate
fi

# Deploy each Lambda
for FUNC in ingest embed search rag; do
    print_status "Deploying $FUNC Lambda..."
    
    FUNC_NAME="mocktailverse-$FUNC"
    
    if aws lambda get-function --function-name $FUNC_NAME --region $REGION &> /dev/null; then
        # Update existing
        aws lambda update-function-code \
            --function-name $FUNC_NAME \
            --zip-file fileb://lambdas/$FUNC/deployment.zip \
            --region $REGION > /dev/null
    else
        # Create new
        aws lambda create-function \
            --function-name $FUNC_NAME \
            --runtime python3.11 \
            --role $ROLE_ARN \
            --handler handler.lambda_handler \
            --zip-file fileb://lambdas/$FUNC/deployment.zip \
            --timeout 300 \
            --memory-size 512 \
            --region $REGION \
            --environment "Variables={
                RAW_BUCKET=mocktailverse-raw-$ACCOUNT_ID,
                EMBEDDINGS_BUCKET=mocktailverse-embeddings-$ACCOUNT_ID,
                METADATA_TABLE=mocktailverse-metadata,
                SEARCH_LAMBDA=mocktailverse-search
            }" > /dev/null
    fi
done

print_status "All Lambda functions deployed!"
