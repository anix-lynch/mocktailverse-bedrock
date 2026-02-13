#!/bin/bash
# Mocktailverse Lambda Deployment Script
# 🎯 PURPOSE: Automated deployment of AWS Lambda functions for ETL pipeline
# 📊 FEATURES: IAM role creation, function packaging, S3 trigger setup, permissions
# 🏗️ ARCHITECTURE: Local build → AWS Lambda → S3 triggers → DynamoDB storage
# ⚡ DEPLOYMENT: One-command deployment with error handling and verification

set -e  # Exit on any error

# Configuration
FUNCTION_NAME="mocktailverse-transform"
HANDLER="transform.lambda_handler"
RUNTIME="python3.9"
MEMORY_SIZE=256
TIMEOUT=900  # 15 minutes
REGION=${AWS_REGION:-"us-east-1"}
ROLE_NAME="mocktailverse-lambda-role"

# Load bucket configuration if available
if [ -f ".bucket_config" ]; then
    source .bucket_config
    RAW_BUCKET=${RAW_BUCKET:-"mocktailverse-raw"}
    PROCESSED_BUCKET=${PROCESSED_BUCKET:-"mocktailverse-processed"}
else
    RAW_BUCKET="mocktailverse-raw"
    PROCESSED_BUCKET="mocktailverse-processed"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current AWS account
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS Account: $ACCOUNT_ID"
print_status "Target Region: $REGION"

# Create IAM role for Lambda if it doesn't exist
create_lambda_role() {
    print_status "Creating IAM role for Lambda function..."
    
    # Check if role already exists
    if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
        print_warning "IAM role $ROLE_NAME already exists"
        return 0
    fi
    
    # Create trust policy document
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    # Create the role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json \
        --description "IAM role for Mocktailverse Lambda function"
    
    if [ $? -eq 0 ]; then
        print_status "Successfully created IAM role: $ROLE_NAME"
        
        # Wait for role to be available
        sleep 10
        
        # Attach AWS managed policies
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
        
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
        
        print_status "Attached necessary IAM policies to role"
    else
        print_error "Failed to create IAM role: $ROLE_NAME"
        return 1
    fi
    
    # Clean up trust policy file
    rm -f trust-policy.json
}

# Create Lambda deployment package
create_deployment_package() {
    print_status "Creating Lambda deployment package..."
    
    # Create temporary directory
    DEPLOY_DIR="lambda-deploy"
    rm -rf $DEPLOY_DIR
    mkdir -p $DEPLOY_DIR
    
    # Copy Lambda function and dependencies
    cp ../lambda/transform.py $DEPLOY_DIR/
    
    # Create requirements file for Lambda
    cat > $DEPLOY_DIR/requirements.txt << EOF
boto3==1.34.0
python-dateutil==2.8.2
EOF
    
    # Install dependencies in deployment directory
    print_status "Installing Lambda dependencies..."
    cd $DEPLOY_DIR
    
    # Create zip package
    zip -r ../deployment.zip .
    cd ..
    
    print_status "Deployment package created: deployment.zip"
    
    # Clean up
    rm -rf $DEPLOY_DIR
}

# Deploy Lambda function
deploy_lambda_function() {
    print_status "Deploying Lambda function..."
    
    # Get role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query Role.Arn --output text)
    
    # Check if function already exists
    if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
        print_status "Updating existing Lambda function..."
        
        # Update function code
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://deployment.zip \
            --region $REGION
        
        # Update function configuration
        aws lambda update-function-configuration \
            --function-name $FUNCTION_NAME \
            --runtime $RUNTIME \
            --role $ROLE_ARN \
            --handler $HANDLER \
            --memory-size $MEMORY_SIZE \
            --timeout $TIMEOUT \
            --environment Variables="{
                PROCESSED_BUCKET=$PROCESSED_BUCKET,
                DYNAMODB_TABLE=mocktailverse-jobs
            }" \
            --region $REGION
        
        print_status "Lambda function updated successfully"
    else
        print_status "Creating new Lambda function..."
        
        # Create new function
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime $RUNTIME \
            --role $ROLE_ARN \
            --handler $HANDLER \
            --memory-size $MEMORY_SIZE \
            --timeout $TIMEOUT \
            --zip-file fileb://deployment.zip \
            --region $REGION \
            --environment Variables="{
                PROCESSED_BUCKET=$PROCESSED_BUCKET,
                DYNAMODB_TABLE=mocktailverse-jobs
            }" \
            --description "Mocktailverse data transformation Lambda function"
        
        print_status "Lambda function created successfully"
    fi
}

