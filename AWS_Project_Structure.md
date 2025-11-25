# 🎯 AWS Serverless Project Structure Guide

## Overview
This guide shows typical folder organization patterns for AWS serverless projects, based on the Mocktailverse ETL pipeline project structure.

## 📁 Your Current Structure (Mocktailverse)

```
mocktailverse/
├── app.py                    # 🎨 Streamlit Dashboard (Frontend)
├── packages.txt              # 📦 Dependencies
├── .streamlit/               # ⚙️ Streamlit Config
│   ├── config.toml          # App configuration
│   └── secrets.toml         # AWS credentials template
├── lambda/                   # ⚡ AWS Lambda Functions
│   ├── transform.py         # ETL data processor
│   └── fetch_cocktails.py   # API data collector
├── api/                      # 🔌 Local API (Development)
│   ├── test_harness.py      # FastAPI testing server
│   └── view_dashboard.py    # Local data browser
├── config/                   # ⚙️ Infrastructure Config
│   └── dynamo_schema.json   # DynamoDB table schema
├── scripts/                  # 🚀 Deployment Scripts
│   ├── deploy_lambda.sh     # Lambda deployment
│   ├── deploy_fetch_lambda.sh # Fetch function deployment
│   └── s3_setup.sh          # S3 infrastructure setup
├── docs/                     # 📚 Documentation
│   ├── README.md            # Project overview
│   ├── DASHBOARD.md         # Live metrics
│   ├── ETL_METRICS.md       # Performance data
│   └── ETL_DASHBOARD.md     # Operations view
└── data/                     # 💾 Sample Data
    └── raw/                  # Input data samples
        └── README.md         # Data instructions
```

## 🏗️ STANDARD AWS ORGANIZATION PATTERNS

### Option 1: Service-Based (Your Current)
```
project/
├── lambda/                   # ⚡ All Lambda functions
├── api/                      # 🔌 API Gateway + local APIs
├── infrastructure/           # 🏗️ CloudFormation/Terraform
├── scripts/                  # 🚀 Deployment automation
├── src/                      # 💻 Shared utilities
└── tests/                    # 🧪 Test suites
```

### Option 2: Layer-Based (Infrastructure First)
```
project/
├── infrastructure/           # 🏗️ AWS resources (CF/TF)
│   ├── lambda/              # Lambda configs
│   ├── api-gateway/         # API configs
│   └── dynamodb/            # Table schemas
├── functions/               # ⚡ Lambda source code
├── web/                     # 🎨 Frontend (Streamlit/React)
└── scripts/                 # 🚀 Deploy scripts
```

### Option 3: Microservice-Style
```
project/
├── services/
│   ├── data-ingestion/      # 🏭 ETL Lambda
│   ├── api/                 # 🔌 API Gateway
│   └── dashboard/           # 🎨 Streamlit app
├── infrastructure/          # 🏗️ Shared resources
└── packages/               # 📦 Shared libraries
```

## 🎯 WHY YOUR STRUCTURE WORKS

### `lambda/` Folder
- ✅ Groups all serverless functions together
- ✅ Easy to find and deploy Lambda code
- ✅ Clear separation from local development code

### `api/` Folder
- ✅ Local FastAPI for testing before AWS deployment
- ✅ API Gateway configs and local simulation
- ✅ Development vs production API separation

### `config/` Folder
- ✅ Infrastructure-as-code definitions
- ✅ DynamoDB schemas, API specs
- ✅ Environment-specific configurations

### `scripts/` Folder
- ✅ All deployment automation
- ✅ One-command deployments
- ✅ Infrastructure setup scripts

## 🔧 AWS-SPECIFIC BEST PRACTICES

1. **Serverless Functions** → `lambda/` or `functions/`
2. **Infrastructure Code** → `infrastructure/` or `config/`
3. **Deployment Scripts** → `scripts/` or `deploy/`
4. **Local Development** → `api/` or `local/`
5. **Frontend Apps** → `web/` or `app/`
6. **Shared Code** → `src/` or `lib/`

## 📊 Mocktailverse Architecture

```
🎯 ETL Pipeline Flow:
Raw Data → S3 Bucket → Lambda Trigger → DynamoDB → Streamlit Dashboard

🏗️ Technology Stack:
• AWS Lambda (Serverless Compute)
• Amazon S3 (Object Storage)
• Amazon DynamoDB (NoSQL Database)
• Streamlit (Data Dashboard)
• TheCocktailDB API (Data Source)

⚡ Key Features:
• Zero infrastructure costs ($0/month)
• Event-driven processing
• Auto-scaling architecture
• Real-time data visualization
```

## 🎨 Project Evolution

**Phase 1: MVP** - Basic ETL pipeline with manual triggers
**Phase 2: Automation** - Event-driven processing via S3 triggers
**Phase 3: Monitoring** - CloudWatch metrics and logging
**Phase 4: Dashboard** - Streamlit visualization
**Phase 5: Production** - Multi-environment deployment

## 💡 Lessons Learned

1. **Start Simple** - Lambda + S3 + DynamoDB covers 80% of use cases
2. **Separate Concerns** - Keep local dev and AWS code separate
3. **Automate Everything** - Scripts for deployment and testing
4. **Monitor Costs** - AWS Free Tier is generous but has limits
5. **Document Architecture** - Self-documenting code with docstrings

---

**Built with ❤️ using AWS Serverless Architecture**
*Mocktailverse ETL Pipeline - Zero Infrastructure Cost Solution*</content>
</xai:function_call">AWS_Project_Structure.md
