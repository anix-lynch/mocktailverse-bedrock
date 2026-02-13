# AI Context - Everything You Need to Work on This Project

> **For future AI agents: Read this first**

---

## Project Identity

**Name:** Mocktailverse  
**Owner:** Anix Lynch (@anixlynch)  
**Type:** GenAI Data Engineering Portfolio Project  
**Status:** Deployed and live

---

## Secrets & Authentication

### AWS
```bash
# Location: ~/.config/secrets/global.env
# Load with: source ~/.config/secrets/global.env

AWS_ACCESS_KEY_ID=****************XE7M
AWS_SECRET_ACCESS_KEY=****************NePI
AWS_DEFAULT_REGION=us-west-2
AWS_ACCOUNT_ID=340752826866
```

### GitHub
```bash
# SSH key configured
# Repo: git@github.com:anix-lynch/mocktailverse-bedrock.git
```

### Vercel
```bash
# Frontend deployed to: gozeroshot.dev/mocktailverse
# Project connected to GitHub (auto-deploy on push)
```

---

## Deployed Resources (AWS Account 340752826866)

### Lambdas (8 functions)
```
mocktailverse-agent          (Python 3.11, fallback mode, Titan Text Lite)
mocktailverse-rag            (Python 3.11, retrieval + generation)
mocktailverse-search         (Python 3.11, DynamoDB KNN)
mocktailverse-search-tool    (Python 3.11, tool wrapper)
mocktailverse-embed          (Python 3.11, Titan Embeddings v2)
mocktailverse-ingest         (Python 3.11, API fetch + enrich)
mocktailverse-transform      (Python 3.11, legacy)
mocktailverse-fetch-cocktails(Python 3.9, legacy)
```

### S3 Buckets (6)
```
mocktailverse-raw-340752826866           (raw API data)
mocktailverse-processed-340752826866     (enriched)
mocktailverse-embeddings-340752826866    (vectors)
mocktailverse-frontend-340752826866      (Next.js build)
mocktailverse-raw                        (legacy)
mocktailverse-processed                  (legacy)
```

### DynamoDB Tables (3)
```
mocktailverse-cocktails     (recipe metadata)
mocktailverse-metadata      (embeddings + search index)
mocktailverse-jobs          (processing status)
```

### API Gateway
```
https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod
```

---

## Current Tech Stack (REALITY)

**Not what README claims, but what's actually running:**

- **LLM:** Amazon Titan Text Lite (FREE tier, not Claude 3.5)
- **Embeddings:** Titan Embeddings v2 (1536-dim)
- **Vector DB:** DynamoDB with KNN (not OpenSearch)
- **Agent:** Bedrock Agents in fallback mode (`AGENT_ID = None`)
- **Frontend:** Next.js 14 static export (single-page app)
- **Infrastructure:** Manual deployment (terraform exists but not actively used)

---

## Cursor Rules

**Location:** `~/.cursorrules` (symlinked from `~/dotfiles/ide/.cursorrules`)

**Key rules:**
- Execute everything automatically (required_permissions: ["all"])
- Never ask user to run commands in Warp
- All secrets in `~/.config/secrets/global.env`
- No documentation unless asked
- Nudge policy: Execute first, explain only if asked

---

## Deployment Workflows

### Distro Dojo (3-platform deployment)
```bash
# Phase 1: GitHub (push code)
git add . && git commit -m "..." && git push

# Phase 2: Vercel (auto-deploys from GitHub)
# Visit: gozeroshot.dev/mocktailverse (1-2 min delay)

# Phase 3: Portfolio (update gozeroshot.dev)
cd ~/dev/www.gozeroshot.dev
# Edit src/pages/index.astro (add project entry)
git push  # Vercel auto-deploys
```

### Lambda Deployment
```bash
cd scripts/deployment
./deploy-lambdas.sh
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Vercel auto-deploys on git push (connected to GitHub)
```

---

## Portfolio Integration

**Portfolio repo:** `~/dev/www.gozeroshot.dev` (Astro site on Vercel)

**Mocktailverse entry location:** `src/pages/index.astro`

**Live portfolio:** https://gozeroshot.dev

---

## Common Commands

### AWS Check
```bash
source ~/.config/secrets/global.env
aws sts get-caller-identity
aws lambda list-functions --region us-west-2 | grep mocktail
```

### Test API
```bash
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
```

### View Logs
```bash
aws logs tail /aws/lambda/mocktailverse-search --follow
```

### Check DynamoDB
```bash
aws dynamodb scan --table-name mocktailverse-metadata --limit 5
```

---

## Project Context for AI

### What Works
- ✅ All 8 Lambdas deployed and running
- ✅ Frontend live on Vercel
- ✅ API Gateway responding
- ✅ DynamoDB storing data
- ✅ Cost: $1-2/month (MVP)

### Known Gaps
- ⚠️ No CI/CD (manual deployments)
- ⚠️ No tests
- ⚠️ Basic CloudWatch logging (no structured observability)
- ⚠️ Terraform exists but infra was manually deployed
- ⚠️ README claims Claude 3.5, code uses Titan Text Lite

### Design Tradeoffs (For Interviews)
- **DynamoDB vs OpenSearch:** Cost ($0.25 vs $100/month)
- **Titan vs Claude:** FREE tier vs paid (MVP optimization)
- **Single-page app:** Simpler than separate routes
- **Monolithic main.tf:** Easier to read for small project

---

## Git Workflow

```bash
# Current branch: main
# Remote: origin (git@github.com:anix-lynch/mocktailverse-bedrock.git)

# Check status
git status

# Make changes, commit, push
git add .
git commit -m "..."
git push
```

---

## File Organization

**Production code:**
- `backend/lambdas/` - GenAI runtime (6 handlers)
- `frontend/app/` - Next.js UI
- `infra/terraform/` - Infrastructure (exists, not actively used)
- `scripts/deployment/` - Deploy scripts

**Reference/Archive:**
- `lambdas/` - Old duplicate structure (ignore)
- `_deprecated/` - Legacy code (ignore)
- `archive/` - Old experiments (ignore)

---

## Interview Prep Context

**Target roles:**
1. GenAI Data Engineer (primary)
2. MLOps Engineer
3. AI Data Engineer
4. ML Engineer
5. Data Engineer (classic)

**Key selling points:**
- Production-deployed RAG system
- Cost-optimized architecture ($1-2/month)
- Serverless GenAI (Lambda + Bedrock)
- Real AWS deployment (not toy project)

**What to emphasize:**
- Retrieval-augmented generation (RAG)
- Vector embeddings (Titan v2)
- DynamoDB as vector DB (cost optimization)
- Prompt engineering for grounding
- Production guardrails (temperature, refusal rules)

---

## For Future AI Agents

**When user says "deploy this":**
1. Check `scripts/deployment/deploy-lambdas.sh`
2. Source AWS credentials: `source ~/.config/secrets/global.env`
3. Execute with `required_permissions: ["all"]`

**When user says "update portfolio":**
1. Navigate to `~/dev/www.gozeroshot.dev`
2. Edit `src/pages/index.astro`
3. Git push (Vercel auto-deploys)

**When user says "test the API":**
1. Use curl commands (see "Common Commands" section)
2. Check CloudWatch logs if issues

**When in doubt:**
- Read `STRUCTURE.md` for folder layout
- Check deployed resources in this doc
- Source AWS credentials before any AWS command
- Use `required_permissions: ["all"]` for all terminal commands

---

**Last Updated:** 2025-02-12  
**Status:** Production deployed, interview-ready
