# 🚀 MOCKTAILVERSE - DEPLOYMENT GUIDE

Complete step-by-step guide to deploy the AWS ETL pipeline.

───────────────────────────────────────────────────────────────────────────────────

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ AWS Account (Free Tier eligible)
- ✅ AWS CLI installed and configured
- ✅ Python 3.8+ installed
- ✅ Basic terminal/command line knowledge

───────────────────────────────────────────────────────────────────────────────────

## 🔧 Step 1: AWS CLI Setup

### Configure AWS Credentials

```bash
aws configure
```

**Enter your credentials:**
- AWS Access Key ID: `YOUR_ACCESS_KEY_ID` (get from AWS Console → IAM → Security Credentials)
- AWS Secret Access Key: `YOUR_SECRET_ACCESS_KEY` (get from AWS Console → IAM → Security Credentials)
- Default region: `us-east-1`
- Default output format: `json`

**⚠️ SECURITY NOTE:** Never commit real AWS credentials to git! Use environment variables or AWS credentials file.

### Verify Configuration

```bash
aws sts get-caller-identity
```

**Expected output:** Your AWS account ID and user ARN

───────────────────────────────────────────────────────────────────────────────────

## 🐍 Step 2: Local Environment Setup

### Create Virtual Environment

```bash
cd /Users/anixlynch/dev/northstar/02_mocktailverse
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import boto3, fastapi; print('✅ Dependencies installed')"
```

───────────────────────────────────────────────────────────────────────────────────

## 📦 Step 3: Deploy S3 Buckets

### Create S3 Buckets

```bash
# Create raw bucket
aws s3 mb s3://mocktailverse-raw --region us-east-1

# Create processed bucket
aws s3 mb s3://mocktailverse-processed --region us-east-1
```

### Verify Buckets

```bash
aws s3 ls | grep mocktailverse
```

**Expected output:**
```
2025-11-06 15:45:27 mocktailverse-processed
2025-11-06 15:45:26 mocktailverse-raw
```

───────────────────────────────────────────────────────────────────────────────────

## ⚡ Step 4: Deploy Lambda Functions

### Deploy Transform Lambda

```bash
./deploy_lambda.sh
```

**What this does:**
- Creates IAM role for Lambda
- Packages Lambda function code
- Deploys `mocktailverse-transform` function
- Configures S3 trigger
- Sets up DynamoDB permissions

### Deploy Fetch Lambda

```bash
./deploy_fetch_lambda.sh
```

**What this does:**
- Packages fetch-cocktails Lambda
- Deploys `mocktailverse-fetch-cocktails` function
- Configures environment variables

### Verify Lambda Functions

```bash
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mocktailverse`)].FunctionName' --output table
```

**Expected output:**
```
-----------------------------------
|          ListFunctions          |
+---------------------------------+
|  mocktailverse-transform        |
|  mocktailverse-fetch-cocktails  |
+---------------------------------+
```

───────────────────────────────────────────────────────────────────────────────────

## 🗄️ Step 5: Create DynamoDB Table

### Create Table

```bash
aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json
```

### Verify Table Status

```bash
aws dynamodb describe-table --table-name mocktailverse-jobs --query 'Table.TableStatus' --output text
```

**Expected output:** `ACTIVE`

**Wait for table to be active:**
```bash
aws dynamodb wait table-exists --table-name mocktailverse-jobs
```

───────────────────────────────────────────────────────────────────────────────────

## 🔗 Step 6: Configure S3 → Lambda Trigger

### Verify Trigger is Configured

```bash
aws s3api get-bucket-notification-configuration --bucket mocktailverse-raw
```

**Expected:** Lambda function ARN should be listed

### If Not Configured, Run:

```bash
FUNCTION_ARN=$(aws lambda get-function --function-name mocktailverse-transform --query 'Configuration.FunctionArn' --output text)

aws lambda add-permission \
  --function-name mocktailverse-transform \
  --statement-id s3-trigger \
  --action "lambda:InvokeFunction" \
  --principal s3.amazonaws.com \
  --source-arn "arn:aws:s3:::mocktailverse-raw"

aws s3api put-bucket-notification-configuration \
  --bucket mocktailverse-raw \
  --notification-configuration "{\"LambdaFunctionConfigurations\":[{\"LambdaFunctionArn\":\"$FUNCTION_ARN\",\"Events\":[\"s3:ObjectCreated:*\"],\"Filter\":{\"Key\":{\"FilterRules\":[{\"Name\":\"suffix\",\"Value\":\"json\"}]}}}]}"
```

───────────────────────────────────────────────────────────────────────────────────

## ✅ Step 7: Verify Deployment

### Check All Services

```bash
echo "=== Lambda Functions ==="
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mocktailverse`)].FunctionName' --output table

echo "=== S3 Buckets ==="
aws s3 ls | grep mocktailverse

echo "=== DynamoDB Table ==="
aws dynamodb describe-table --table-name mocktailverse-jobs --query 'Table.TableStatus' --output text

echo "=== S3 Trigger ==="
aws s3api get-bucket-notification-configuration --bucket mocktailverse-raw --query 'LambdaFunctionConfigurations[0].LambdaFunctionArn' --output text
```

───────────────────────────────────────────────────────────────────────────────────

## 🧪 Step 8: Test the Pipeline

