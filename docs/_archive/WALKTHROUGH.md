# 🎯 Interview Walkthrough - Mocktailverse

> **5-minute technical walkthrough for GenAI Data/ML Engineer interviews**

---

## Quick Facts

**What it is:** Production-ready GenAI RAG platform on AWS  
**Stack:** Next.js + AWS Lambda + Bedrock + DynamoDB  
**Cost:** $1-2/month (MVP), designed to scale to $25/month  
**Status:** Live at [gozeroshot.dev/mocktailverse](https://gozeroshot.dev/mocktailverse)

---

## Folder Structure (Hiring Manager View)

```
mocktailverse-bedrock/
│
├── 🌐 frontend/                  # Next.js 14 UI (Deployed on Vercel)
│   ├── app/page.tsx              # Main search interface
│   ├── components/               # React components
│   └── next.config.js            # Static export config
│
├── ⚙️ backend/lambdas/           # GenAI Runtime (Deployed on AWS Lambda)
│   ├── agent/                    # Bedrock Agent orchestrator
│   ├── rag/                      # RAG pipeline (retrieve + generate)
│   ├── search/                   # Vector KNN search (DynamoDB)
│   ├── embed/                    # Titan Embeddings generation
│   ├── ingest/                   # API fetch + LLM enrichment
│   └── search_tool/              # Tool wrapper for agent
│
├── 🏗️ infra/terraform/           # Infrastructure as Code
│   └── main.tf                   # AWS resource definitions
│
├── 🔄 workflows/                 # Orchestration
│   └── README.md                 # EventBridge/Step Functions specs
│
├── 📜 scripts/                   # DevOps utilities
│   └── deployment/               # Deploy scripts
│
└── 📖 docs/                      # Architecture & Guides
    ├── architecture/             # System design docs
    │   └── GENAI_FLOW_MAPPING.md # Mental model → code mapping
    └── TECHNICAL_OVERVIEW.md     # Deep dive

---

## 3-Minute Technical Walkthrough

### **1. The Problem**
Traditional cocktail recipe search uses keyword matching. Users can't ask "What's a refreshing tropical drink?" and get semantically relevant results.

### **2. The Solution**
Built a RAG (Retrieval-Augmented Generation) system that:
1. **Ingests** cocktail data from TheCocktailDB API
2. **Enriches** with Bedrock LLM (extracts flavor profiles, tasting notes)
3. **Embeds** recipes into 1536-dimensional vectors (Titan Embeddings v2)
4. **Searches** using KNN similarity in DynamoDB (cost-optimized vs OpenSearch)
5. **Generates** grounded answers with Bedrock (temperature 0.3, refusal rules)

### **3. The Architecture**

```
User Query (Next.js)
    ↓
API Gateway
    ↓
Lambda: Search (embeds query)
    ↓
DynamoDB: KNN search (top-5 recipes)
    ↓
Lambda: RAG (context assembly)
    ↓
Bedrock: Titan Text Lite (generation)
    ↓
User sees grounded answer
```

### **4. Key Engineering Decisions**

| Decision | Reasoning |
|----------|-----------|
| **DynamoDB vs OpenSearch** | $0.25/month vs $100-300/month (400x cheaper) |
| **Titan vs Claude** | FREE tier vs paid (cost optimization for MVP) |
| **Lambda vs ECS** | Serverless = zero idle cost, auto-scaling |
| **Static export (Next.js)** | CDN-friendly, no Node.js server needed |

### **5. Production Guardrails**

**Truth (Hallucination < 5%):**
- Always retrieve context before generation
- Low temperature (0.3)
- Refusal rule: "I don't know" when context is missing

**Cost (< $0.01 per query):**
- Bounded top-K retrieval (limit context size)
- DynamoDB over OpenSearch
- Titan over Claude

**Speed (p95 < 5s):**
- Parallel retrieval paths
- Minimal prompt engineering
- CloudFront CDN for frontend

---

## Code Tour (5 key files)

### 1. **`backend/lambdas/ingest/handler.py`** (Data Pipeline)
```python
# Fetch from API → Enrich with Bedrock → Store in DynamoDB
def fetch_from_api():
    cocktails = requests.get("https://thecocktaildb.com/api/json/v1/1/search.php")
    enriched = extract_metadata_with_bedrock(cocktails)  # LLM extracts flavor profile
    store_in_dynamodb(enriched)
```

**What it shows:** LLM-powered data enrichment (not manual ETL)

---

### 2. **`backend/lambdas/embed/handler.py`** (Vector Generation)
```python
# Generate 1536-dim embeddings using Bedrock Titan
def embed_text(text: str) -> List[float]:
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    return response['embedding']  # [0.23, -0.45, ...]
```

**What it shows:** Semantic vectorization for RAG

---

### 3. **`backend/lambdas/search/handler.py`** (KNN Search)
```python
# DynamoDB-based vector search (no OpenSearch needed)
def knn_search(query_embedding: List[float], k: int = 5):
    all_cocktails = dynamodb.scan(TableName='mocktailverse-metadata')
    similarities = [(cosine_similarity(query_embedding, c['embedding']), c) 
                    for c in all_cocktails]
    return sorted(similarities, reverse=True)[:k]
```

**What it shows:** Custom KNN implementation (cost optimization)

---

### 4. **`backend/lambdas/rag/handler.py`** (Context Assembly)
```python
# RAG: Retrieve → Assemble → Generate
def handle_rag_request(question: str):
    # Step 1: Retrieve
    context_docs = lambda_client.invoke(
        FunctionName='mocktailverse-search',
        Payload=json.dumps({'query': question})
    )
    
    # Step 2: Assemble
    context = build_context(context_docs)  # Top-5 recipes as text
    
    # Step 3: Generate
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer only from context."
    answer = bedrock.invoke_model(modelId='amazon.titan-text-lite-v1', body=prompt)
    
    return answer
```

**What it shows:** Full RAG pipeline implementation

---

### 5. **`backend/lambdas/agent/handler.py`** (Bedrock Agent)
```python
# Conversational AI with tool calling
def handle_bedrock_agent(message: str, session_id: str):
    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=message
    )
    # Agent routes to search_cocktails tool or generates creative variations
    return response
