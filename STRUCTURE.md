# Project Structure

```
mocktailverse-bedrock/
│
├── frontend/                 # Next.js UI
│   └── app/page.tsx
│
├── backend/lambdas/          # AWS Lambda functions
│   ├── ingest/               # Data pipeline
│   ├── embed/                # Embeddings (Titan v2)
│   ├── search/               # Vector search (DynamoDB)
│   ├── rag/                  # RAG pipeline
│   └── agent/                # Bedrock Agent
│
├── infra/terraform/          # Infrastructure
│   └── main.tf
│
└── scripts/deployment/       # Deploy scripts
```

## Data Flow

```
API → ingest → embed → DynamoDB → search → rag → response
```

## Tech Stack

- **Frontend:** Next.js 14 (Vercel)
- **Backend:** AWS Lambda + Bedrock
- **Embeddings:** Titan Embeddings v2 (1536-dim)
- **Vector DB:** DynamoDB (cost-optimized)
- **LLM:** Titan Text Lite (free tier)

## Deployment

- **Live:** https://gozeroshot.dev/mocktailverse
- **API:** https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod
