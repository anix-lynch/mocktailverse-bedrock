#!/bin/bash
# Mocktailverse S3 Infrastructure Setup
# 🎯 PURPOSE: Create and configure S3 buckets for ETL data pipeline
# 📊 FEATURES: Raw/processed buckets, lifecycle policies, encryption, versioning
# 🏗️ ARCHITECTURE: Data lake foundation for serverless ETL pipeline
# ⚡ COST: $0/month (within AWS Free Tier: 5GB storage, 2000 PUT requests)

set -e  # Exit on any error

# Configuration
RAW_BUCKET="mocktailverse-raw"
PROCESSED_BUCKET="mocktailverse-processed"
REGION=${AWS_REGION:-"us-east-1"}

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

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env file..."
    # Export only lines that don't start with #
    export $(grep -v '^#' .env | grep -v '^#' | grep -v '^$' | sed 's/^/export /')
fi

if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current AWS account and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS Account: $ACCOUNT_ID"
print_status "Target Region: $REGION"

# Function to create bucket with proper configuration
create_bucket() {
    local bucket_name=$1
    local bucket_type=$2
    
    print_status "Creating $bucket_type bucket: $bucket_name"
    
    # Check if bucket already exists
    if aws s3 ls s3://$bucket_name &> /dev/null; then
        print_warning "Bucket $bucket_name already exists"
        return 0
    fi
    
    # Create bucket
    if [ "$REGION" = "us-east-1" ]; then
        # us-east-1 doesn't support LocationConstraint
        aws s3 mb s3://$bucket_name --region $REGION
    else
        aws s3 mb s3://$bucket_name --region $REGION \
            --create-bucket-configuration LocationConstraint=$REGION
    fi
    
    if [ $? -eq 0 ]; then
        print_status "Successfully created bucket: $bucket_name"
        
        # Add bucket tags
        aws s3api put-bucket-tagging \
            --bucket $bucket_name \
            --tagging 'TagSet=[{Key=Project,Value=Mocktailverse},{Key=Environment,Value=Development},{Key=Type,Value='$bucket_type'}]' \
            --region $REGION
        
        # Set bucket versioning
        aws s3api put-bucket-versioning \
            --bucket $bucket_name \
            --versioning-configuration Status=Enabled \
            --region $REGION
        
        # Set bucket encryption
        aws s3api put-bucket-encryption \
            --bucket $bucket_name \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }' \
            --region $REGION
        
        # Set lifecycle policy for raw bucket (delete after 30 days)
        if [ "$bucket_type" = "Raw" ]; then
            aws s3api put-bucket-lifecycle-configuration \
                --bucket $bucket_name \
                --lifecycle-configuration '{
                    "Rules": [
                        {
                            "ID": "DeleteOldFiles",
                            "Status": "Enabled",
                            "Expiration": {
                                "Days": 30
                            },
                            "Filter": {
                                "Prefix": ""
                            }
                        }
                    ]
                }' \
                --region $REGION
            print_status "Set 30-day lifecycle policy for raw bucket"
        fi
        
        # Set lifecycle policy for processed bucket (delete after 90 days)
        if [ "$bucket_type" = "Processed" ]; then
            aws s3api put-bucket-lifecycle-configuration \
                --bucket $bucket_name \
                --lifecycle-configuration '{
                    "Rules": [
                        {
                            "ID": "DeleteOldFiles",
                            "Status": "Enabled",
                            "Expiration": {
                                "Days": 90
                            },
                            "Filter": {
                                "Prefix": ""
                            }
                        }
                    ]
                }' \
                --region $REGION
            print_status "Set 90-day lifecycle policy for processed bucket"
        fi
        
    else
        print_error "Failed to create bucket: $bucket_name"
        return 1
    fi
}

# Function to set up bucket notification for Lambda trigger
setup_lambda_notification() {
    local bucket_name=$1
    local lambda_function_name=$2
    
    print_status "Setting up Lambda trigger for bucket: $bucket_name"
    
    # This will be configured after Lambda is deployed
    print_warning "Lambda notification will be configured after Lambda deployment"
    print_status "Run: aws s3api put-bucket-notification-configuration --bucket $bucket_name --notification-configuration '{\"LambdaFunctionConfigurations\":[{\"LambdaFunctionArn\":\"arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$lambda_function_name\",\"Events\":[\"s3:ObjectCreated:*\"]}]}'"
}

# Create raw bucket
create_bucket $RAW_BUCKET "Raw"

# Create processed bucket  
create_bucket $PROCESSED_BUCKET "Processed"

# Upload sample data to raw bucket
print_status "Uploading sample data to raw bucket..."
if [ -f "data/raw/sample_data.json" ]; then
    aws s3 cp data/raw/sample_data.json s3://$RAW_BUCKET/sample_data.json
    print_status "Sample data uploaded to s3://$RAW_BUCKET/sample_data.json"
else
    print_warning "Sample data file not found at data/raw/sample_data.json"
fi

# Display bucket information
print_status "Bucket setup complete!"
echo ""
echo "Bucket Information:"
echo "=================="
echo "Raw Bucket: s3://$RAW_BUCKET"
echo "Processed Bucket: s3://$PROCESSED_BUCKET"
echo "Region: $REGION"
echo ""
echo "Next Steps:"
echo "1. Deploy Lambda function: ./deploy_lambda.sh"
echo "2. Create DynamoDB table: aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json"
echo "3. Configure S3 trigger for Lambda (see output of deploy_lambda.sh)"
echo ""
echo "Test the setup:"
echo "1. Start FastAPI test harness: cd api && python test_harness.py"
echo "2. Visit http://localhost:8000/docs for API documentation"
echo "3. Test with sample data using the /ingest endpoint"

# Save bucket names to environment file for other scripts
cat > .bucket_config << EOF
RAW_BUCKET=$RAW_BUCKET
PROCESSED_BUCKET=$PROCESSED_BUCKET
REGION=$REGION
ACCOUNT_ID=$ACCOUNT_ID
EOF

print_status "Bucket configuration saved to .bucket_config"