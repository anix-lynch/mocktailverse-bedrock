# Project Structure

```
mocktailverse-bedrock/
│
├── 🌐 frontend/                      # Next.js 14 UI (Vercel)
│   ├── app/
│   │   ├── page.tsx                  # Main UI (search + chat combined)
│   │   ├── layout.tsx                # Root layout
│   │   ├── globals.css               # Tailwind styles
│   │   └── components/
│   │       └── DebugPanel.tsx        # Debug component
│   ├── public/                       # Static assets
│   ├── next.config.js                # Static export config
│   └── package.json                  # Dependencies
│
├── ⚙️ backend/                       # GenAI Runtime (AWS Lambda)
│   └── lambdas/
│       ├── agent/handler.py          # Bedrock Agent orchestrator
│       ├── embed/handler.py          # Titan Embeddings v2
│       ├── ingest/handler.py         # API fetch + LLM enrichment
│       ├── rag/handler.py            # RAG pipeline
│       ├── search/handler.py         # DynamoDB KNN search
│       └── search_tool/handler.py    # Tool wrapper for agent
│
├── 🏗️ infra/terraform/              # Infrastructure as Code
│   └── main.tf                       # AWS resources (all-in-one)
│
├── 🔄 workflows/                     # Orchestration
│   └── README.md                     # EventBridge/Step Functions docs
│
├── 📜 scripts/deployment/            # DevOps Utilities
│   ├── deploy-lambdas.sh             # Lambda deployment
│   ├── deploy_mvp.sh                 # Full stack deploy
│   └── load_sample_data.py           # Seed DynamoDB
│
└── 📖 AI_CONTEXT.md                  # Everything AI needs to work on this project
```

## Data Flow

```
TheCocktailDB API
    ↓
ingest → enrich (Bedrock) → S3
    ↓
embed → Titan Embeddings v2 → DynamoDB
    ↓
User Query → API Gateway
    ↓
search → KNN in DynamoDB (top-5)
    ↓
rag → context assembly → Bedrock generation
    ↓
User sees answer
```

## Deployed URLs

- **Live:** https://gozeroshot.dev/mocktailverse
- **API:** https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod
- **GitHub:** https://github.com/anix-lynch/mocktailverse-bedrock
- **Portfolio:** https://gozeroshot.dev

## Key Tech Decisions

- **DynamoDB** (not OpenSearch) - $0.25/month vs $100-300/month
- **Titan Text Lite** (not Claude) - FREE tier vs paid
- **Single-page frontend** (not separate routes) - MVP simplicity
- **Monolithic terraform** (not split files) - Easier to read for small project
