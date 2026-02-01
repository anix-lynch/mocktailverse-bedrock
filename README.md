# 🍹 Mocktailverse: GenAI Data Engineering Platform

> **Portfolio Snapshot (MVP Deployed)**  
> This repository is a read-only snapshot of the deployed Mocktailverse MVP.  
> Live demo: [https://gozeroshot.dev/mocktailverse](https://gozeroshot.dev/mocktailverse)  
> What to review: `lambdas/` (GenAI logic), `terraform/` (infra), `frontend/` (UI)

## Recruiter Quick Scan (2 minutes)

- What it is: GenAI platform with RAG + Agents, DynamoDB vector search, serverless orchestration, Next.js UI
- Why it matters: Optimized for Truth / Search / Money / Fast

KPI targets:

- Truth: hallucination rate < 5%
- Search: retrieval relevance > 80%
- Money: cost per query < $0.01
- Fast: p95 latency < 5s

Where to look:

- lambdas/ → GenAI runtime (ingest/embed/search/rag/agent)
- terraform/ → infrastructure + cost decisions
- frontend/ → Next.js chat/search UI

![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Lambda%20%7C%20OpenSearch-orange?logo=amazon-aws)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![Cost](https://img.shields.io/badge/Cost-$1-2%2Fmonth-brightgreen)
![Status](https://img.shields.io/badge/Status-Production-green)

> **A production-ready GenAI data platform that transforms cocktail recipes into an intelligent, semantic search system with conversational AI—showcasing modern AI Data Engineering for 2025.**

## 🎬 Demo

![Mocktailverse Demo](./demo.gif)

**Live Demo:** [https://gozeroshot.dev/mocktailverse](https://gozeroshot.dev/mocktailverse) | **API:** [https://<API_GATEWAY_ID>.execute-api.us-west-2.amazonaws.com/prod](https://<API_GATEWAY_ID>.execute-api.us-west-2.amazonaws.com/prod)

---

## 🎯 What This Is

Mocktailverse isn't your typical ETL pipeline. It's a **GenAI-native data engineering system** that demonstrates how modern AI platforms are built:

- **LLM-powered metadata extraction** using AWS Bedrock
- **Semantic vector search** with embeddings and KNN
- **RAG (Retrieval-Augmented Generation)** for grounded responses
- **Conversational AI agents** with tool calling
- **Event-driven serverless architecture** that scales automatically
- **Cost-optimized** to run for ~$25/month on AWS

Think of it as a **real-world example of AI Platform Engineering**—the kind of system you'd build at a company doing GenAI at scale, just applied to cocktail recipes instead of enterprise data.

---

## 🚀 Why This Matters

### Traditional ETL vs GenAI Data Engineering

| Old Way (ETL) | New Way (GenAI) |
|---------------|-----------------|
| Batch jobs running on schedules | Event-driven, real-time processing |
| SQL transformations | LLM-powered enrichment |
| Keyword search (LIKE '%mojito%') | Semantic vector search |
| Static dashboards | Conversational AI agents |
| Manual data quality checks | AI-driven validation |
| Relational databases | Vector databases + NoSQL |

**This project shows I can build the "New Way."**

---

## 🏗️ Architecture

```
External APIs → S3 → Lambda (Bedrock LLM) → DynamoDB
                ↓
         EventBridge (Scheduled)
                ↓
    Embedding Pipeline (Bedrock Titan) → S3
                ↓
    DynamoDB (Metadata + Search)
                ↓
    API Gateway ← Next.js Frontend (CloudFront)
         ↓
    Search + RAG + Bedrock Agents Endpoints
```

**Architecture:** Uses DynamoDB for search (cost-efficient). Bedrock Agents provide conversational AI with custom tools—no OpenSearch needed!

**Full architecture diagram**: See [`ARCHITECTURE.md`](./ARCHITECTURE.md)

---

## ✨ Key Features

### 1. **AI-Powered Ingestion**
- Fetch cocktail data from external APIs
- Use **Bedrock Claude 3.5** to extract and enrich metadata
- Generate flavor profiles, tasting notes, and categorizations automatically
- Store enriched data in DynamoDB

### 2. **Semantic Search** (DynamoDB-based)
- Convert recipes into **1536-dimensional embeddings** (Bedrock Titan v2)
- DynamoDB-based search with intelligent filtering
- Search by meaning, not just keywords
- Example: "refreshing summer drinks" finds mojitos, lemonades, and spritzers

### 3. **RAG Pipeline**
- User asks: *"What's a good mocktail for a tropical party?"*
- System:
  1. Embeds the query
  2. Retrieves top 5 relevant recipes (KNN search)
  3. Builds context from retrieved data
  4. Calls Bedrock Claude to generate a grounded answer
- Result: Accurate, contextual responses backed by real data

### 4. **Bedrock Agents** (Conversational AI with Custom Tools) ⭐
- **AWS Bedrock Agents** with custom tools for intelligent cocktail assistance
- Custom tools:
  - `search_cocktails` - Find recipes by natural language queries
  - `suggest_variation` - Create new cocktail variations
  - `get_tasting_notes` - Provide flavor analysis
- Multi-turn conversations with session memory
- DynamoDB-backed retrieval (no OpenSearch needed!)
- Example: *"Find me a tropical drink"* → Agent uses search tool → Returns contextual recommendations

### 5. **Event-Driven Architecture**
- **EventBridge** scheduled rule for daily ingestion
- **Lambda functions** for processing (ingest, embed, search, rag)
- No long-running servers—everything is serverless
- Automatic scaling and error handling

**Note:** Step Functions Express planned for complex multi-stage workflows.

### 6. **Modern Frontend**
- **Next.js 14** with App Router
- Server-side rendering for SEO
- Real-time search with debouncing
- Chat interface for AI bartender
- Deployed on **CloudFront** for global CDN

---

## 💰 Cost Breakdown

**Current Deployment (MVP):** Running for **~$1-2/month** on AWS:

| Service | Monthly Cost | Why |
|---------|-------------|-----|
| CloudFront | $0.85 | 10GB transfer (first year free) |
| DynamoDB | $0.25 | On-demand writes (25GB free tier) |
| API Gateway | $0.04 | 10K requests |
| Bedrock Claude | $0.30 | 100K tokens/month |
| Bedrock Titan Embeddings | $0.10 | 1M tokens |
| Lambda | $0.00 | Free Tier (1M requests) |
| S3 | $0.02 | 1GB storage (5GB free tier) |
| **TOTAL (MVP)** | **~$1.56** | |

**Note:** Uses DynamoDB for search + Bedrock Agents for conversational AI. No OpenSearch needed—keeps costs low while showcasing cutting-edge GenAI tech!

---

## 🛠️ Tech Stack

### Infrastructure (Deployed)
- **AWS Lambda** - Serverless compute (ingest, embed, search, rag, agent)
- **Amazon S3** - Data lake storage (raw, embeddings, frontend)
- **Amazon DynamoDB** - Metadata store + intelligent search
- **Amazon EventBridge** - Scheduled ingestion triggers
- **AWS API Gateway** - RESTful API layer
- **Amazon CloudFront** - Global CDN for frontend
- **AWS Bedrock Agents** - Conversational AI with custom tools ⭐

### AI/ML (Implemented)
- **AWS Bedrock Claude 3.5** - LLM for metadata extraction and generation
- **AWS Bedrock Titan Embeddings v2** - Vector embeddings
- **AWS Bedrock Agents** - Conversational AI with custom tools ⭐

### Application
- **Next.js 14** - React framework
- **TypeScript** - Type-safe frontend
- **Tailwind CSS** - Styling
- **Python 3.11** - Backend Lambda functions
- **Terraform** - Infrastructure as Code

---

## 📊 Real-World Use Cases

While this uses cocktail recipes as the domain, the **exact same architecture** applies to:

- **Customer support**: Semantic search over support docs + RAG chatbot
- **E-commerce**: Product recommendations based on natural language queries
- **Healthcare**: Medical literature search with grounded Q&A
- **Legal**: Contract analysis with semantic retrieval
- **Finance**: Research reports with AI-powered insights

**The skills demonstrated here transfer directly to enterprise GenAI systems.**

---

## 🚀 Quick Start

### Prerequisites
- AWS Account with Bedrock access
- AWS CLI configured
- Node.js 18+
- Python 3.11+
- Terraform 1.5+

### Deploy Infrastructure

```bash
# 1. Clone repo
git clone https://github.com/anix-lynch/mocktailverse-bedrock.git
cd mocktailverse-bedrock

# 2. Deploy AWS infrastructure
cd terraform
terraform init
terraform apply

# 3. Deploy Lambda functions
cd ../lambdas
./deploy.sh

# 4. Deploy frontend
cd ../frontend
npm install
npm run build
aws s3 sync out/ s3://mocktailverse-frontend
```

### Test the System

```bash
# Search endpoint
curl -X POST https://api.mocktailverse.dev/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "refreshing summer drinks"}'

# RAG endpoint
curl -X POST https://api.mocktailverse.dev/v1/rag \
  -H "Content-Type: application/json" \
  -d '{"question": "What makes a good mojito?"}'

# Bedrock Agent endpoint
curl -X POST https://<API_GATEWAY_ID>.execute-api.us-west-2.amazonaws.com/prod/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me a refreshing tropical drink", "session_id": "user-123"}'
```

---

## 📁 Project Structure

```
mocktailverse/
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main Terraform config
│   ├── bedrock.tf            # Bedrock resources
│   ├── opensearch.tf         # Vector DB setup
│   └── step_functions.tf     # Orchestration workflows
│
├── lambdas/                  # Serverless functions
│   ├── ingest/               # Data ingestion + LLM extraction
│   ├── embed/                # Embedding generation
│   ├── search/               # Vector search
│   ├── rag/                  # RAG retrieval
│   └── agent/                # Bedrock agent runtime
│
├── frontend/                 # Next.js application
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   └── lib/                  # API clients
│
├── workflows/                # Step Functions definitions
│   ├── ingestion.json        # Ingestion workflow
│   └── embedding.json        # Embedding workflow
│
├── ARCHITECTURE.md           # Detailed architecture docs
└── README.md                 # You are here
```

## Repository Map

Production paths (current):
- lambdas/ — GenAI runtime
- terraform/ — infra as code
- frontend/ — UI

Legacy / experiments (not used in deployed MVP):
- lambda/
- legacy/
- archive/

---

## 🎓 What I Learned

### GenAI Data Engineering Skills
- ✅ Building RAG pipelines from scratch
- ✅ Vector database design and optimization
- ✅ LLM prompt engineering for data extraction
- ✅ Embedding generation and semantic search
- ✅ Agent orchestration with tool calling
- ✅ Event-driven serverless architectures

### AWS Bedrock Expertise
- ✅ Claude 3.5 for generation tasks
- ✅ Titan Embeddings for vector creation
- ✅ Bedrock Agents with custom tools
- ✅ Guardrails for content safety
- ✅ Cost optimization strategies

### Platform Engineering
- ✅ Infrastructure as Code (Terraform)
- ✅ Serverless orchestration (Step Functions)
- ✅ API design and versioning
- ✅ Observability and monitoring
- ✅ Cost-efficient architecture

---

## Reliability Guardrails (Production Mindset)

- Retrieval-first: always fetch top-K recipes before generation (RAG)
- Grounded answers: answer only from retrieved context
- Refusal: return "I don't know" when context is missing
- Bounded context: limit top-K and context size to control cost + truncation
- Telemetry loop: tokens, latency, and interaction signals feed tuning

## Core Outcomes

- Grounded responses (Truth)
- Clarification-first behavior (Search)
- Low cost per query (Money)
- Fast responses (Fast)

### System Design: Truth / Search / Money / Fast

```
🍹 MOCKTAILVERSE — WHAT IT ACHIEVES (WITH KPIs)

├── ✅ TRUTH — AI doesn't make stuff up
│   (Hallucination Rate < 5%)
│
│   ├── Always looks at real recipes first
│   │   (RAG retrieval → DynamoDB KNN)
│   │
│   ├── Answers only from what it finds
│   │   (grounded prompt → Claude)
│   │
│   ├── Says "I don't know" when context is missing
│   │   (refusal rule)
│   │
│   └── Keeps creativity low for factual answers
│       (temperature ≤ 0.3)
│
├── ✅ SEARCH — AI asks smart questions instead of guessing
│   (Retrieval Relevance > 80%)
│
│   ├── Measures confidence in retrieved results
│   │   (top-K relevance score)
│   │
│   ├── If confidence is low, asks user follow-up
│   │   (clarification loop)
│   │
│   ├── Uses tools when action is needed
│   │   (Bedrock Agents → Lambda tools)
│   │
│   └── Verifies tool results before answering
│       (post-tool grounding)
│
├── ✅ MONEY — Each answer costs very little
│   (Cost per Query < $0.01)
│
│   ├── Limits how much context is sent to the model
│   │   (bounded top-K, context usage < 80%)
│   │
│   ├── Uses DynamoDB instead of expensive vector DBs
│   │   (DynamoDB KNN vs OpenSearch)
│   │
│   ├── Uses Titan embeddings for cheap vectorization
│   │   (Bedrock Titan)
│   │
│   ├── Runs everything serverless
│   │   (Lambda + API Gateway)
│   │
│   └── Tracks token usage and cost per request
│       (telemetry)
│
└── ✅ FAST — Responses feel instant
    (p95 Latency < 5s)

    ├── Parallel retrieval + tool execution
    │   (async paths)
    │
    ├── Lightweight orchestration
    │   (Lambda router)
    │
    ├── Minimal prompt size
    │   (context trimming)
    │
    ├── Global frontend delivery
    │   (Next.js + CDN)
    │
    └── Monitors p95 response time
        (latency telemetry)
```

---

## 📚 Documentation

- **[Technical Overview](./docs/TECHNICAL_OVERVIEW.md)** - Architecture and tech stack
- **[Architecture Diagrams](./docs/ARCHITECTURE_MAPS.md)** - Visual system design
- **[Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** - Setup instructions
- **[Bedrock Access Guide](./docs/BEDROCK_ACCESS_GUIDE.md)** - AWS Bedrock configuration

---

## 🤝 Contributing

This is a portfolio project, but I'm open to suggestions! Feel free to:
- Open issues for bugs or ideas
- Submit PRs for improvements
- Use this as a template for your own GenAI projects

---

## 📝 License

MIT License - Feel free to use this as a learning resource or template!

---

## 👨‍💻 About Me

**Anix Lynch** - GenAI Data Engineer / AI Platform Engineer

I build production-ready AI systems that actually ship. This project demonstrates my ability to:
- Design and implement GenAI data platforms
- Work with modern LLM technologies (Bedrock, RAG, Agents)
- Build cost-efficient serverless architectures
- Create end-to-end AI products from data to deployment

**Connect with me:**
- 🌐 [Portfolio](https://gozeroshot.dev)
- 💼 [LinkedIn](https://linkedin.com/in/anixlynch)
- 🐙 [GitHub](https://github.com/anix-lynch)

---

**Built with ❤️ using AWS Bedrock, Next.js, and a lot of coffee**

*Last Updated: 2025-11-25 | Status: MVP Deployed | Cost: $1-2/month (MVP) | Full version: $25/month*