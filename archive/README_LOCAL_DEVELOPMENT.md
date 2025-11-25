# Mocktailverse - Local Development Guide

## Free Tier & Local Development Options

### Option 1: AWS Free Tier (Recommended)
AWS Free Tier includes:
- **S3**: 5GB storage, 20,000 requests/month
- **Lambda**: 1M free requests per month, 400,000 GB-seconds of compute
- **DynamoDB**: 25GB storage, 25 provisioned RCU/WCU

### Option 2: LocalStack (No AWS Account Needed)
Install LocalStack for local AWS emulation:
```bash
# Install LocalStack
pip install localstack

# Start LocalStack
localstack start

# Configure environment
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY=test
export AWS_SECRET_KEY=test
export AWS_REGION=us-east-1
```

### Option 3: Open Source Database (CockroachDB)
Replace DynamoDB with CockroachDB for free local database:

```bash
# Install CockroachDB
docker run -d --name cockroachdb -p 26257:26257 cockroachdb/cockroach

# Update .env configuration
DATABASE_URL=postgresql://root@localhost:26257/defaultdb?sslmode=disable
USE_COCKROACHDB=true
```

## MCP Servers Needed for Local Development

### Required MCP Servers:
1. **filesystem** - Already available
   - For reading/writing local files
   - Managing project structure

2. **docker** (Optional) - For database containers
   - If using CockroachDB or LocalStack
   - Install Docker Desktop or Docker CLI

### No Additional AWS MCP Servers Needed
The project is designed to work with:
- Local file system for data storage
- In-memory processing for testing
- Optional AWS connection when credentials available

## Modified Files for Local Development

### 1. API Test Harness (`api/test_harness.py`)
- ✅ Already supports local mode (no AWS credentials)
- ✅ Uses in-memory storage for demo
- ✅ Falls back gracefully when AWS not available

### 2. Lambda Function (`lambda/transform.py`)
- ✅ Can be tested locally with Python
- ✅ Includes local test mode in `__main__` section
- ✅ No AWS dependencies for core transformation logic

### 3. Scripts Adapted for Local Use
- ✅ `s3_setup.sh` - Skips bucket creation if no AWS credentials
- ✅ `deploy_lambda.sh` - Creates local deployment package
- ✅ `logs_fetch.sh` - Works with local log files

## Quick Start for Local Development

### 1. Setup Environment
```bash
cd northstar/02_mocktailverse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run FastAPI Test Harness
```bash
cd api
python test_harness.py

# Test at http://localhost:8000/docs
# Upload sample data via POST /ingest
```

### 3. Test Lambda Transformation Locally
```bash
cd lambda
python transform.py

# Tests transformation logic with sample data
# No AWS credentials required
```

### 4. Optional: Start LocalStack
```bash
# In separate terminal
localstack start

# Then run with LocalStack endpoint
export AWS_ENDPOINT_URL=http://localhost:4566
cd api && python test_harness.py
```

### 5. Optional: Start CockroachDB
```bash
# In separate terminal
docker run -d --name cockroachdb -p 26257:26257 cockroachdb/cockroach

# Update .env to use CockroachDB
echo "USE_COCKROACHDB=true" >> .env
echo "DATABASE_URL=postgresql://root@localhost:26257/defaultdb?sslmode=disable" >> .env
```

## Testing Without AWS Account

### Complete Local Workflow:
1. **Data Ingestion**: FastAPI receives and validates data
2. **Transformation**: Lambda logic processes locally
3. **Storage**: Local file system or optional database
4. **API Testing**: Full end-to-end testing via FastAPI

### Sample Test Commands:
```bash
# Test data ingestion
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d @data/raw/sample_data.json

# Check processing status
curl "http://localhost:8000/status/{job_id}"

# Get results
curl "http://localhost:8000/results"

# Reset data (for testing)
curl -X POST "http://localhost:8000/reset"
```

## Benefits of Local Development

- **No AWS Costs**: Everything runs locally
- **Faster Iteration**: No cloud deployment delays
- **Full Control**: Debug and modify as needed
- **Privacy**: Data never leaves your machine
- **Offline Development**: No internet required after setup

## When Ready for AWS Deployment

Once you have AWS credentials or want to use free tier:
1. Configure AWS CLI: `aws configure`
2. Run `./s3_setup.sh` to create buckets
3. Run `./deploy_lambda.sh` to deploy Lambda
4. Create DynamoDB table with provided schema

The same code works in both local and AWS environments!