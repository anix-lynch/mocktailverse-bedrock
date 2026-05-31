# Mocktailverse Architecture

Two parts: **what's deployed (MVP)** and **what's planned (v2)**. The MVP is the source of truth — it matches the code in `lambdas/` and `infra/terraform/`. The v2 section is the roadmap, not a claim of what exists.

---

## Deployed MVP

```
┌──────────────────────────────────────────────────────────────┐
│ 1. INGESTION (event-driven)                                    │
│                                                                │
│   External recipe API ──► ingest Lambda ──► DynamoDB(metadata) │
│                              │  (Titan Text Lite enriches)     │
│        EventBridge (daily) ──┘                                 │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│ 2. EMBEDDINGS                                                  │
│                                                                │
│   embed Lambda ──► Bedrock Titan Embeddings v2 (1024-dim)      │
│                 ──► vectors stored on the DynamoDB item        │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│ 3. SEARCH + RAG (API Gateway)                                  │
│                                                                │
│   search Lambda : embed query → cosine vs S3 embeddings → top-K │
│   rag Lambda    : retrieve top-K → build context →             │
│                   Titan (temp 0.3) → grounded answer            │
│                   (empty retrieval → "I don't know")            │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│ 4. AGENT (API Gateway /agent/chat)                             │
│                                                                │
│   agent Lambda : calls search_cocktails tool (DynamoDB) first, │
│                  then Titan answers from retrieved rows.       │
│   (A managed Bedrock Agent alias is wired but disabled —       │
│    AGENT_ID = None — so the direct Titan + tool path runs.)    │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│ 5. FRONTEND                                                    │
│                                                                │
│   Next.js 14 build ──► S3 ──► CloudFront CDN ──► API Gateway   │
└──────────────────────────────────────────────────────────────┘
```

### Deployed technology

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Ingestion | Lambda + EventBridge | Event-driven daily collection |
| LLM | **Bedrock Titan Text Lite** | Metadata enrichment + RAG generation |
| Embeddings | **Bedrock Titan Embeddings v2 (1024-dim)** | Vectorization |
| Semantic search | **S3-stored embeddings + cosine** | Real similarity ranking in Lambda, no OpenSearch |
| Agent | Lambda tool-calling (`search_cocktails`) | Data-grounded conversation |
| API | API Gateway + Lambda | REST endpoints |
| Frontend | Next.js 14 + CloudFront | React UI |
| Storage | S3 + DynamoDB | Raw data + metadata + vectors |
| Observability | CloudWatch | Logs + metrics |

### Cost (live)

| Service | Usage | Cost |
|---------|-------|------|
| CloudFront | 10GB transfer | $0.85 |
| DynamoDB | on-demand, 1K writes | $0.25 |
| Bedrock Titan (gen) | 100K tokens | $0.30 |
| Bedrock Titan (embed) | 1M tokens | $0.10 |
| API Gateway | 10K requests | $0.04 |
| S3 | 1GB | $0.02 |
| Lambda | 10K invocations | $0.00 (free tier) |
| **Total** | | **~$1.56/month** |

Using DynamoDB instead of OpenSearch Serverless (~$24/mo minimum 1 OCU) is the single biggest cost decision.

### Data-flow example

```
"Show me refreshing mocktails with mint"
  → /v1/search → search Lambda
      → Titan embed query → DynamoDB semantic search (top-K)
      → [Mojito Mocktail, Mint Lemonade, ...] with relevance scores

"What makes a good mojito?"
  → /v1/rag → rag Lambda
      → retrieve top-K → build context → Titan (temp 0.3) grounded answer
      → if nothing retrieved → "I don't know" (grounded:false)
```

---

## Planned (v2) — roadmap, NOT yet built

These appear in earlier designs and are intentionally deferred to keep the MVP at ~$1.56/month:

- **OpenSearch Serverless** for ANN vector search (would replace DynamoDB search; ~$24/mo)
- **Step Functions Express** orchestration for the ingest → embed → index pipeline (notes in `workflows/`)
- **Larger model** (e.g. Claude 3.x) for richer generation in place of Titan Text Lite
- **More agent tools**: `suggest_variation`, `get_tasting_notes` (currently designed only)
- **Managed Bedrock Agent** enabled (alias is wired; `AGENT_ID` currently `None`)
- **Bedrock Guardrails** for PII / content safety

---

## Why GenAI data engineering (not traditional ETL)

| Traditional ETL | This system |
|----------------|-------------|
| Batch on schedules | Event-driven (EventBridge) |
| SQL transforms | LLM enrichment (Titan) |
| Keyword search | Semantic search |
| Static dashboards | Grounded RAG + agent |
| Manual QA | Refuse-on-empty grounding |
| Relational only | DynamoDB (vectors + NoSQL) |
