# 🚀 START HERE - Learning This Repo

> **Follow this guide to understand the codebase in 30 minutes**

---

## Step 1: Understand the Flow (5 min)

Read: [`docs/architecture/GENAI_FLOW_MAPPING.md`](architecture/GENAI_FLOW_MAPPING.md)

**What you'll learn:**
- How data flows through the system
- What each Lambda does
- How frontend → API → Lambda → Bedrock works

---

## Step 2: Walk Through Each Component (20 min)

### A. Frontend (5 min)
```
frontend/app/page.tsx     ← Main UI (read this first)
frontend/app/layout.tsx   ← Root layout
```

**What to look for:**
- Line 30: How API calls are made
- Search interface logic
- Response rendering

### B. Backend Lambdas (10 min)

**Order to read:**

1. **`backend/lambdas/ingest/handler.py`** (Data Pipeline)
   - How we fetch from TheCocktailDB API
   - How Bedrock enriches data
   - How we store in DynamoDB

2. **`backend/lambdas/embed/handler.py`** (Embeddings)
   - How we generate 1536-dim vectors
   - Titan Embeddings v2 usage

3. **`backend/lambdas/search/handler.py`** (Vector Search)
   - DynamoDB KNN implementation
   - Cosine similarity logic

4. **`backend/lambdas/rag/handler.py`** (RAG Pipeline)
   - How we retrieve context
   - How we call Bedrock for generation
   - Prompt engineering

5. **`backend/lambdas/agent/handler.py`** (Agent)
   - Bedrock Agents integration
   - Tool calling logic

6. **`backend/lambdas/search_tool/handler.py`** (Tool Wrapper)
   - How tools are exposed to agent

### C. Infrastructure (5 min)
```
infra/terraform/main.tf   ← AWS resources
```

**What to look for:**
- Lambda definitions
- DynamoDB tables
- S3 buckets
- API Gateway config

---

## Step 3: Interview Prep (5 min)

Read: [`docs/WALKTHROUGH.md`](WALKTHROUGH.md)

**What you'll learn:**
- 5-minute technical walkthrough script
- Common interview questions
- How to explain tradeoffs

---

## Navigation Guide

### Production Code (Focus Here)
```
backend/lambdas/      ← GenAI runtime (Python)
frontend/app/         ← UI (Next.js)
infra/terraform/      ← Infrastructure (Terraform)
docs/architecture/    ← System design
```

### Reference (Skim If Needed)
```
scripts/deployment/   ← Deploy scripts
workflows/            ← Orchestration docs
```

### Ignore for Learning
```
_deprecated/          ← Old code (hidden)
archive/              ← Old experiments (hidden)
lambdas/              ← Duplicate of backend/ (hidden)
data/                 ← Sample data (hidden)
```

---

## Learning Path for Different Roles

### 1. GenAI Data Engineer (Your Target)
**Focus:** RAG pipeline, embeddings, vector search

**Read in order:**
1. `docs/architecture/GENAI_FLOW_MAPPING.md`
2. `backend/lambdas/ingest/handler.py`
3. `backend/lambdas/embed/handler.py`
4. `backend/lambdas/search/handler.py`
5. `backend/lambdas/rag/handler.py`

**Key concepts to master:**
- RAG retrieval strategies
- Vector embeddings generation
- DynamoDB as vector DB
- Prompt engineering for grounding
- Cost optimization (why Titan vs Claude)

---

### 2. ML Engineer
**Focus:** Model selection, embeddings, evaluation

**Read in order:**
1. `backend/lambdas/embed/handler.py`
2. `backend/lambdas/search/handler.py`
3. `docs/architecture/GENAI_FLOW_MAPPING.md`

**Key concepts:**
- Titan Embeddings v2 (1536-dim)
- KNN similarity search
- Cosine similarity implementation
- Model tradeoffs (Titan vs Claude)

---

### 3. MLOps Engineer
**Focus:** Deployment, monitoring, CI/CD

**Read in order:**
1. `infra/terraform/main.tf`
2. `scripts/deployment/deploy-lambdas.sh`
3. `docs/DEPLOYMENT_GUIDE.md`

**Key concepts:**
- Lambda deployment
- Infrastructure as code
- Serverless architecture
- Cost monitoring

---

### 4. Data Engineer (Classic)
**Focus:** Data pipelines, ETL, storage

**Read in order:**
1. `backend/lambdas/ingest/handler.py`
2. `backend/lambdas/embed/handler.py`
3. `docs/architecture/GENAI_FLOW_MAPPING.md`

**Key concepts:**
- API ingestion
- S3 data lake
- DynamoDB as metadata store
- Event-driven pipelines

---

## Quick Reference: "Where is X?"

| What You Want | Where to Look |
|---------------|---------------|
| **How RAG works** | `backend/lambdas/rag/handler.py` |
| **How embeddings are made** | `backend/lambdas/embed/handler.py` |
| **How search works** | `backend/lambdas/search/handler.py` |
| **How data is ingested** | `backend/lambdas/ingest/handler.py` |
| **How agent orchestrates** | `backend/lambdas/agent/handler.py` |
| **Infrastructure setup** | `infra/terraform/main.tf` |
| **API endpoints** | Search for "API Gateway" in main.tf |
| **Frontend UI** | `frontend/app/page.tsx` |
| **System architecture** | `docs/architecture/GENAI_FLOW_MAPPING.md` |
| **Interview prep** | `docs/WALKTHROUGH.md` |

---

## Testing Commands

### Test Search
```bash
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/search \
  -H "Content-Type: application/json" \
  -d '{"query": "refreshing summer drinks"}'
```

### Test RAG
```bash
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/rag \
  -H "Content-Type: application/json" \
  -d '{"question": "What makes a good mojito?"}'
```

### Test Agent
```bash
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me a tropical drink", "session_id": "test-123"}'
```

---

## Debugging Tips

### View Lambda Logs
```bash
aws logs tail /aws/lambda/mocktailverse-search --follow
```

### Check DynamoDB
```bash
aws dynamodb scan --table-name mocktailverse-metadata --limit 5
```

### View S3 Data
```bash
aws s3 ls s3://mocktailverse-raw-340752826866/
```

---

## Next Steps After Learning

1. **Run locally:** Set up local testing with AWS credentials
2. **Make changes:** Pick a Lambda and enhance it
3. **Deploy:** Use `scripts/deployment/deploy-lambdas.sh`
4. **Interview:** Use `docs/WALKTHROUGH.md` as your guide

---

**Time to master this repo: 30 minutes**  
**Interview confidence after: 9/10**

**Start with:** [`docs/architecture/GENAI_FLOW_MAPPING.md`](architecture/GENAI_FLOW_MAPPING.md)
