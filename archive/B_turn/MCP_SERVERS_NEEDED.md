# Mocktailverse - MCP Servers Needed

## Required MCP Servers

### 1. **filesystem** (Already Available)
- **Purpose**: Reading/writing local files
- **Usage**: Managing project structure, sample data, and configuration files
- **Status**: ✅ Already available in your environment

### 2. **docker** (Optional, for database containers)
- **Purpose**: Running CockroachDB or LocalStack containers
- **Usage**: If you want to use CockroachDB instead of DynamoDB
- **Installation**: Install Docker Desktop or Docker CLI
- **Status**: ⚠️ Optional - only needed for local database

### 3. **No Additional AWS MCP Servers Needed**
The project is designed to work without requiring any AWS-specific MCP servers:
- All AWS interactions are handled through boto3 in Python code
- No need for AWS S3, Lambda, or DynamoDB MCP servers
- Configuration is done through environment variables and CLI scripts

## Free Tier Development Options

### Option 1: AWS Free Tier (Recommended)
- **S3**: 5GB storage, 20,000 requests/month
- **Lambda**: 1M free requests per month, 400,000 GB-seconds of compute
- **DynamoDB**: 25GB storage, 25 provisioned RCU/WCU
- **Setup**: Configure AWS CLI with `aws configure`

### Option 2: Local Development (No AWS Account)
- **FastAPI Test Harness**: Runs locally with in-memory storage
- **CockroachDB**: Free open-source database (via Docker)
- **LocalStack**: Local AWS emulation (optional)
- **Setup**: No AWS credentials required

## Quick Start Commands

### For Local Development (No AWS):
```bash
# 1. Setup environment
cd northstar/02_mocktailverse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start CockroachDB (optional)
./setup_cockroachdb.sh setup

# 3. Run FastAPI test harness
cd api
python test_harness_with_db.py

# 4. Test at http://localhost:8000/docs
```

### For AWS Free Tier:
```bash
# 1. Configure AWS credentials
aws configure

# 2. Setup S3 buckets
./s3_setup.sh

# 3. Deploy Lambda function
./deploy_lambda.sh

# 4. Create DynamoDB table
aws dynamodb create-table --cli-input-json file://dynamo_schema.json

# 5. Run FastAPI test harness
cd api
python test_harness.py
```

## Project Architecture

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

## Testing Without AWS Account

### Complete Local Workflow:
1. **Data Ingestion**: FastAPI receives and validates data
2. **Transformation**: Lambda logic processes locally
3. **Storage**: Local file system or optional CockroachDB
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

## Summary

You only need:
1. **filesystem** MCP server (already available)
2. **docker** MCP server (optional, only for CockroachDB)

No AWS-specific MCP servers are required - all AWS interactions are handled through the Python code with boto3.