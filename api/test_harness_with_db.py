from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json
import boto3
import os
from datetime import datetime
import uuid
import logging

# Optional database support for local development
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mocktailverse Test Harness",
    description="Local FastAPI mock endpoint to simulate end-to-end flow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for data validation
class JobRequirement(BaseModel):
    skill: str
    level: Optional[str] = None

class JobListing(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    salary_range: Optional[str] = None
    remote: bool = False
    posted_date: str
    description: str
    requirements: List[str] = []
    contact_email: EmailStr

class TransformedJob(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    remote: bool
    posted_date: str
    description: str
    requirements: List[str] = []
    contact_email: str
    processed_at: str
    data_source: str = "mocktailverse_ingest"

class IngestResponse(BaseModel):
    message: str
    job_id: str
    status: str
    timestamp: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    timestamp: str

class ResultsResponse(BaseModel):
    jobs: List[TransformedJob]
    total_count: int
    timestamp: str

# In-memory storage for demo purposes
job_status_store = {}
processed_jobs_store = []

# AWS Configuration (for real AWS integration)
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
RAW_BUCKET = os.getenv('RAW_BUCKET', 'mocktailverse-raw')
PROCESSED_BUCKET = os.getenv('PROCESSED_BUCKET', 'mocktailverse-processed')

# Database Configuration
USE_COCKROACHDB = os.getenv('USE_COCKROACHDB', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', '')

# Database connection for CockroachDB
db_connection = None
if USE_COCKROACHDB and DATABASE_URL and PSYCOPG2_AVAILABLE:
    try:
        db_connection = psycopg2.connect(DATABASE_URL)
        logger.info("Connected to CockroachDB")
    except Exception as e:
        logger.error(f"Failed to connect to CockroachDB: {str(e)}")
        db_connection = None

# Initialize AWS clients if credentials are available
aws_clients = {}
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    aws_clients['s3'] = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    aws_clients['dynamodb'] = boto3.resource(
        'dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    logger.info("AWS clients initialized")
else:
    logger.warning("AWS credentials not found, running in mock mode")

def transform_job_data(job_data: JobListing) -> TransformedJob:
    """
    Transform job data (simplified version of Lambda logic)
    """
    # Extract salary information
    salary_min, salary_max = extract_salary_range(job_data.salary_range)
    
    # Normalize remote status
    remote = normalize_remote(job_data.remote)
    
    # Normalize date
    posted_date = normalize_date(job_data.posted_date)
    
    return TransformedJob(
        job_id=job_data.job_id,
        title=job_data.title.strip(),
        company=job_data.company.strip(),
        location=job_data.location.strip(),
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency="USD",
        remote=remote,
        posted_date=posted_date,
        description=job_data.description.strip(),
        requirements=[req.strip() for req in job_data.requirements if req.strip()],
        contact_email=job_data.contact_email.lower(),
        processed_at=datetime.utcnow().isoformat(),
        data_source="mocktailverse_ingest"
    )

def extract_salary_range(salary_range: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """
    Extract min and max salary from range string
    """
    if not salary_range:
        return None, None
    
    try:
        # Handle formats like "120k-180k" or "120000-180000"
        if '-' in salary_range:
            parts = salary_range.split('-')
            min_part = parts[0].strip()
            max_part = parts[1].strip()
            
            # Handle 'k' notation
            if 'k' in min_part.lower():
                salary_min = int(float(min_part.lower().replace('k', '')) * 1000)
            else:
                salary_min = int(min_part.replace(',', ''))
                
            if 'k' in max_part.lower():
                salary_max = int(float(max_part.lower().replace('k', '')) * 1000)
            else:
                salary_max = int(max_part.replace(',', ''))
                
            return salary_min, salary_max
    except (ValueError, AttributeError):
        pass
    
    return None, None

def normalize_remote(remote_value: bool) -> bool:
    """
    Normalize remote work boolean
    """
    return bool(remote_value)

def normalize_date(date_str: str) -> str:
    """
    Normalize date format
    """
    try:
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue
    except (ValueError, AttributeError):
        pass
    
    return date_str  # Return original if parsing fails

async def process_job_background(job_data: JobListing, job_id: str):
    """
    Background task to simulate Lambda processing
    """
    try:
        # Update status to processing
        job_status_store[job_id] = {
            "status": "processing",
            "progress": 50,
            "message": "Transforming job data...",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Transform data
        transformed_job = transform_job_data(job_data)
        
        # Update status to completed
        job_status_store[job_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Job processed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in processed jobs
        processed_jobs_store.append(transformed_job.dict())
        
        # If AWS is available, store in real services
        if 's3' in aws_clients:
            try:
                # Save to S3 processed bucket
                aws_clients['s3'].put_object(
                    Bucket=PROCESSED_BUCKET,
                    Key=f"processed/{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                    Body=json.dumps(transformed_job.dict(), indent=2),
                    ContentType='application/json'
                )
                logger.info(f"Saved job {job_id} to S3")
            except Exception as e:
                logger.error(f"Failed to save to S3: {str(e)}")
        
        if 'dynamodb' in aws_clients:
            try:
                # Save to DynamoDB
                table = aws_clients['dynamodb'].Table('mocktailverse-jobs')
                table.put_item(Item=transformed_job.dict())
                logger.info(f"Saved job {job_id} to DynamoDB")
            except Exception as e:
                logger.error(f"Failed to save to DynamoDB: {str(e)}")
        
        # If CockroachDB is available, store in database
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("""
                    INSERT INTO processed_jobs (
                        job_id, title, company, location, salary_min, salary_max,
                        salary_currency, remote, posted_date, description, requirements,
                        contact_email, processed_at, data_source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (job_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        location = EXCLUDED.location,
                        salary_min = EXCLUDED.salary_min,
                        salary_max = EXCLUDED.salary_max,
                        salary_currency = EXCLUDED.salary_currency,
                        remote = EXCLUDED.remote,
                        posted_date = EXCLUDED.posted_date,
                        description = EXCLUDED.description,
                        requirements = EXCLUDED.requirements,
                        contact_email = EXCLUDED.contact_email,
                        processed_at = EXCLUDED.processed_at,
                        data_source = EXCLUDED.data_source
                """, (
                    transformed_job.job_id, transformed_job.title, transformed_job.company,
                    transformed_job.location, transformed_job.salary_min, transformed_job.salary_max,
                    transformed_job.salary_currency, transformed_job.remote, transformed_job.posted_date,
                    transformed_job.description, json.dumps(transformed_job.requirements),
                    transformed_job.contact_email, transformed_job.processed_at, transformed_job.data_source
                ))
                db_connection.commit()
                logger.info(f"Saved job {job_id} to CockroachDB")
            except Exception as e:
                logger.error(f"Failed to save to CockroachDB: {str(e)}")
                if db_connection:
                    db_connection.rollback()
                
    except Exception as e:
        # Update status to failed
        job_status_store[job_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Processing failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(f"Job processing failed: {str(e)}")

# Create database table if needed
@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    """
    if USE_COCKROACHDB and db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
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
                )
            """)
            db_connection.commit()
            logger.info("CockroachDB table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Mocktailverse Test Harness",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "POST /ingest - Upload job data for processing",
            "status": "GET /status/{job_id} - Check processing status",
            "results": "GET /results - Retrieve processed data",
            "docs": "GET /docs - API documentation"
        },
        "aws_configured": bool(aws_clients),
        "database_configured": bool(db_connection),
        "database_type": "CockroachDB" if USE_COCKROACHDB else "None"
    }

@app.post("/ingest", response_model=IngestResponse)
async def ingest_job(job_data: JobListing, background_tasks: BackgroundTasks):
    """
    Upload job data for processing
    """
    try:
        # Generate unique job ID if not provided
        job_id = job_data.job_id or str(uuid.uuid4())
        
        # Initialize job status
        job_status_store[job_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Job queued for processing",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_job_background, job_data, job_id)
        
        return IngestResponse(
            message="Job data received and queued for processing",
            job_id=job_id,
            status="queued",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Ingest error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """
    Check processing status of a job
    """
    if job_id not in job_status_store:
        raise HTTPException(status_code=404, detail="Job ID not found")
    
    status_data = job_status_store[job_id]
    return StatusResponse(**status_data, job_id=job_id)

@app.get("/results", response_model=ResultsResponse)
async def get_results():
    """
    Retrieve all processed job data
    """
    # If CockroachDB is available, query from database
    if USE_COCKROACHDB and db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM processed_jobs ORDER BY processed_at DESC")
            rows = cursor.fetchall()
            
            # Convert rows to TransformedJob objects
            jobs = []
            for row in rows:
                job_dict = {
                    'job_id': row[0],
                    'title': row[1],
                    'company': row[2],
                    'location': row[3],
                    'salary_min': row[4],
                    'salary_max': row[5],
                    'salary_currency': row[6],
                    'remote': row[7],
                    'posted_date': row[8],
                    'description': row[9],
                    'requirements': json.loads(row[10]) if row[10] else [],
                    'contact_email': row[11],
                    'processed_at': row[12],
                    'data_source': row[13]
                }
                jobs.append(job_dict)
            
            return ResultsResponse(
                jobs=jobs,
                total_count=len(jobs),
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Failed to query CockroachDB: {str(e)}")
            # Fallback to in-memory storage
            return ResultsResponse(
                jobs=processed_jobs_store,
                total_count=len(processed_jobs_store),
                timestamp=datetime.utcnow().isoformat()
            )
    else:
        # Use in-memory storage
        return ResultsResponse(
            jobs=processed_jobs_store,
            total_count=len(processed_jobs_store),
            timestamp=datetime.utcnow().isoformat()
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "aws_configured": bool(aws_clients),
        "database_configured": bool(db_connection),
        "database_type": "CockroachDB" if USE_COCKROACHDB else "None",
        "processed_jobs": len(processed_jobs_store),
        "active_jobs": len(job_status_store)
    }

@app.post("/reset")
async def reset_data():
    """
    Reset all data (for testing purposes)
    """
    global job_status_store, processed_jobs_store
    job_status_store.clear()
    processed_jobs_store.clear()
    
    # Clear database if available
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("DELETE FROM processed_jobs")
            db_connection.commit()
            logger.info("Cleared CockroachDB table")
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
    
    return {
        "message": "All data reset",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)