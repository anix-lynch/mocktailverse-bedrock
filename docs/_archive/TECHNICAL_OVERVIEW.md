# Technical Overview

## Architecture

Mocktailverse is a serverless GenAI application built on AWS, demonstrating enterprise-grade RAG (Retrieval Augmented Generation) architecture with real-time observability.

### Core Components

**Frontend**
- Next.js 14 static site deployed to S3 + CloudFront
- Real-time debug panel exposing AI reasoning pipeline
- Live demo: [CloudFront URL]

**Backend**
- AWS Lambda functions (Python 3.11)
- API Gateway REST endpoints
- DynamoDB for metadata storage

**AI/ML Layer**
- **Embeddings**: Amazon Titan Embeddings v2 (1536-dimensional vectors)
- **Vector Search**: Semantic retrieval via OpenSearch Serverless (or DynamoDB fallback)
- **Generation**: Claude 3 Haiku via AWS Bedrock
- **Orchestration**: Bedrock Agents with custom tool integration

### Data Flow

```
User Query → API Gateway → Lambda (Agent)
                              ↓
                        Generate Embedding (Titan)
                              ↓
                        Semantic Search (OpenSearch/DynamoDB)
                              ↓
                        Retrieve Top-K Results
                              ↓
                        Assemble RAG Context
                              ↓
                        LLM Generation (Claude)
                              ↓
                        Return Response + Debug Data
```

### Key Features

1. **Transparent AI Pipeline**: Every query exposes the full reasoning chain:
   - Query embedding vector (1536 dims)
   - Top-K semantic search results with similarity scores
   - RAG context window sent to LLM
   - Agent tool calls with inputs/outputs

2. **Cost Efficiency**: 
   - Serverless architecture (pay-per-invocation)
   - No idle compute costs
   - Estimated $0.10/month for demo usage

3. **Production Ready**:
   - Error handling and fallbacks
   - CloudFront CDN for global delivery
   - Infrastructure as code (Python automation scripts)

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| API | AWS API Gateway, Lambda |
| AI/ML | Bedrock (Titan, Claude), OpenSearch Serverless |
| Storage | S3, DynamoDB |
| CDN | CloudFront |
| IaC | Python (boto3), AWS CLI |

## Performance

- **Cold Start**: ~2-3s (Lambda initialization)
- **Warm Response**: ~800-1200ms (embedding + search + generation)
- **Embedding Latency**: ~100ms (Titan)
- **Generation Latency**: ~600-800ms (Claude)
