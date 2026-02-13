# 📁 Project Structure

> **Clean, interview-friendly organization**

---

## Production Folders (Review These)

```
mocktailverse-bedrock/
│
├── 🌐 frontend/                      # Next.js 14 UI
│   ├── app/
│   │   ├── page.tsx                  # Main UI
│   │   ├── layout.tsx                # Root layout
│   │   ├── globals.css               # Styles
│   │   └── components/               # React components
│   ├── public/                       # Static assets
│   ├── next.config.js                # Static export config
│   └── package.json                  # Dependencies
│
├── ⚙️ backend/lambdas/               # GenAI Runtime (Python)
│   ├── agent/
│   │   ├── handler.py                # Bedrock Agent orchestrator
│   │   └── requirements.txt
│   ├── rag/
│   │   ├── handler.py                # RAG pipeline
│   │   └── requirements.txt
│   ├── search/
│   │   ├── handler.py                # Vector KNN search
│   │   └── requirements.txt
│   ├── embed/
│   │   ├── handler.py                # Titan Embeddings
│   │   └── requirements.txt
│   ├── ingest/
│   │   ├── handler.py                # Data ingestion + LLM enrichment
│   │   └── requirements.txt
│   └── search_tool/
│       ├── handler.py                # Tool wrapper
│       └── requirements.txt
│
├── 🏗️ infra/terraform/              # Infrastructure as Code
│   └── main.tf                       # AWS resource definitions
│
├── 🔄 workflows/                     # Orchestration
│   └── README.md                     # EventBridge/Step Functions docs
│
├── 📜 scripts/                       # DevOps utilities
│   └── deployment/                   # Deploy scripts
│
└── 📖 docs/                          # Architecture & Guides
    ├── architecture/
    │   ├── GENAI_FLOW_MAPPING.md     # GenAI mental model → code
    │   └── ARCHITECTURE.md           # System design
    ├── TECHNICAL_OVERVIEW.md         # Deep technical dive
    ├── BEDROCK_ACCESS_GUIDE.md       # AWS Bedrock setup
    └── DEPLOYMENT_GUIDE.md           # How to deploy
```

---

## Reference/Archive Folders (Skip for Interviews)

```
├── archive/                          # Old experiments
├── data/                             # Sample data files
├── lambdas/                          # Old Lambda structure (use backend/ instead)
└── _deprecated/                      # Legacy code (not in production)
    ├── lambda/
    └── legacy/
```

---

## Key Files to Review

### For Interviews:
1. **`WALKTHROUGH.md`** - 5-minute technical walkthrough
2. **`docs/architecture/GENAI_FLOW_MAPPING.md`** - Mental model mapping
3. **`backend/lambdas/*/handler.py`** - Production GenAI code
4. **`README.md`** - High-level overview

### For Deployment:
1. **`frontend/next.config.js`** - Vercel config
2. **`infra/terraform/main.tf`** - AWS infrastructure
3. **`scripts/deployment/`** - Deploy scripts
4. **`.env.example`** - Required environment variables

---

## What Each Lambda Does

| Lambda | Purpose | Trigger | Tech |
|--------|---------|---------|------|
| **ingest** | Fetch data from API, enrich with LLM | EventBridge schedule | Bedrock Titan Text Lite |
| **embed** | Generate 1536-dim embeddings | S3 upload or manual | Bedrock Titan Embeddings v2 |
| **search** | KNN similarity search | API Gateway `/search` | DynamoDB scan + cosine similarity |
| **rag** | Retrieve context + generate answer | API Gateway `/rag` | Calls search → Bedrock generation |
| **agent** | Conversational AI with tools | API Gateway `/agent/chat` | Bedrock Agents (fallback mode) |
| **search_tool** | Tool wrapper for agent | Bedrock Agent invocation | DynamoDB query wrapper |

---

## Data Flow

```
TheCocktailDB API
    ↓
Lambda: ingest (fetch + LLM enrich)
    ↓
S3: mocktailverse-processed
    ↓
Lambda: embed (vectorize)
    ↓
DynamoDB: mocktailverse-metadata
    ↓
User Query → API Gateway
    ↓
Lambda: search (KNN)
    ↓
Lambda: rag (context assembly)
    ↓
Bedrock: generation
    ↓
User sees answer
```

---

## Deployed Resources (AWS Account 340752826866)

### Lambda Functions (8)
```
mocktailverse-agent
mocktailverse-rag
mocktailverse-search
mocktailverse-search-tool
mocktailverse-embed
mocktailverse-ingest
mocktailverse-transform
mocktailverse-fetch-cocktails
```

### S3 Buckets (6)
```
mocktailverse-raw-340752826866
mocktailverse-processed-340752826866
mocktailverse-embeddings-340752826866
mocktailverse-frontend-340752826866
```

### DynamoDB Tables (3)
```
mocktailverse-cocktails      (Recipe metadata)
mocktailverse-metadata       (Embeddings + search index)
mocktailverse-jobs           (Processing status)
```

### API Gateway
```
https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod
```

### Frontend (Vercel)
```
https://gozeroshot.dev/mocktailverse
```

---

## Git Workflow

```bash
# Current state
git status  # Clean, no uncommitted changes

# Archive old folders (already done)
ls _deprecated/  # Contains legacy code

# Production code is in:
ls backend/lambdas/  # All 6 Lambda handlers
ls frontend/app/     # Next.js UI
ls docs/architecture/  # Documentation
```

---

## For Next AI Agent

**Production paths:**
- `backend/lambdas/` - Current Lambda functions
- `frontend/` - Next.js UI
- `infra/terraform/` - Infrastructure
- `docs/architecture/` - System design docs

**Ignore these:**
- `lambdas/` - Old structure (superseded by backend/)
- `_deprecated/` - Legacy experiments
- `archive/` - Old data files

**Status:** ✅ Clean and interview-ready (as of 2025-02-12)
