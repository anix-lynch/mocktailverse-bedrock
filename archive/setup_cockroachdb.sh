#!/bin/bash

# Mocktailverse CockroachDB Setup Script
# Sets up CockroachDB as an alternative to DynamoDB for local development

set -e  # Exit on any error

# Configuration
CONTAINER_NAME="mocktailverse-cockroachdb"
DB_PORT=26257
DB_HOST="localhost"
DB_USER="root"
DB_NAME="defaultdb"
DATABASE_URL="postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME?sslmode=disable"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Function to start CockroachDB container
start_cockroachdb() {
    print_status "Starting CockroachDB container..."
    
    # Check if container already exists
    if docker ps -a --format "table" --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        print_warning "CockroachDB container already exists"
        
        # Check if it's running
        if docker ps --format "table" --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
            print_status "CockroachDB container is already running"
            return 0
        else
            print_status "Starting existing CockroachDB container..."
            docker start $CONTAINER_NAME
            return 0
        fi
    fi
    
    # Pull latest CockroachDB image
    print_status "Pulling CockroachDB Docker image..."
    docker pull cockroachdb/cockroach
    
    # Start new container
    print_status "Starting new CockroachDB container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $DB_PORT:$DB_PORT \
        cockroachdb/cockroach start-single-node \
        --insecure \
        --listen-addr=0.0.0.0
    
    if [ $? -eq 0 ]; then
        print_status "CockroachDB container started successfully"
    else
        print_error "Failed to start CockroachDB container"
        return 1
    fi
    
    # Wait for database to be ready
    print_status "Waiting for CockroachDB to be ready..."
    sleep 10
    
    # Test connection
    if docker exec $CONTAINER_NAME cockroach sql --insecure -e "SELECT 1;" &> /dev/null; then
        print_status "CockroachDB is ready for connections"
    else
        print_error "CockroachDB failed to start properly"
        return 1
    fi
}

# Function to stop CockroachDB container
stop_cockroachdb() {
    print_status "Stopping CockroachDB container..."
    
    if docker ps -a --format "table" --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        docker stop $CONTAINER_NAME
        print_status "CockroachDB container stopped"
    else
        print_warning "CockroachDB container is not running"
    fi
}

# Function to remove CockroachDB container
remove_cockroachdb() {
    print_status "Removing CockroachDB container..."
    
    if docker ps -a --format "table" --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        docker stop $CONTAINER_NAME
    fi
    
    if docker ps -a --format "table" --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        docker rm $CONTAINER_NAME
        print_status "CockroachDB container removed"
    else
        print_warning "CockroachDB container does not exist"
    fi
}

# Function to create database table
create_database_table() {
    print_status "Creating database table..."
    
    # Wait a bit more for database to be fully ready
    sleep 5
    
    # Create table using cockroach sql
    docker exec $CONTAINER_NAME cockroach sql --insecure << EOF
CREATE TABLE IF NOT EXISTS processed_jobs (
    job_id STRING PRIMARY KEY,
    title STRING NOT NULL,
    company STRING NOT NULL,
    location STRING NOT NULL,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency STRING NOT NULL DEFAULT 'USD',
    remote BOOLEAN NOT NULL DEFAULT FALSE,
    posted_date STRING NOT NULL,
    description STRING NOT NULL,
    requirements JSONB NOT NULL DEFAULT '[]',
    contact_email STRING NOT NULL,
    processed_at STRING NOT NULL,
    data_source STRING NOT NULL DEFAULT 'mocktailverse_ingest'
);
EOF
    
    if [ $? -eq 0 ]; then
        print_status "Database table created successfully"
    else
        print_error "Failed to create database table"
        return 1
    fi
}

# Function to show connection info
show_connection_info() {
    print_status "CockroachDB Connection Information:"
    echo "==============================="
    echo "Host: $DB_HOST"
    echo "Port: $DB_PORT"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    echo "Connection URL: $DATABASE_URL"
    echo ""
    echo "Environment Variables:"
    echo "======================"
    echo "export DATABASE_URL=\"$DATABASE_URL\""
    echo "export USE_COCKROACHDB=true"
    echo ""
    echo "Test Connection:"
    echo "================="
    echo "docker exec $CONTAINER_NAME cockroach sql --insecure"
}

# Function to display usage
usage() {
    echo "Mocktailverse CockroachDB Setup Script"
    echo "=================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start CockroachDB container"
    echo "  stop        Stop CockroachDB container"
    echo "  restart     Restart CockroachDB container"
    echo "  remove      Remove CockroachDB container"
    echo "  setup       Start CockroachDB and create table"
    echo "  info        Show connection information"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # Start and initialize CockroachDB"
    echo "  $0 info       # Show connection details"
    echo ""
}

# Main execution logic
case "${1:-}" in
    start)
        start_cockroachdb
        ;;
    stop)
        stop_cockroachdb
        ;;
    restart)
        stop_cockroachdb
        sleep 2
        start_cockroachdb
        ;;
    remove)
        remove_cockroachdb
        ;;
    setup)
        start_cockroachdb
        create_database_table
        show_connection_info
        ;;
    info)
        show_connection_info
        ;;
    --help|-h)
        usage
        exit 0
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac

print_status "CockroachDB setup completed!"