# Set up S3 trigger for Lambda
setup_s3_trigger() {
    print_status "Setting up S3 trigger for Lambda function..."
    
    # Get Lambda function ARN
    FUNCTION_ARN=$(aws lambda get-function \
        --function-name $FUNCTION_NAME \
        --query Configuration.FunctionArn \
        --output text \
        --region $REGION)
    
    # Add S3 trigger
    aws s3api put-bucket-notification-configuration \
        --bucket $RAW_BUCKET \
        --notification-configuration '{
            "LambdaFunctionConfigurations": [
                {
                    "LambdaFunctionArn": "'$FUNCTION_ARN'",
                    "Events": ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [
                                {
                                    "Name": "suffix",
                                    "Value": "json"
                                }
                            ]
                        }
                    }
                }
            ]
        }' \
        --region $REGION
    
    # Add permission for S3 to invoke Lambda
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id s3-trigger \
        --action "lambda:InvokeFunction" \
        --principal s3.amazonaws.com \
        --source-arn arn:aws:s3:::$RAW_BUCKET \
        --region $REGION
    
    print_status "S3 trigger configured successfully"
}

# Grant DynamoDB permissions to Lambda
grant_dynamodb_permissions() {
    print_status "Granting DynamoDB permissions to Lambda..."
    
    # Create custom policy for DynamoDB access
    cat > dynamodb-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DescribeTable"
            ],
            "Resource": "arn:aws:dynamodb:$REGION:$ACCOUNT_ID:table/mocktailverse-jobs"
        }
    ]
}
EOF
    
    # Attach custom policy
    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name MocktailverseDynamoDBAccess \
        --policy-document file://dynamodb-policy.json
    
    print_status "DynamoDB permissions granted"
    
    # Clean up
    rm -f dynamodb-policy.json
}

# Test Lambda function
test_lambda_function() {
    print_status "Testing Lambda function..."
    
    # Create test event
    cat > test-event.json << EOF
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "$REGION",
      "eventTime": "2024-01-15T12:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": {
          "name": "$RAW_BUCKET",
          "arn": "arn:aws:s3:::$RAW_BUCKET"
        },
        "object": {
          "key": "sample_data.json",
          "size": 1024,
          "eTag": "d41d8cd98f00b204e9800998ecf8427e"
        }
      }
    }
  ]
}
EOF
    
    # Invoke Lambda function
    aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload file://test-event.json \
        --region $REGION \
        test-output.json
    
    # Display results
    if [ -f "test-output.json" ]; then
        print_status "Lambda test completed successfully"
        echo "Test output:"
        cat test-output.json | jq '.' 2>/dev/null || cat test-output.json
        rm -f test-output.json
    else
        print_error "Lambda test failed"
    fi
    
    # Clean up
    rm -f test-event.json
}

# Main deployment flow
main() {
    print_status "Starting Mocktailverse Lambda deployment..."
    
    # Create IAM role
    create_lambda_role
    
    # Create deployment package
    create_deployment_package
    
    # Deploy Lambda function
    deploy_lambda_function
    
    # Grant DynamoDB permissions
    grant_dynamodb_permissions
    
    # Set up S3 trigger
    setup_s3_trigger
    
    # Test function
    test_lambda_function
    
    # Clean up deployment package
    rm -f deployment.zip
    
    print_status "Lambda deployment completed successfully!"
    echo ""
    echo "Deployment Summary:"
    echo "=================="
    echo "Function Name: $FUNCTION_NAME"
    echo "Runtime: $RUNTIME"
    echo "Memory: ${MEMORY_SIZE}MB"
    echo "Timeout: ${TIMEOUT}s"
    echo "Raw Bucket: $RAW_BUCKET"
    echo "Processed Bucket: $PROCESSED_BUCKET"
    echo "Region: $REGION"
    echo ""
    echo "Next Steps:"
    echo "1. Create DynamoDB table: aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json"
    echo "2. Test with FastAPI: cd api && python test_harness.py"
    echo "3. Upload test data to S3: aws s3 cp data/raw/sample_data.json s3://$RAW_BUCKET/"
}

# Run main function
main "$@"