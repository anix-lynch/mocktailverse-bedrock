# 🚀 Deployment Guide

## Prerequisites

- AWS Account with Bedrock access enabled
- AWS CLI configured (`aws configure`)
- Terraform >= 1.5.0
- Node.js >= 18
- Python >= 3.11

## Quick Deploy (5 minutes)

```bash
# 1. Clone and enter directory
cd /Users/anixlynch/dev/northstar/02_mocktailverse

# 2. Run master deployment script
./deploy.sh
```

That's it! The script will:
1. Package all Lambda functions
2. Deploy infrastructure with Terraform
3. Load initial cocktail data
4. Test API endpoints
5. Output your CloudFront URL

## Manual Deployment (Step-by-Step)

### Step 1: Package Lambda Functions

```bash
# Package all functions
for func in ingest embed search rag; do
    cd lambdas/$func
    rm -rf package deployment.zip
    mkdir package
    pip install -r requirements.txt -t package/
    cp handler.py package/
    cd package && zip -r ../deployment.zip . && cd ../..
done
```

### Step 2: Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Resources Created:**
- 3x S3 buckets (raw, embeddings, frontend)
- 1x DynamoDB table (metadata)
- 4x Lambda functions (ingest, embed, search, rag)
- 1x API Gateway (HTTP API)
- 1x CloudFront distribution
- 1x EventBridge rule (daily ingestion)
- IAM roles and policies

### Step 3: Load Initial Data

```bash
# Fetch 20 mocktails
aws lambda invoke \
    --function-name mocktailverse-ingest \
    --payload '{"fetch_type":"mocktails","limit":20}' \
    response.json

# Generate embeddings
aws lambda invoke \
    --function-name mocktailverse-embed \
    --payload '{}' \
    response.json
```

### Step 4: Test API

```bash
# Get API endpoint
API_URL=$(cd terraform && terraform output -raw api_endpoint)

# Test search
curl -X POST "$API_URL/v1/search" \
    -H "Content-Type: application/json" \
    -d '{"query":"refreshing summer drinks","k":5}'

# Test RAG
curl -X POST "$API_URL/v1/rag" \
    -H "Content-Type: application/json" \
    -d '{"question":"What makes a good mojito?"}'
```

### Step 5: Deploy Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set API URL
export NEXT_PUBLIC_API_URL="YOUR_API_GATEWAY_URL"

# Build
npm run build

# Deploy to S3
BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket)
aws s3 sync out/ s3://$BUCKET

# Get CloudFront URL
cd ../terraform
terraform output cloudfront_url
```

## Configuration

### Environment Variables

**Lambda Functions:**
- `RAW_BUCKET` - S3 bucket for raw data
- `EMBEDDINGS_BUCKET` - S3 bucket for embeddings
- `METADATA_TABLE` - DynamoDB table name
- `SEARCH_LAMBDA` - Search Lambda function name

**Frontend:**
- `NEXT_PUBLIC_API_URL` - API Gateway endpoint

### Terraform Variables

Edit `terraform/main.tf` to customize:

```hcl
variable "aws_region" {
  default = "us-west-2"  # Change region
}

variable "project_name" {
  default = "mocktailverse"  # Change project name
}
```

## Cost Optimization

### Current Setup (~$1-5/month)

**Free Tier Usage:**
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage free
- S3: 5GB storage free
- CloudFront: 1TB transfer free (first year)

**Paid Services:**
- Bedrock Claude: ~$0.30/month (100K tokens)
- Bedrock Titan Embeddings: ~$0.10/month (1M tokens)
- API Gateway: ~$0.04/month (10K requests)

### With OpenSearch Serverless (+$24/month)

To add vector search with OpenSearch:

```hcl
# Add to terraform/main.tf
resource "aws_opensearchserverless_collection" "vectors" {
  name = "${var.project_name}-vectors"
  type = "VECTORSEARCH"
}
```

**Total: ~$25/month**

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/mocktailverse-ingest --follow
aws logs tail /aws/lambda/mocktailverse-embed --follow
aws logs tail /aws/lambda/mocktailverse-search --follow
aws logs tail /aws/lambda/mocktailverse-rag --follow
```

### Metrics

```bash
# Lambda invocations
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=mocktailverse-search \
    --start-time 2025-11-24T00:00:00Z \
    --end-time 2025-11-25T00:00:00Z \
    --period 3600 \
    --statistics Sum
```

## Troubleshooting

### Lambda Timeout

If embeddings generation times out:

```hcl
# Increase timeout in terraform/main.tf
resource "aws_lambda_function" "embed" {
  timeout = 600  # 10 minutes
}
```

### Bedrock Access Denied

Enable Bedrock models in AWS Console:
1. Go to AWS Bedrock console
2. Click "Model access"
3. Enable Claude 3.5 Sonnet and Titan Embeddings v2

### API CORS Errors

CORS is configured in API Gateway. If issues persist:

```hcl
# Update in terraform/main.tf
cors_configuration {
  allow_origins = ["*"]  # Or specific domain
  allow_methods = ["GET", "POST", "OPTIONS"]
  allow_headers = ["*"]
}
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Warning:** This will delete all data including:
- S3 buckets and contents
- DynamoDB table
- Lambda functions
- CloudFront distribution

## Next Steps

1. **Add More Data**: Run ingestion Lambda with larger limits
2. **Custom Domain**: Add Route53 + ACM certificate
3. **OpenSearch**: Enable vector search for better accuracy
4. **Monitoring**: Set up CloudWatch alarms
5. **CI/CD**: Add GitHub Actions for auto-deployment

## Support

- **GitHub**: https://github.com/anix-lynch/mocktailverse
- **Portfolio**: https://gozeroshot.dev
- **Issues**: Open a GitHub issue

---

**Built with ❤️ using AWS Bedrock, Next.js, and Terraform**
