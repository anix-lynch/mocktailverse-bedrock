# 🍹 Mocktailverse: GenAI Data Engineering Platform

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
git clone https://github.com/anix-lynch/mocktailverse.git
cd mocktailverse

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

## 🎤 Interview Talking Points

### "What did you build?"

> I built Mocktailverse, a GenAI-native data engineering platform that transforms cocktail recipe data into an intelligent semantic search system with conversational AI. It's a complete end-to-end pipeline showcasing modern AI platform engineering—from LLM-powered data extraction to RAG-based retrieval to conversational agents.

### "Why does this demonstrate GenAI Data Engineering?"

> This shows the fundamental shift from traditional ETL to AI-native systems. Instead of just moving data from A to B, I'm using LLMs for metadata extraction, generating embeddings for semantic search, implementing RAG for grounded retrieval, and deploying conversational agents. These are the exact skills companies need for building GenAI products in 2025.

### "What makes this production-ready?"

> It's 100% serverless, event-driven, and cost-optimized. The entire system runs for $25/month on AWS, scales automatically, has zero infrastructure to manage, and includes proper observability with CloudWatch. I used Step Functions for orchestration, Bedrock for LLM inference, OpenSearch for vector search, and CloudFront for global distribution—all AWS-native services that enterprises actually use.

### "What's the technical depth?"

> I implemented:
> - Multi-stage embedding pipeline with cosine similarity deduplication
> - KNN vector search with OpenSearch
> - RAG architecture with context retrieval and prompt engineering
> - Bedrock Agents with custom tools and guardrails
> - Event-driven workflows with Step Functions
> - Infrastructure as Code with Terraform
> - Next.js frontend with SSR and API integration

This isn't a tutorial project—it's a real AI platform that could handle production traffic.

---

## 🔮 Future Enhancements

- [ ] Multi-modal search (image + text)
- [ ] Fine-tuned embedding model for cocktail domain
- [ ] Real-time streaming responses
- [ ] A/B testing framework for prompts
- [ ] Cost analytics dashboard
- [ ] Multi-region deployment
- [ ] GraphQL API layer
- [ ] Mobile app (React Native)

---

## 📚 Documentation

- **[Architecture Guide](./ARCHITECTURE.md)** - Detailed system design
- **[API Reference](./docs/API.md)** - Endpoint documentation
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Step-by-step setup
- **[Cost Analysis](./docs/COSTS.md)** - Detailed cost breakdown

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