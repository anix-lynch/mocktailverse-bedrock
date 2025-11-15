#!/bin/bash
# Mocktailverse AWS ETL Pipeline Deployment Script
# Deploys entire infrastructure to AWS Free Tier

set -e

echo "🍹 Mocktailverse ETL Pipeline Deployment"
echo "========================================"

# Load AWS credentials
if [ -f ~/.config/secrets/global.env ]; then
    source ~/.config/secrets/global.env
    echo "✅ Loaded AWS credentials from global.env"
else
    echo "❌ Error: ~/.config/secrets/global.env not found"
    exit 1
fi

# Verify AWS credentials
echo ""
echo "Verifying AWS credentials..."
aws sts get-caller-identity || {
    echo "❌ AWS credentials not configured correctly"
    exit 1
}

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ Authenticated as AWS Account: $ACCOUNT_ID"

# Set variables
STACK_NAME="mocktailverse-etl-stack"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
TEMPLATE_FILE="deploy/cloudformation-etl-stack.yaml"

echo ""
echo "📋 Deployment Configuration:"
echo "   Stack Name: $STACK_NAME"
echo "   Region: $REGION"
echo "   Account: $ACCOUNT_ID"
echo ""

# Create CloudFormation stack
echo "🚀 Creating CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION \
    --tags Key=Project,Value=Mocktailverse Key=Environment,Value=Production

echo "⏳ Waiting for stack creation (this takes ~5-10 minutes)..."
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $REGION

echo ""
echo "✅ Stack created successfully!"

# Get stack outputs
echo ""
echo "📊 Getting stack outputs..."
AIRFLOW_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`AirflowURL`].OutputValue' \
    --output text \
    --region $REGION)

RAW_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' \
    --output text \
    --region $REGION)

PROCESSED_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ProcessedDataBucketName`].OutputValue' \
    --output text \
    --region $REGION)

DYNAMODB_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' \
    --output text \
    --region $REGION)

LAMBDA_FUNCTION=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
    --output text \
    --region $REGION)

# Upload Lambda function code
echo ""
echo "📦 Uploading Lambda function code..."
cd lambda
zip -r transform.zip transform.py
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION \
    --zip-file fileb://transform.zip \
    --region $REGION
rm transform.zip
cd ..

# Upload Glue job script
echo ""
echo "📦 Uploading Glue job script..."
SCRIPTS_BUCKET="mocktailverse-scripts-$ACCOUNT_ID"
aws s3 cp glue_job.py s3://$SCRIPTS_BUCKET/glue/transform_cocktail_data.py --region $REGION

# Upload sample data
echo ""
echo "📦 Uploading sample data..."
aws s3 cp margarita_recipes.json s3://$RAW_BUCKET/extracted/$(date +%Y/%m/%d)/cocktail_data.json --region $REGION

echo ""
echo "========================================"
echo "🎉 Deployment Complete!"
echo "========================================"
echo ""
echo "📊 Access Your Infrastructure:"
echo "   Airflow UI: $AIRFLOW_URL"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🗄️ AWS Resources:"
echo "   Raw Data Bucket: $RAW_BUCKET"
echo "   Processed Bucket: $PROCESSED_BUCKET"
echo "   DynamoDB Table: $DYNAMODB_TABLE"
echo "   Lambda Function: $LAMBDA_FUNCTION"
echo ""
echo "⚠️ Important Notes:"
echo "   1. Airflow may take 2-3 minutes to fully start"
echo "   2. First DAG run will initialize the pipeline"
echo "   3. All resources are within AWS Free Tier limits"
echo "   4. Monitor usage at: https://console.aws.amazon.com/billing"
echo ""
echo "🚀 Next Steps:"
echo "   1. Access Airflow UI at: $AIRFLOW_URL"
echo "   2. Trigger DAG: 'mocktailverse_etl_pipeline'"
echo "   3. View results in DynamoDB: $DYNAMODB_TABLE"
echo "   4. Monitor with Streamlit: streamlit run streamlit_app.py"
echo ""
echo "💡 To destroy the stack:"
echo "   ./deploy/destroy.sh"
echo ""
