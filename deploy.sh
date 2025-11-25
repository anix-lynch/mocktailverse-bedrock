#!/bin/bash
# Complete deployment script for Mocktailverse GenAI Platform

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
print_info() { echo -e "${BLUE}[i]${NC} $1"; }

echo "========================================="
echo "  Mocktailverse GenAI Platform Deploy"
echo "========================================="
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI not found"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform not found"
    exit 1
fi

REGION=${AWS_DEFAULT_REGION:-us-west-2}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

print_status "AWS Account: $ACCOUNT_ID"
print_status "Region: $REGION"
echo ""

# Step 1: Package Lambda functions
print_info "Step 1/4: Packaging Lambda functions..."

FUNCTIONS=("ingest" "embed" "search" "rag")

for FUNC in "${FUNCTIONS[@]}"; do
    print_status "Packaging $FUNC..."
    
    cd "lambdas/$FUNC"
    
    rm -rf package deployment.zip
    mkdir -p package
    
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt -t package/ --quiet
    fi
    
    cp handler.py package/
    
    cd package
    zip -r ../deployment.zip . > /dev/null
    cd ../..
done

print_status "All Lambda functions packaged"
echo ""

# Step 2: Deploy infrastructure with Terraform
print_info "Step 2/4: Deploying AWS infrastructure..."

cd terraform

terraform init -upgrade

print_warn "Terraform will create AWS resources. Review the plan carefully."
terraform plan

read -p "Deploy infrastructure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

terraform apply -auto-approve

# Get outputs
API_ENDPOINT=$(terraform output -raw api_endpoint)
CLOUDFRONT_URL=$(terraform output -raw cloudfront_url)
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket)

cd ..

print_status "Infrastructure deployed"
echo ""

# Step 3: Run initial data ingestion
print_info "Step 3/4: Running initial data ingestion..."

print_status "Fetching 20 mocktails from API..."
aws lambda invoke \
    --function-name mocktailverse-ingest \
    --payload '{"fetch_type":"mocktails","limit":20}' \
    --region $REGION \
    /tmp/ingest_response.json > /dev/null

print_status "Generating embeddings..."
aws lambda invoke \
    --function-name mocktailverse-embed \
    --payload '{}' \
    --region $REGION \
    /tmp/embed_response.json > /dev/null

print_status "Initial data loaded"
echo ""

# Step 4: Test the API
print_info "Step 4/4: Testing API endpoints..."

print_status "Testing search endpoint..."
curl -s -X POST "$API_ENDPOINT/v1/search" \
    -H "Content-Type: application/json" \
    -d '{"query":"refreshing summer drinks","k":3}' | jq '.count'

print_status "Testing RAG endpoint..."
curl -s -X POST "$API_ENDPOINT/v1/rag" \
    -H "Content-Type: application/json" \
    -d '{"question":"What makes a good mojito?"}' | jq -r '.answer' | head -n 3

echo ""
print_status "API endpoints working!"
echo ""

# Summary
echo "========================================="
echo "  Deployment Complete!"
echo "========================================="
echo ""
echo "📊 API Endpoint:"
echo "   $API_ENDPOINT"
echo ""
echo "🌐 CloudFront URL (frontend will be here):"
echo "   $CLOUDFRONT_URL"
echo ""
echo "📦 Frontend Bucket:"
echo "   $FRONTEND_BUCKET"
echo ""
echo "Next steps:"
echo "1. Build Next.js frontend: cd frontend && npm run build"
echo "2. Deploy frontend: aws s3 sync out/ s3://$FRONTEND_BUCKET"
echo "3. Update gozeroshot.dev to link to: $CLOUDFRONT_URL"
echo ""
print_status "System ready for use!"
