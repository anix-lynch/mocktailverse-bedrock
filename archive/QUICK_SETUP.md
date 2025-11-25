# Mocktailverse - Quick Setup Guide

## Setup with Your AWS Credentials

Your AWS credentials are already configured in `.env` file. Here's how to get started:

### 1. Install Dependencies
```bash
cd northstar/02_mocktailverse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup AWS Infrastructure
```bash
# Create S3 buckets
./s3_setup.sh

# Deploy Lambda function
./deploy_lambda.sh

# Create DynamoDB table
aws dynamodb create-table --cli-input-json file://dynamo_schema.json
```

### 3. Test the System
```bash
# Run FastAPI test harness
cd api
python test_harness.py

# Test at http://localhost:8000/docs
# Upload sample data via POST /ingest
```

### 4. Verify End-to-End Flow
```bash
# Upload sample data to S3 (triggers Lambda)
aws s3 cp data/raw/sample_data.json s3://mocktailverse-raw/

# Check processed data in S3
aws s3 ls s3://mocktailverse-processed/

# Query DynamoDB for processed records
aws dynamodb scan --table-name mocktailverse-jobs
```

## Free Tier Usage

Your AWS Free Tier includes:
- **S3**: 5GB storage, 20,000 requests/month
- **Lambda**: 1M free requests per month, 400,000 GB-seconds of compute
- **DynamoDB**: 25GB storage, 25 provisioned RCU/WCU

This demo is designed to stay within free tier limits:
- Small sample data (5 job listings)
- Minimal Lambda memory (256MB)
- Efficient DynamoDB provisioned throughput

## Monitoring Costs

Use the cost estimation script to track usage:
```bash
# Get cost estimation for last 7 days
./logs_fetch.sh --costs

# Get recent errors
./logs_fetch.sh --errors

# Get performance metrics
./logs_fetch.sh --metrics
```

## Architecture Flow with Your AWS Account

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │    │     S3      │    │   Lambda    │    │  DynamoDB   │
│ Test Harness │───▶│  (Raw Layer) │───▶│(Transform   │───▶│(Refined     │
│             │    │              │    │  Layer)     │    │  Layer)     │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
                      │                      │
                      ▼                      ▼
                s3://mocktailverse/     Lambda normalizes,
                raw/                   validates fields,
                                        adds timestamps
```

## Troubleshooting

### Common Issues:
1. **AWS Credentials Error**
   - Verify credentials in `.env` file
   - Run `aws configure` to set up CLI

2. **S3 Bucket Already Exists**
   - The script handles this gracefully
   - Check bucket names in output

3. **Lambda Deployment Error**
   - Check IAM permissions for Lambda
   - Verify role exists in IAM console

4. **DynamoDB Table Already Exists**
   - The script handles this gracefully
   - Check table name in output

### Getting Help:
```bash
# Check Lambda logs
./logs_fetch.sh 24  # Last 24 hours

# Get cost breakdown
./logs_fetch.sh --costs

# Check API health
curl http://localhost:8000/health
```

## Next Steps

1. **Test with Sample Data**: Use the provided sample data
2. **Upload Your Own Data**: Replace sample_data.json with your data
3. **Monitor Costs**: Use logs_fetch.sh to track usage
4. **Scale Up**: Adjust Lambda memory and DynamoDB throughput as needed

Your AWS account is now configured and ready to use with the Mocktailverse project!