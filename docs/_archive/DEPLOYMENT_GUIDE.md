# Deployment Guide

This guide covers deploying the Mocktailverse GenAI platform to AWS.

## Prerequisites

- AWS Account with Bedrock access (us-west-2 region)
- AWS CLI configured with credentials
- Node.js 18+ and Python 3.11+
- Access to Claude 3 Haiku and Titan Embeddings in Bedrock

## Quick Start

### 1. Backend Deployment

Deploy Lambda functions and API Gateway:

```bash
cd lambdas/agent
zip -r agent.zip .
aws lambda update-function-code \
  --function-name mocktailverse-agent \
  --zip-file fileb://agent.zip \
  --region us-west-2
```

Repeat for `search`, `rag`, and `ingest` lambdas.

### 2. Frontend Deployment

Build and deploy to S3:

```bash
cd frontend
npm install
npm run build
aws s3 sync out/ s3://<YOUR_BUCKET>/ --delete
```

Create CloudFront invalidation:

```bash
aws cloudfront create-invalidation \
  --distribution-id <YOUR_DIST_ID> \
  --paths "/*"
```

### 3. Configure Environment

Update `lambdas/agent/handler.py`:
- Set `BEDROCK_MODEL` to your preferred model
- Configure `AGENT_ID` and `AGENT_ALIAS_ID` if using Bedrock Agents

Update `frontend/next.config.js`:
- Set `NEXT_PUBLIC_API_URL` to your API Gateway endpoint

### 4. Test

```bash
curl -X POST <API_GATEWAY_URL>/prod/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a mojito?"}'
```

## Architecture

The deployment creates:
- **4 Lambda functions** (agent, search, rag, ingest)
- **1 API Gateway** REST API
- **1 S3 bucket** for frontend static files
- **1 CloudFront distribution**
- **1 DynamoDB table** for metadata
- **1 OpenSearch Serverless collection** (optional)

## Cost Estimate

Expected monthly cost for light usage (100-500 queries):
- Lambda: ~$0.05
- Bedrock API calls: ~$0.10
- S3 + CloudFront: ~$0.01
- **Total: ~$0.15-0.20/month**

## Monitoring

View logs in CloudWatch:
```bash
aws logs tail /aws/lambda/mocktailverse-agent --follow
```

## Troubleshooting

**Common Issues:**

1. **"Access Denied" on CloudFront**: Check S3 bucket policy allows public read
2. **Lambda timeout**: Increase timeout to 30s in Lambda configuration
3. **Model not available**: Request access in Bedrock console (Model access page)

## Cleanup

To delete all resources:
```bash
# Delete S3 bucket
aws s3 rm s3://<YOUR_BUCKET> --recursive
aws s3api delete-bucket --bucket <YOUR_BUCKET>

# Delete Lambda functions
aws lambda delete-function --function-name mocktailverse-agent
# Repeat for other functions

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id <API_ID>
```

## Next Steps

- Add more cocktail data to DynamoDB
- Implement conversation memory
- Add rate limiting and authentication
- Deploy to multiple regions