```

**What it shows:** AI orchestration and tool calling

---

## Common Interview Questions

### **Q: Why DynamoDB instead of a real vector database?**
**A:** "Cost and simplicity. OpenSearch Serverless costs $100-300/month minimum. DynamoDB free tier gives 25GB storage and 200M requests/month, perfect for MVP. For production with millions of vectors, I'd upgrade to OpenSearch or Pinecone."

---

### **Q: Why Titan instead of Claude?**
**A:** "Engineering tradeoff for MVP cost control. Titan Text Lite is FREE tier, no access request needed. Claude 3.5 is smarter but costs more. For production, I'd A/B test both and choose based on quality metrics (hallucination rate, user satisfaction)."

---

### **Q: How do you prevent hallucination?**
**A:** "Three strategies:
1. **Retrieval-first:** Always fetch context before generation
2. **Low temperature:** 0.3 for factual queries (vs 0.7+ for creative)
3. **Refusal rule:** Prompt includes 'If context doesn't have the answer, say I don't know'

Current target: hallucination rate < 5%."

---

### **Q: How would you scale this to 1M queries/day?**
**A:** "Four bottlenecks to address:
1. **Search:** Migrate to OpenSearch/Pinecone (DynamoDB KNN doesn't scale)
2. **Cost:** Add caching layer (Redis) for popular queries
3. **Latency:** Parallelize retrieval and tool calling (Step Functions)
4. **Observability:** Add DataDog for token tracking, latency monitoring, quality eval

Cost projection: ~$500-1000/month at 1M queries/day."

---

### **Q: What's missing from MVP?**
**A:** "Three areas:
1. **Observability:** No structured logging, no hallucination tracking
2. **Evaluation:** No automated RAGAS metrics, no A/B testing
3. **Orchestration:** Manual triggers instead of Step Functions

Happy to discuss production hardening strategy."

---

## Live Demo Flow (1 minute)

1. **Show live site:** [gozeroshot.dev/mocktailverse](https://gozeroshot.dev/mocktailverse)
2. **Search:** "refreshing summer drinks"
3. **Point out:** Results are semantically relevant (mojito, lemonade, spritzer)
4. **Explain:** "Query was embedded → KNN search → top-5 recipes → displayed"
5. **Optional:** Show GitHub code structure

---

## Repo Health

✅ **Clean structure** (2025-02-12 reorganization)  
✅ **Production deployed** (Vercel + AWS)  
✅ **Documented** (GENAI_FLOW_MAPPING.md, TECHNICAL_OVERVIEW.md)  
⚠️ **No tests** (MVP priority was shipping)  
⚠️ **No CI/CD** (Manual deployments via scripts)  

**Next steps:** Add pytest suite, GitHub Actions, automated eval pipeline.

---

## How to Use This Doc

1. **Pre-interview:** Read this + `docs/architecture/GENAI_FLOW_MAPPING.md`
2. **During interview:** Reference specific code files when explaining
3. **Technical questions:** Use "Common Interview Questions" section
4. **System design:** Draw architecture diagram from memory

**Interview confidence: 9/10** (You built it, you can explain every decision.)

---

**Last Updated:** 2025-02-12  
**Interviewer-Ready:** ✅ Yes