### Test 1: Fetch Mocktails via Lambda

```bash
echo '{"fetch_type":"mocktails","limit":3}' > test_payload.json
aws lambda invoke \
  --function-name mocktailverse-fetch-cocktails \
  --payload file://test_payload.json \
  response.json

cat response.json | python3 -m json.tool
```

### Test 2: Upload Data to S3 (Triggers Transform)

```bash
aws s3 cp data/raw/sample_data.json s3://mocktailverse-raw/test_upload.json
```

**Wait 5-10 seconds, then check:**

```bash
# Check processed bucket
aws s3 ls s3://mocktailverse-processed/ --recursive | tail -3

# Check DynamoDB
aws dynamodb scan --table-name mocktailverse-jobs --limit 5 --query 'Items[*].title.S' --output text
```

### Test 3: Local FastAPI Test Harness

```bash
cd api
source ../venv/bin/activate
python test_harness.py
```

**Visit:** http://localhost:8000/docs

**Test endpoint:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d @../data/raw/sample_data.json
```

───────────────────────────────────────────────────────────────────────────────────

## 📊 Step 9: Monitor & Verify

### Check Lambda Logs

```bash
# Transform Lambda logs
aws logs tail /aws/lambda/mocktailverse-transform --since 1h

# Fetch Lambda logs
aws logs tail /aws/lambda/mocktailverse-fetch-cocktails --since 1h
```

### Check Data in DynamoDB

```bash
# Count records
aws dynamodb scan --table-name mocktailverse-jobs --select COUNT

# View sample records
aws dynamodb scan --table-name mocktailverse-jobs --limit 3 --query 'Items[*].[job_id.S,title.S,company.S]' --output table
```

### Check S3 Files

```bash
# Raw bucket
aws s3 ls s3://mocktailverse-raw/ --recursive

# Processed bucket
aws s3 ls s3://mocktailverse-processed/ --recursive
```

───────────────────────────────────────────────────────────────────────────────────

## 🎯 Quick Deployment (One Command)

If you want to deploy everything at once:

```bash
# Make scripts executable
chmod +x s3_setup.sh deploy_lambda.sh deploy_fetch_lambda.sh

# Deploy S3 buckets
./s3_setup.sh

# Deploy Lambda functions
./deploy_lambda.sh
./deploy_fetch_lambda.sh

# Create DynamoDB table
aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json

# Wait for table to be active
aws dynamodb wait table-exists --table-name mocktailverse-jobs
```

───────────────────────────────────────────────────────────────────────────────────

## 🔍 Troubleshooting

### Issue: Lambda Permission Denied

**Solution:**
```bash
aws iam attach-role-policy \
  --role-name mocktailverse-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Issue: S3 Trigger Not Working

**Solution:**
```bash
# Re-configure trigger
FUNCTION_ARN=$(aws lambda get-function --function-name mocktailverse-transform --query 'Configuration.FunctionArn' --output text)

aws lambda add-permission \
  --function-name mocktailverse-transform \
  --statement-id s3-trigger-$(date +%s) \
  --action "lambda:InvokeFunction" \
  --principal s3.amazonaws.com \
  --source-arn "arn:aws:s3:::mocktailverse-raw"
```

### Issue: DynamoDB Table Creation Fails

**Check:** Table might already exist
```bash
aws dynamodb describe-table --table-name mocktailverse-jobs
```

**If exists and you want to recreate:**
```bash
aws dynamodb delete-table --table-name mocktailverse-jobs
aws dynamodb wait table-not-exists --table-name mocktailverse-jobs
# Then recreate
```

───────────────────────────────────────────────────────────────────────────────────

## ✅ Deployment Checklist

- [ ] AWS CLI configured
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] S3 buckets created (raw + processed)
- [ ] Lambda transform function deployed
- [ ] Lambda fetch-cocktails function deployed
- [ ] DynamoDB table created and active
- [ ] S3 → Lambda trigger configured
- [ ] IAM permissions set
- [ ] Pipeline tested end-to-end
- [ ] CloudWatch logs accessible

───────────────────────────────────────────────────────────────────────────────────

## 🎉 Success Indicators

You'll know deployment is successful when:

✅ **Lambda Functions:** Both show "Active" status  
✅ **S3 Buckets:** Both buckets accessible  
✅ **DynamoDB:** Table status is "ACTIVE"  
✅ **S3 Trigger:** Lambda ARN configured  
✅ **Test Upload:** File uploads trigger Lambda automatically  
✅ **Data Storage:** Records appear in DynamoDB  
✅ **Logs:** CloudWatch shows successful executions  

───────────────────────────────────────────────────────────────────────────────────

## 📝 Post-Deployment

### View Dashboard

Check your metrics:
- `ETL_METRICS.md` - Production metrics
- `DASHBOARD.md` - Business overview
- `ETL_DASHBOARD.md` - Technical operations

### Monitor Costs

```bash
# Check free tier usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=mocktailverse-transform \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

### Next Steps

1. Set up EventBridge for scheduled fetches
2. Add CloudWatch alarms
3. Create SNS notifications
4. Build frontend dashboard
5. Add additional API integrations

───────────────────────────────────────────────────────────────────────────────────

**Deployment Complete! 🎉**

Your AWS ETL pipeline is now live and ready for production use.

