#!/bin/bash

# Mocktailverse CloudWatch Logs and Cost Estimation Script
# Fetches Lambda logs and provides cost estimation via boto3 CLI wrapper

set -e  # Exit on any error

# Configuration
FUNCTION_NAME="mocktailverse-transform"
LOG_GROUP="/aws/lambda/$FUNCTION_NAME"
REGION=${AWS_REGION:-"us-east-1"}
DAYS_BACK=${1:-7}  # Default to last 7 days

# Load configuration if available
if [ -f ".env" ]; then
    source .env
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Function to fetch CloudWatch logs
fetch_cloudwatch_logs() {
    local hours_back=$1
    print_header "CloudWatch Logs (Last $hours_back hours)"
    
    # Calculate start time
    start_time=$(date -u -d "$hours_back hours ago" '+%Y-%m-%dT%H:%M:%SZ')
    
    # Fetch log streams
    print_status "Fetching log streams..."
    log_streams=$(aws logs describe-log-streams \
        --log-group-name $LOG_GROUP \
        --region $REGION \
        --order-by LastEventTime \
        --descending \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$log_streams" ]; then
        print_warning "No log streams found for function: $FUNCTION_NAME"
        return 1
    fi
    
    # Fetch log events
    print_status "Fetching log events..."
    aws logs get-log-events \
        --log-group-name $LOG_GROUP \
        --log-stream-name "$log_streams" \
        --region $REGION \
        --start-time $(date -d "$start_time" +%s)000 \
        --query 'events[*].[timestamp,message]' \
        --output table
    
    echo ""
}

# Function to get Lambda metrics
get_lambda_metrics() {
    print_header "Lambda Performance Metrics (Last $DAYS_BACK days)"
    
    # Calculate start time for metrics
    start_time=$(date -u -d "$DAYS_BACK days ago" '+%Y-%m-%dT%H:%M:%SZ')
    
    # Get CloudWatch metrics
    print_status "Fetching Lambda metrics..."
    
    # Invocations
    invocations=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Invocations \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --start-time $start_time \
        --end-time $(date -u '+%Y-%m-%dT%H:%M:%SZ') \
        --period 3600 \
        --statistics Sum \
        --region $REGION \
        --query 'Datapoints[0].Sum' \
        --output text 2>/dev/null || echo "0")
    
    # Duration
    avg_duration=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Duration \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --start-time $start_time \
        --end-time $(date -u '+%Y-%m-%dT%H:%M:%SZ') \
        --period 3600 \
        --statistics Average \
        --region $REGION \
        --query 'Datapoints[0].Average' \
        --output text 2>/dev/null || echo "0")
    
    # Errors
    errors=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Errors \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --start-time $start_time \
        --end-time $(date -u '+%Y-%m-%dT%H:%M:%SZ') \
        --period 3600 \
        --statistics Sum \
        --region $REGION \
        --query 'Datapoints[0].Sum' \
        --output text 2>/dev/null || echo "0")
    
    # Throttles
    throttles=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Throttles \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --start-time $start_time \
        --end-time $(date -u '+%Y-%m-%dT%H:%M:%SZ') \
        --period 3600 \
        --statistics Sum \
        --region $REGION \
        --query 'Datapoints[0].Sum' \
        --output text 2>/dev/null || echo "0")
    
    # Display metrics
    echo "Metric Summary:"
    echo "================"
    printf "%-15s %10s\n" "Metric" "Value"
    printf "%-15s %10s\n" "Invocations" "${invocations:-0}"
    printf "%-15s %10.2f ms\n" "Avg Duration" "${avg_duration:-0}"
    printf "%-15s %10s\n" "Errors" "${errors:-0}"
    printf "%-15s %10s\n" "Throttles" "${throttles:-0}"
    
    # Calculate error rate
    if [ "${invocations:-0}" -gt 0 ]; then
        error_rate=$(echo "scale=2; ${errors:-0} * 100 / $invocations" | bc 2>/dev/null || echo "0")
        printf "%-15s %10.2f%%\n" "Error Rate" "$error_rate"
    fi
    
    echo ""
}

