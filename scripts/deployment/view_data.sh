#!/bin/bash

# Quick Data Viewer for Mocktailverse
# Shows what's in your AWS resources

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Mocktailverse - Data Viewer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

# DynamoDB Data
echo -e "${YELLOW}📊 DynamoDB Table: mocktailverse-jobs${NC}"
echo "─────────────────────────────────────────────────────"
RECORD_COUNT=$(aws dynamodb scan --table-name mocktailverse-jobs --select COUNT --query 'Count' --output text 2>/dev/null || echo "0")
echo "Total Records: $RECORD_COUNT"
echo ""

if [ "$RECORD_COUNT" -gt 0 ]; then
    echo "Sample Records:"
    aws dynamodb scan --table-name mocktailverse-jobs --limit 5 \
        --query 'Items[*].[job_id.S,title.S,company.S]' \
        --output table 2>/dev/null || echo "  (Unable to fetch)"
else
    echo "  No records yet"
fi
echo ""

# S3 Files
echo -e "${YELLOW}📁 S3 Processed Files${NC}"
echo "─────────────────────────────────────────────────────"
FILE_COUNT=$(aws s3 ls s3://mocktailverse-processed/ --recursive 2>/dev/null | wc -l | tr -d ' ')
echo "Total Files: $FILE_COUNT"
echo ""
echo "Recent Files:"
aws s3 ls s3://mocktailverse-processed/ --recursive 2>/dev/null | tail -5 || echo "  (Unable to fetch)"
echo ""

# Lambda Status
echo -e "${YELLOW}⚡ Lambda Functions${NC}"
echo "─────────────────────────────────────────────────────"
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mocktailverse`)].FunctionName' --output table 2>/dev/null || echo "  (Unable to fetch)"
echo ""

# Quick Actions
echo -e "${GREEN}💡 Quick Actions:${NC}"
echo "  • View in AWS Console: See VIEW_YOUR_DATA.md"
echo "  • Fetch more data: aws lambda invoke --function-name mocktailverse-fetch-cocktails --payload '{\"fetch_type\":\"mocktails\",\"limit\":3}' response.json"
echo "  • View logs: aws logs tail /aws/lambda/mocktailverse-transform --since 1h"
echo ""

