# 👀 How to View Your AWS Data

## Option 1: AWS Console (Web Dashboard)

### Access Your Resources:

1. **DynamoDB Table** (Your Data)
   - Go to: https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables
   - Click: `mocktailverse-jobs`
   - Click: "Explore table items" to see your data

2. **S3 Buckets** (File Storage)
   - Go to: https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1
   - Click: `mocktailverse-processed` to see processed files
   - Click: `mocktailverse-raw` to see raw files

3. **Lambda Functions** (Your Code)
   - Go to: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
   - See: `mocktailverse-transform` and `mocktailverse-fetch-cocktails`
   - Click any function → "Monitor" tab to see logs/metrics

4. **CloudWatch Logs** (See What Happened)
   - Go to: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups
   - Look for: `/aws/lambda/mocktailverse-transform`
   - Look for: `/aws/lambda/mocktailverse-fetch-cocktails`

## Option 2: Command Line (Quick View)

### View DynamoDB Data (Your Table)
```bash
# See all records
aws dynamodb scan --table-name mocktailverse-jobs

# See first 5 records nicely formatted
aws dynamodb scan --table-name mocktailverse-jobs --limit 5 --query 'Items[*].[job_id.S,title.S,company.S]' --output table

# Count records
aws dynamodb scan --table-name mocktailverse-jobs --select COUNT
```

### View S3 Files
```bash
# List all processed files
aws s3 ls s3://mocktailverse-processed/ --recursive

# Download and view a file
aws s3 cp s3://mocktailverse-processed/cocktails/20251107_000106_cocktails.json ./view_file.json
cat view_file.json | python3 -m json.tool
```

### View Lambda Logs
```bash
# Recent logs from transform function
aws logs tail /aws/lambda/mocktailverse-transform --since 1h

# Recent logs from fetch function
aws logs tail /aws/lambda/mocktailverse-fetch-cocktails --since 1h
```

## Option 3: Quick Local Viewer Script

Run this to see your data in terminal:
```bash
./view_data.sh
```

