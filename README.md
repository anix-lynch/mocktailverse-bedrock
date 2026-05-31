# Mocktailverse — AWS Serverless RAG Stack

> A complete serverless GenAI stack on **AWS, end-to-end in Terraform** — 6 Lambdas, DynamoDB, S3, EventBridge, API Gateway, CloudFront. Scales to zero, runs for **~$1.56/month**. (My AWS card; the rest of my stack is GCP.)

![Demo](demo.gif)

> Live stack is torn down to **$0 between interviews** and redeploys with one `terraform apply` (see [DEPLOYMENT.md](DEPLOYMENT.md)). The GIF above is the deployed MVP.

---

## Repo Map

```
mocktailverse-bedrock/
│
├── lambdas/          ✅ the GenAI runtime — 6 Python Lambdas
│   ├── ingest/       ✅ pull recipes + Titan enriches metadata → DynamoDB
│   ├── embed/        ✅ Titan v2 embeddings (1024-dim) → S3
│   ├── search/       ✅ cosine-similarity semantic search
│   ├── rag/          ✅ retrieve top-K → grounded answer (refuses if no context)
│   ├── agent/        ✅ tool-calling agent: search tool + Titan
│   └── search_tool/  ✅ the callable search tool the agent uses
├── infra/terraform/  ✅ all AWS resources (S3, DynamoDB, 6 Lambdas, API GW, EventBridge)
├── frontend/         ✅ Next.js 14 chat + search UI → S3 + CloudFront
├── scripts/          ✅ benchmark.py — latency harness
├── data/             ✅ seed recipes + DynamoDB schema
├── ARCHITECTURE.md   📖 system design + diagrams
├── DEPLOYMENT.md     📖 deploy + teardown
└── README.md         📖 you are here
```

---

## Architecture

```
External recipe API
        │
        ▼
   ingest Lambda ──(Titan enrich)──► DynamoDB (metadata)
        ▲                                  │
   EventBridge (daily)              embed Lambda (Titan v2, 1024-dim → S3)
                                           │
                                           ▼
        ┌──────────────── API Gateway ────────────────┐
        ▼                  ▼                            ▼
   search Lambda      rag Lambda                  agent Lambda
   (cosine sim)   (retrieve→ground→answer)   (search tool + Titan)
        │                  │                            │
        └──────────────────┴────────────────────────────┘
                           ▼
              Next.js 14 frontend (S3 + CloudFront CDN)
```

Full design + diagrams: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## What it does

- **AI ingestion** — Bedrock Titan Text Lite enriches recipes (flavor, tasting notes, categories) → DynamoDB
- **Semantic search** — Titan v2 embeddings (1024-dim) in S3, ranked by **real cosine similarity** — no OpenSearch bill
- **Grounded RAG** — retrieve top-K → answer only from that context at `temperature 0.3`; empty retrieval returns `"I don't know"` instead of hallucinating
- **Tool-calling agent** — calls a `search_cocktails` tool against DynamoDB before answering, so replies are data-backed
- **Event-driven** — EventBridge daily ingest; fully serverless, scales to zero
- **Frontend** — Next.js 14 served globally via CloudFront

**Stack:** AWS Lambda · Bedrock (Titan Text Lite + Titan Embeddings v2) · DynamoDB · S3 · EventBridge · API Gateway · CloudFront · Terraform · Next.js 14

Same architecture transfers to enterprise GenAI: support-doc RAG, product recommendations, medical-literature Q&A, contract analysis.

---

## Cost (live)

| Service | Monthly |
|---------|---------|
| CloudFront | $0.85 |
| DynamoDB (on-demand) | $0.25 |
| Bedrock Titan (gen) | $0.30 |
| Bedrock Titan (embed) | $0.10 |
| API Gateway | $0.04 |
| S3 | $0.02 |
| Lambda | $0.00 (free tier) |
| **Total** | **~$1.56** |

DynamoDB + S3 cosine search (instead of OpenSearch Serverless, ~$24/mo) is the main cost lever.

---

## Quick Start

```bash
git clone https://github.com/anix-lynch/mocktailverse-bedrock.git
cd mocktailverse-bedrock

# Infrastructure (outputs the API Gateway URL)
cd infra/terraform && terraform init && terraform apply

# Frontend
cd ../../frontend && npm install && npm run build
aws s3 sync out/ s3://<frontend-bucket-from-tf-output>
```

Test (use the `api_url` Terraform output for `<API>`):

```bash
curl -X POST "<API>/v1/search" -H "Content-Type: application/json" -d '{"query": "refreshing summer drinks"}'
curl -X POST "<API>/v1/rag"    -H "Content-Type: application/json" -d '{"question": "What makes a good mojito?"}'
curl -X POST "<API>/agent/chat" -H "Content-Type: application/json" -d '{"message": "Find me a tropical drink", "session_id": "u1"}'
```

Prereqs: AWS account with Bedrock (Titan) access · AWS CLI · Node 18+ · Python 3.11+ · Terraform 1.5+.

---

## About

**Anix Lynch** — GenAI / AI Platform Engineer. I build serverless AI systems that ship and stay cheap.

🌐 [Portfolio](https://gozeroshot.dev) · 💼 [LinkedIn](https://linkedin.com/in/anixlynch) · 🐙 [GitHub](https://github.com/anix-lynch) · MIT License
