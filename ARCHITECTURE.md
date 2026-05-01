# 🏗️ Mocktailverse GenAI Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MOCKTAILVERSE AI PLATFORM                            │
│                    GenAI Data Engineering System (2025)                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. INGESTION LAYER (Event-Driven)                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  External APIs          S3 Raw Zone                EventBridge               │
│  (TheCocktailDB)   →   (cocktails/*.json)    →    (S3 Events)                │
│       │                      │                          │                     │
│       └──────────────────────┴──────────────────────────┘                    │
│                                  ↓                                            │
│                       Lambda: ingest_and_extract                             │
│                       ┌─────────────────────────┐                            │
│                       │ • Parse JSON            │                            │
│                       │ • Call Bedrock Claude   │                            │
│                       │ • Extract metadata      │                            │
│                       │ • Enrich with LLM       │                            │
│                       └─────────────────────────┘                            │
│                                  ↓                                            │
│                       DynamoDB: metadata_table                               │
│                       (job_id, name, category, enriched_desc)                │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. SEMANTIC TRANSFORMATION LAYER (Vector Pipeline)                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                       Step Functions Workflow                                │
│                       ┌─────────────────────────┐                            │
│                       │ 1. Chunk text           │                            │
│                       │ 2. Generate embeddings  │                            │
│                       │ 3. Dedupe via cosine    │                            │
│                       │ 4. Index vectors        │                            │
│                       └─────────────────────────┘                            │
│                                  ↓                                            │
│         Lambda: chunk_and_embed          Lambda: vector_indexer              │
│         ┌──────────────────────┐         ┌──────────────────────┐            │
│         │ Bedrock Titan        │         │ OpenSearch           │            │
│         │ Embeddings v2        │    →    │ Serverless           │            │
│         │ (1536 dimensions)    │         │ (Vector Engine)      │            │
│         └──────────────────────┘         └──────────────────────┘            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. VECTOR SEARCH + RAG LAYER (Retrieval)                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                       API Gateway: /api/v1/*                                 │
│                                  ↓                                            │
│         ┌────────────────────────┴────────────────────────┐                  │
│         │                                                  │                  │
│    Lambda: search              Lambda: rag_retrieval                         │
│    ┌──────────────┐             ┌──────────────────────┐                     │
│    │ 1. Embed     │             │ 1. Embed query       │                     │
│    │    query     │             │ 2. KNN search (k=5)  │                     │
│    │ 2. KNN       │             │ 3. Build context     │                     │
│    │    search    │             │ 4. Call Bedrock      │                     │
│    │ 3. Return    │             │ 5. Generate answer   │                     │
│    │    results   │             └──────────────────────┘                     │
│    └──────────────┘                       ↓                                  │
│                                  Bedrock Claude 3.5                           │
│                                  (RAG-powered generation)                     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. AGENT LAYER (AI Bartender)                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                       API Gateway: /agent/chat                               │
│                                  ↓                                            │
│                       Lambda: bedrock_agent                                  │
│                       ┌─────────────────────────┐                            │
│                       │ Bedrock Agent Runtime   │                            │
│                       │ ┌─────────────────────┐ │                            │
│                       │ │ Tools:              │ │                            │
│                       │ │ • search_cocktails  │ │                            │
│                       │ │ • suggest_variation │ │                            │
│                       │ │ • get_tasting_notes │ │                            │
│                       │ └─────────────────────┘ │                            │
│                       │ Guardrails: PII filter  │                            │
│                       └─────────────────────────┘                            │
│                                  ↓                                            │
│                       Conversational AI Interface                            │
│                       (Multi-turn, grounded retrieval)                       │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. ORCHESTRATION (Event-Driven)                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  EventBridge Rules          Step Functions Express                           │
│  ┌──────────────────┐       ┌──────────────────────────┐                    │
│  │ S3 Upload        │  →    │ Ingestion Workflow       │                    │
│  │ Schedule (daily) │  →    │ Embedding Workflow       │                    │
│  │ API Trigger      │  →    │ Reindex Workflow         │                    │
│  └──────────────────┘       └──────────────────────────┘                    │
│                                                                               │
│  CloudWatch Logs + Metrics                                                   │
│  (Observability, cost tracking, error alerts)                                │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. APPLICATION LAYER (Next.js Frontend)                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                       CloudFront Distribution                                │
│                                  ↓                                            │
│                       S3: Static Next.js Build                               │
│                       ┌─────────────────────────┐                            │
│                       │ Pages:                  │                            │
│                       │ • /search (semantic)    │                            │
│                       │ • /chat (AI bartender)  │                            │
│                       │ • /explore (browse)     │                            │
│                       │ • /about (architecture) │                            │
│                       └─────────────────────────┘                            │
│                                  ↓                                            │
│                       API Gateway (backend)                                  │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

**User Query: "Show me refreshing mocktails with mint"**

```
1. Frontend (Next.js)
   └─> POST /api/v1/search { query: "refreshing mocktails with mint" }

2. API Gateway
   └─> Lambda: search

3. Lambda: search
   ├─> Bedrock Titan Embeddings (embed query)
   ├─> OpenSearch Serverless (KNN search, k=5)
   └─> Return: [Mojito Mocktail, Mint Lemonade, ...]

4. Frontend
   └─> Display results with semantic relevance scores
```

**Agent Query: "Create a tropical variation of a mojito"**

```
1. Frontend (Next.js)
   └─> POST /agent/chat { message: "Create a tropical variation..." }

2. API Gateway
   └─> Lambda: bedrock_agent

3. Bedrock Agent
   ├─> Tool: search_cocktails("mojito")
   ├─> Tool: suggest_variation(base="mojito", theme="tropical")
   ├─> Generate response with grounded retrieval
   └─> Return: "Here's a Tropical Mojito variation..."

4. Frontend
   └─> Display conversational response
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Ingestion** | Lambda + EventBridge | Event-driven data collection |
| **LLM Processing** | Bedrock Claude 3.5 | Metadata extraction, enrichment |
| **Embeddings** | Bedrock Titan v2 | 1536-dim vector generation |
| **Vector DB** | OpenSearch Serverless | KNN/ANN semantic search |
| **Orchestration** | Step Functions Express | Workflow automation |
| **Agent** | Bedrock Agents | Conversational AI with tools |
| **API** | API Gateway + Lambda | RESTful endpoints |
| **Frontend** | Next.js + CloudFront | Modern React UI |
| **Storage** | S3 + DynamoDB | Raw data + metadata |
| **Observability** | CloudWatch | Logs, metrics, alarms |

## Cost Breakdown (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 10K invocations/month | $0.00 (Free Tier) |
| S3 | 1GB storage + 1K requests | $0.02 |
| DynamoDB | On-demand, 1K writes | $0.25 |
| OpenSearch Serverless | 1 OCU (min) | $24.00 |
| Bedrock Claude | 100K tokens/month | $0.30 |
| Bedrock Titan Embeddings | 1M tokens | $0.10 |
| Step Functions Express | 1K executions | $0.00 (Free Tier) |
| API Gateway | 10K requests | $0.04 |
| CloudFront | 10GB transfer | $0.85 |
| **TOTAL** | | **~$25.56/month** |

**Remaining Budget**: $174.44 for experimentation, scaling, or additional features.

## Why This is GenAI Data Engineering (Not Traditional ETL)

| Traditional ETL | GenAI Data Engineering |
|----------------|------------------------|
| Batch processing | Event-driven + real-time |
| SQL transformations | LLM-powered enrichment |
| Keyword search | Semantic vector search |
| Static dashboards | Conversational AI agents |
| Manual data quality | AI-driven validation |
| Scheduled jobs | Serverless orchestration |
| Relational DB | Vector DB + NoSQL |
