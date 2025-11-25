# 📁 Mocktailverse - Project Structure

```
mocktailverse/
├── README.md                    # Main project documentation
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment variables template
│
├── api/                         # FastAPI application
│   ├── test_harness.py          # Main API server
│   ├── test_harness_with_db.py  # Database-enabled version
│   └── test_cocktail_fetch.py   # Lambda testing utility
│
├── lambda/                      # AWS Lambda functions
│   ├── transform.py             # Data transformation Lambda
│   └── fetch_cocktails.py       # Cocktail API fetcher Lambda
│
├── scripts/                     # Deployment & utility scripts
│   ├── s3_setup.sh              # S3 bucket creation
│   ├── deploy_lambda.sh         # Transform Lambda deployment
│   ├── deploy_fetch_lambda.sh   # Fetch Lambda deployment
│   ├── setup_cockroachdb.sh     # Local DB setup (optional)
│   └── logs_fetch.sh            # CloudWatch logs utility
│
├── config/                      # Configuration files
│   └── dynamo_schema.json       # DynamoDB table schema
│
├── data/                        # Sample data
│   ├── raw/                     # Raw input data
│   │   └── sample_data.json
│   └── processed/               # Processed output (generated)
│
└── docs/                        # Documentation
    ├── DASHBOARD.md             # CEO-friendly dashboard
    ├── ETL_DASHBOARD.md         # Technical operations dashboard
    ├── ETL_METRICS.md           # ETL metrics & health index
    ├── STACK.md                 # Architecture stack diagram
    ├── hamberger_stack_for_B.md # Educational stack (with checkmarks)
    ├── deployment_guide_for_B.md # Step-by-step deployment guide
    ├── README_LOCAL_DEVELOPMENT.md
    ├── MCP_SERVERS_NEEDED.md
    ├── QUICK_SETUP.md
    ├── SIMPLE_SETUP.md
    └── DOCKER_READY.md
```

## Directory Purpose

- **`api/`** - FastAPI application for local testing and development
- **`lambda/`** - AWS Lambda function code (deployed to AWS)
- **`scripts/`** - Deployment and utility scripts
- **`config/`** - AWS resource configuration files
- **`data/`** - Sample data for testing
- **`docs/`** - All project documentation
