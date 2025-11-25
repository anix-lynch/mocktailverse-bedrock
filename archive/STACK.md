───────────────────────────────🍹 MOCKTAILVERSE STACK───────────────────────────────

          ( 🎨 FRONTEND – The User Interface )

        ┌──────────────────────────────────────────────────┐

        │ ✨ FastAPI Test Harness (Local development UI)   │

        │ 📊 Interactive API docs at /docs endpoint       │

        │ 🧪 End-to-end testing & data ingestion interface │

        │ 🚀 Ready for React/Vite frontend integration     │

        └──────────────────────────────────────────────────┘

                           │  ▲

                           │  │ HTTP/HTTPS API calls

                           ▼  │

        ┌──────────────────────────────────────────────────┐

        │ ⚙️ MID LAYER (The Processing Engine)              │

        │ 🚪 S3 Event Triggers (Automatic pipeline start)  │

        │ ⚡ Lambda: mocktailverse-transform                │

        │    (Transforms raw data → processed format)       │

        │ ⚡ Lambda: mocktailverse-fetch-cocktails          │

        │    (Fetches from TheCocktailDB API)              │

        │ 🏃‍♀️ FastAPI (Optional local orchestration)        │

        └──────────────────────────────────────────────────┘

                           │  ▲

                           │  │ S3 Events, API Calls, Direct Invocation

                           ▼  │

        ┌──────────────────────────────────────────────────┐

        │ 💾 BACKEND (The Data Foundation)                 │

        │ 📦 S3 Raw Bucket (Incoming data storage)         │

        │ 📦 S3 Processed Bucket (Transformed data)         │

        │ 🗄️ DynamoDB (Structured data warehouse)          │

        │ 🍸 TheCocktailDB API (External data source)      │

        │ 📊 CloudWatch (Monitoring & logging)             │

        │ 🔐 IAM Roles & Policies (Security & permissions) │

        └──────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────────────────

   🛠️ Tools: AWS CLI, boto3, Python, Pydantic (data validation)

   ☁️ Deployment: AWS Serverless (Lambda, S3, DynamoDB)

   💰 Cost: $0/month (AWS Free Tier eligible)

───────────────────────────────────────────────────────────────────────────────────

## Architecture Flow

```
┌──────────────┐
│  External    │
│   APIs       │──┐
└──────────────┘  │
                  │
┌──────────────┐  │    ┌──────────────┐
│  FastAPI     │──┼───▶│  S3 Raw      │
│  Test Harness│  │    │  Bucket      │
└──────────────┘  │    └──────┬───────┘
                  │           │
                  │           │ (S3 Event Trigger)
                  │           ▼
                  │    ┌──────────────┐
                  │    │   Lambda     │
                  │    │  Transform   │
                  │    └──────┬───────┘
                  │           │
                  │    ┌───────┴───────┐
                  │    │               │
                  ▼    ▼               ▼
            ┌──────────┐      ┌──────────┐
            │ DynamoDB  │      │ S3 Processed │
            │  Table    │      │   Bucket     │
            └──────────┘      └──────────────┘
```

## Service Details

**Frontend Layer:**
- FastAPI with auto-generated Swagger UI
- RESTful API endpoints for data ingestion
- Real-time status monitoring
- Ready for frontend framework integration

**Processing Layer:**
- **Lambda Transform:** Event-driven data transformation
- **Lambda Fetch:** Scheduled/on-demand API data fetching
- **S3 Triggers:** Automatic pipeline activation
- **Error Handling:** Built-in retry logic & dead-letter queues

**Data Layer:**
- **S3 Raw:** Landing zone for incoming data
- **S3 Processed:** Clean, transformed data storage
- **DynamoDB:** Fast, scalable NoSQL database
- **CloudWatch:** Centralized logging & metrics

**External Services:**
- **TheCocktailDB API:** Free cocktail recipe data source
- **Future:** Spoonacular/Edamam for non-alcoholic drinks

## Key Features

✅ **Serverless Architecture** - No servers to manage  
✅ **Auto-Scaling** - Handles traffic spikes automatically  
✅ **Event-Driven** - S3 uploads trigger processing  
✅ **Cost-Effective** - $0/month on free tier  
✅ **Production-Ready** - Error handling & monitoring  
✅ **Scalable** - Handles 10x growth without changes

## Data Flow

1. **Ingestion:** Data arrives via FastAPI or direct S3 upload
2. **Trigger:** S3 event automatically invokes Lambda
3. **Transform:** Lambda normalizes, validates, enriches data
4. **Store:** Processed data saved to DynamoDB + S3
5. **Monitor:** CloudWatch tracks all operations

## Security

- IAM roles with least-privilege access
- S3 bucket encryption enabled
- DynamoDB encryption at rest
- VPC endpoints (optional for production)
- API authentication ready