# Function to estimate costs
estimate_costs() {
    print_header "Cost Estimation (Last $DAYS_BACK days)"
    
    # Get Lambda configuration
    memory_size=$(aws lambda get-function \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query 'Configuration.MemorySize' \
        --output text 2>/dev/null || echo "256")
    
    # Calculate costs based on AWS pricing (us-east-1 rates)
    # Lambda pricing: $0.0000166667 per GB-second
    # Request pricing: $0.20 per 1M requests
    
    # Convert MB to GB
    memory_gb=$(echo "scale=3; $memory_size / 1024" | bc 2>/dev/null || echo "0.256")
    
    # Estimate compute cost
    # Assuming average execution time from metrics or default 100ms
    avg_duration_ms=${avg_duration:-100}
    duration_seconds=$(echo "scale=6; $avg_duration_ms / 1000" | bc 2>/dev/null || echo "0.1")
    
    # GB-seconds per invocation
    gb_seconds_per_invoke=$(echo "scale=6; $memory_gb * $duration_seconds" | bc 2>/dev/null || echo "0")
    
    # Total GB-seconds
    total_gb_seconds=$(echo "scale=6; $gb_seconds_per_invoke * ${invocations:-0}" | bc 2>/dev/null || echo "0")
    
    # Compute cost
    compute_cost=$(echo "scale=4; $total_gb_seconds * 0.0000166667" | bc 2>/dev/null || echo "0")
    
    # Request cost
    request_cost=$(echo "scale=4; ${invocations:-0} / 1000000 * 0.20" | bc 2>/dev/null || echo "0")
    
    # Total Lambda cost
    total_lambda_cost=$(echo "scale=4; $compute_cost + $request_cost" | bc 2>/dev/null || echo "0")
    
    # Estimate data transfer costs (simplified)
    # S3 storage: $0.023 per GB-month
    # S3 requests: $0.0004 per 1K PUT/GET requests
    # DynamoDB: $0.00025 per write request, $0.000125 per read request
    
    # Assume average data size and operations
    avg_data_size_kb=5  # Average job listing size
    s3_put_requests=${invocations:-0}
    s3_get_requests=${invocations:-0}  # Assume 1:1 read ratio
    dynamo_writes=${invocations:-0}
    dynamo_reads=${invocations:-0}  # Assume 1:1 read ratio
    
    # S3 costs
    s3_request_cost=$(echo "scale=4; ($s3_put_requests + $s3_get_requests) / 1000 * 0.0004" | bc 2>/dev/null || echo "0")
    
    # DynamoDB costs
    dynamo_cost=$(echo "scale=4; ($dynamo_writes * 0.00025) + ($dynamo_reads * 0.000125)" | bc 2>/dev/null || echo "0")
    
    # Total estimated cost
    total_cost=$(echo "scale=4; $total_lambda_cost + $s3_request_cost + $dynamo_cost" | bc 2>/dev/null || echo "0")
    
    # Display cost breakdown
    echo "Cost Breakdown (USD):"
    echo "======================="
    printf "%-20s %10s %10.4f\n" "Lambda Compute" "$compute_cost"
    printf "%-20s %10s %10.4f\n" "Lambda Requests" "$request_cost"
    printf "%-20s %10s %10.4f\n" "S3 Requests" "$s3_request_cost"
    printf "%-20s %10s %10.4f\n" "DynamoDB Ops" "$dynamo_cost"
    printf "%-20s %10s %10.4f\n" "----------------" "----------"
    printf "%-20s %10s %10.4f\n" "TOTAL ESTIMATED" "$total_cost"
    
    # Monthly projection
    daily_avg=$(echo "scale=4; $total_cost / $DAYS_BACK" | bc 2>/dev/null || echo "0")
    monthly_projection=$(echo "scale=2; $daily_avg * 30" | bc 2>/dev/null || echo "0")
    printf "%-20s %10s %10.2f\n" "Monthly Projection" "$monthly_projection"
    
    echo ""
    print_warning "These are estimates based on current usage patterns"
    print_warning "Actual costs may vary based on data volume and usage patterns"
    echo ""
}

# Function to get recent errors
get_recent_errors() {
    print_header "Recent Lambda Errors (Last 24 hours)"
    
    # Calculate start time (24 hours ago)
    start_time=$(date -u -d "24 hours ago" '+%Y-%m-%dT%H:%M:%SZ')
    
    # Filter logs for errors
    aws logs filter-log-events \
        --log-group-name $LOG_GROUP \
        --region $REGION \
        --start-time $(date -d "$start_time" +%s)000 \
        --filter-pattern "?ERROR ? ?Exception ? ?Traceback" \
        --query 'events[*].[timestamp,message]' \
        --output table 2>/dev/null || print_warning "No error logs found"
    
    echo ""
}

# Function to display usage summary
usage_summary() {
    echo "Mocktailverse Logs and Cost Monitoring Tool"
    echo "======================================"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  [hours]        Fetch logs for specified hours (default: 7)"
    echo "  --metrics       Show performance metrics only"
    echo "  --costs         Show cost estimation only"
    echo "  --errors         Show recent errors only"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 24           # Fetch logs for last 24 hours"
    echo "  $0 --metrics     # Show metrics for last 7 days"
    echo "  $0 --costs       # Show cost estimation for last 7 days"
    echo "  $0 --errors      # Show recent errors"
    echo ""
}

# Main execution logic
main() {
    case "${1:-}" in
        --help|-h)
            usage_summary
            exit 0
            ;;
        --metrics)
            get_lambda_metrics
            ;;
        --costs)
            estimate_costs
            ;;
        --errors)
            get_recent_errors
            ;;
        *)
            # Default: show all information
            fetch_cloudwatch_logs "${1:-7}"
            get_lambda_metrics
            estimate_costs
            get_recent_errors
            ;;
    esac
    
    print_status "Log and cost analysis completed"
    echo "For detailed AWS billing, visit: https://console.aws.amazon.com/billing/"
}

# Check for required tools
if ! command -v bc &> /dev/null; then
    print_warning "bc calculator not found. Cost calculations may be limited."
fi

# Run main function
main "$@"