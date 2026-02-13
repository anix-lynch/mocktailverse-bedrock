#!/bin/bash
# Simplified deployment - use existing infrastructure where possible

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_info() { echo -e "${BLUE}[i]${NC} $1"; }

REGION=us-west-2

print_info "Deploying Mocktailverse GenAI Platform (Simplified)"
echo ""

# Use existing DynamoDB table
TABLE_NAME="mocktailverse-metadata"

# Check if table exists, create if not
if ! aws dynamodb describe-table --table-name $TABLE_NAME --region $REGION &> /dev/null; then
    print_info "Creating DynamoDB table..."
    aws dynamodb create-table \
        --table-name $TABLE_NAME \
        --attribute-definitions \
            AttributeName=cocktail_id,AttributeType=S \
        --key-schema AttributeName=cocktail_id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region $REGION
    
    aws dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION
    print_status "DynamoDB table created"
else
    print_status "Using existing DynamoDB table"
fi

# Deploy Lambda functions using existing script
print_info "Deploying Lambda functions..."
./deploy-lambdas.sh

print_status "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Test ingestion: aws lambda invoke --function-name mocktailverse-ingest --payload '{\"fetch_type\":\"mocktails\",\"limit\":10}' response.json"
echo "2. Generate embeddings: aws lambda invoke --function-name mocktailverse-embed --payload '{}' response.json"
echo "3. Test search: aws lambda invoke --function-name mocktailverse-search --payload '{\"body\":\"{\\\"query\\\":\\\"refreshing drinks\\\",\\\"k\\\":3}\"}' response.json"
