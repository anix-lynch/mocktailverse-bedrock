#!/bin/bash
# Phase 1: Screenshot Extraction Commands
# Run these commands and take screenshots of the output

echo "📸 Phase 1: Screenshot Commands"
echo "================================"
echo ""
echo "Run each command below and take a screenshot of the output"
echo ""

# 1. DynamoDB Table Data
echo "1️⃣  DynamoDB Table - Sample Records"
echo "-----------------------------------"
echo "Command:"
echo "aws dynamodb scan --table-name mocktailverse-jobs --limit 5 --query 'Items[*].[job_id.S,title.S,company.S,processed_at.S]' --output table"
echo ""
echo "Take screenshot of this output"
echo ""

# 2. DynamoDB Table Count
echo "2️⃣  DynamoDB Table - Record Count"
echo "--------------------------------"
echo "Command:"
echo "aws dynamodb scan --table-name mocktailverse-jobs --select COUNT"
echo ""
echo "Take screenshot of this output"
echo ""

# 3. S3 Raw Bucket Contents
echo "3️⃣  S3 Raw Bucket - File List"
echo "-----------------------------"
echo "Command:"
echo "aws s3 ls s3://mocktailverse-raw/ --recursive --human-readable"
echo ""
echo "Take screenshot of this output"
echo ""

# 4. S3 Processed Bucket Contents
echo "4️⃣  S3 Processed Bucket - File List"
echo "-----------------------------------"
echo "Command:"
echo "aws s3 ls s3://mocktailverse-processed/ --recursive --human-readable"
echo ""
echo "Take screenshot of this output"
echo ""

# 5. S3 Bucket Summary
echo "5️⃣  S3 Buckets - Storage Summary"
echo "-------------------------------"
echo "Command:"
echo "aws s3 ls s3://mocktailverse-raw/ --recursive --summarize --human-readable | tail -2"
echo "aws s3 ls s3://mocktailverse-processed/ --recursive --summarize --human-readable | tail -2"
echo ""
echo "Take screenshot of this output"
echo ""

# 6. Lambda Functions Status
echo "6️⃣  Lambda Functions - Status"
echo "----------------------------"
echo "Command:"
echo "aws lambda list-functions --query 'Functions[?contains(FunctionName, \`mocktailverse\`)].{Name:FunctionName,Status:State,LastModified:LastModified}' --output table"
echo ""
echo "Take screenshot of this output"
echo ""

# 7. CloudWatch Logs - Recent
echo "7️⃣  CloudWatch Logs - Recent Activity"
echo "-------------------------------------"
echo "Command:"
echo "aws logs tail /aws/lambda/mocktailverse-transform --since 24h --format short | head -20"
echo ""
echo "Take screenshot of this output"
echo ""

# 8. Lambda Metrics
echo "8️⃣  Lambda - Invocation Metrics"
echo "-------------------------------"
echo "Command:"
echo "aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --dimensions Name=FunctionName,Value=mocktailverse-transform --start-time \$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) --end-time \$(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum"
echo ""
echo "Take screenshot of this output"
echo ""

# 9. ETL Metrics Summary
echo "9️⃣  ETL Metrics - Quick Summary"
echo "-------------------------------"
echo "Command:"
echo "echo 'Records in DynamoDB:' && aws dynamodb scan --table-name mocktailverse-jobs --select COUNT --query 'Count' --output text && echo 'Files in S3 Processed:' && aws s3 ls s3://mocktailverse-processed/ --recursive | wc -l"
echo ""
echo "Take screenshot of this output"
echo ""

# 10. Pipeline Health Check
echo "🔟 Pipeline Health - All Services"
echo "--------------------------------"
echo "Command:"
echo "echo 'Lambda Functions:' && aws lambda list-functions --query 'Functions[?contains(FunctionName, \`mocktailverse\`)].FunctionName' --output text | wc -w && echo 'S3 Buckets:' && aws s3 ls | grep mocktailverse | wc -l && echo 'DynamoDB Table:' && aws dynamodb describe-table --table-name mocktailverse-jobs --query 'Table.TableStatus' --output text"
echo ""
echo "Take screenshot of this output"
echo ""

echo "✅ All commands listed above"
echo ""
echo "Next steps:"
echo "1. Run each command"
echo "2. Take screenshot of output"
echo "3. Save screenshots to docs/images/ folder"
echo "4. Update README with image paths"

