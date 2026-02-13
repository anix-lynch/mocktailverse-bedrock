# 🎯 IDE Navigation Guide - What You Should See

> **Your Cursor IDE should now show ONLY the clean structure**

---

## What Your IDE File Tree Should Look Like NOW

```
MOCKTAILVERSE-BEDROCK/
│
├── 📂 backend/                    👈 Click to expand
│   └── lambdas/
│       ├── agent/
│       ├── embed/
│       ├── ingest/
│       ├── rag/
│       ├── search/
│       └── search_tool/
│
├── 📂 frontend/                   👈 Click to expand
│   └── app/
│       ├── page.tsx               👈 Read this first
│       ├── layout.tsx
│       ├── components/
│       └── globals.css
│
├── 📂 infra/                      👈 Infrastructure
│   └── terraform/
│       └── main.tf
│
├── 📂 docs/                       👈 All documentation here
│   ├── START_HERE.md              👈 Start your learning here
│   ├── WALKTHROUGH.md             👈 Interview prep
│   ├── architecture/
│   │   └── GENAI_FLOW_MAPPING.md  👈 Key system doc
│   └── [other guides]
│
├── 📂 scripts/                    👈 Deployment tools
│   └── deployment/
│
├── 📂 workflows/                  👈 Orchestration
│
├── 📄 README.md                   👈 Project overview
└── 📄 .cursorignore               👈 Hides messy folders
```

---

## What You Should NOT See Anymore

These folders are now hidden (via .cursorignore):
- ❌ `_deprecated/` 
- ❌ `archive/`
- ❌ `lambdas/` (old duplicate)
- ❌ `data/`

If you still see them: **Restart Cursor IDE** or run:
```bash
# Refresh IDE
code . --reuse-window
```

---

## Learning Path (Click in This Order)

### 1. Start Here (5 min)
📁 `docs/START_HERE.md` ← Overview

### 2. Understand Architecture (10 min)
📁 `docs/architecture/GENAI_FLOW_MAPPING.md` ← System flow

### 3. Read Production Code (15 min)

**Backend (in order):**
1. 📁 `backend/lambdas/ingest/handler.py` ← Data pipeline
2. 📁 `backend/lambdas/embed/handler.py` ← Embeddings
3. 📁 `backend/lambdas/search/handler.py` ← Vector search
4. 📁 `backend/lambdas/rag/handler.py` ← RAG pipeline
5. 📁 `backend/lambdas/agent/handler.py` ← Agent orchestrator

**Frontend:**
1. 📁 `frontend/app/page.tsx` ← Main UI

**Infrastructure:**
1. 📁 `infra/terraform/main.tf` ← AWS resources

---

## Quick Navigation Tips

### Use Cursor's Command Palette
Press `Cmd+P` (Mac) or `Ctrl+P` (Windows) and type:

- `handler.py` → See all Lambda handlers
- `page.tsx` → Jump to frontend
- `main.tf` → Jump to infrastructure
- `START_HERE` → Jump to learning guide

### Use Cursor's File Search
Press `Cmd+Shift+F` (Mac) or `Ctrl+Shift+F` (Windows) to search:

- `def lambda_handler` → Find all Lambda entry points
- `bedrock.invoke_model` → Find all Bedrock calls
- `DynamoDB` → Find all database operations
- `fetch(` → Find all API calls in frontend

---

## Folder Purposes (Quick Reference)

| Folder | Purpose | When to Open |
|--------|---------|--------------|
| `backend/lambdas/` | GenAI runtime code | Learning system logic |
| `frontend/app/` | UI code | Understanding user interface |
| `infra/terraform/` | AWS resources | Understanding infrastructure |
| `docs/` | All documentation | Interview prep & learning |
| `scripts/deployment/` | Deploy scripts | When deploying changes |
| `workflows/` | Orchestration docs | Understanding automation |

---

## What Each Lambda Does (From IDE)

**Right-click any Lambda folder → "Open in Integrated Terminal"**

Then read the handler.py docstring:

### agent/handler.py
```python
"""
Lambda: Bedrock Agent Runtime
Purpose: Conversational AI with custom tools
Trigger: API Gateway /agent/chat endpoint
"""
```

### embed/handler.py
```python
"""
Lambda: Embedding Generation
Purpose: Generate 1536-dim vectors via Titan Embeddings v2
Trigger: S3 upload or manual invocation
"""
```

### ingest/handler.py
```python
"""
Lambda: Ingest & Extract
Purpose: Fetch cocktail data and use Bedrock Claude to extract/enrich
Trigger: EventBridge schedule or S3 upload
"""
```

### rag/handler.py
```python
"""
Lambda: RAG Retrieval
Purpose: Retrieval-Augmented Generation using Bedrock
Trigger: API Gateway /v1/rag endpoint
"""
```

### search/handler.py
```python
"""
Lambda: Vector Search
Purpose: Semantic search using DynamoDB KNN
Trigger: API Gateway /v1/search endpoint
"""
```

---

## IDE Shortcuts (Learn the Repo Faster)

### Cursor-Specific
- `Cmd+K` → Ask Cursor about code
  - Example: "Explain this Lambda function"
  - Example: "How does RAG work here?"

### VS Code Standard
- `Cmd+P` → Quick open file
- `Cmd+Shift+F` → Search across files
- `Cmd+B` → Toggle sidebar
- `Cmd+\` → Split editor
- `F12` → Go to definition
- `Shift+F12` → Find all references

---

## Learning Checklist

Use this to track your progress:

```
□ Read docs/START_HERE.md
□ Read docs/architecture/GENAI_FLOW_MAPPING.md
□ Read backend/lambdas/ingest/handler.py
□ Read backend/lambdas/embed/handler.py
□ Read backend/lambdas/search/handler.py
□ Read backend/lambdas/rag/handler.py
□ Read backend/lambdas/agent/handler.py
□ Read frontend/app/page.tsx
□ Read infra/terraform/main.tf
□ Read docs/WALKTHROUGH.md (interview prep)
□ Test API endpoints (curl commands)
□ Understand cost tradeoffs (Titan vs Claude, DynamoDB vs OpenSearch)
```

**Estimated time:** 30-45 minutes

---

## If You Get Lost

1. **Return to START_HERE.md:** `docs/START_HERE.md`
2. **Check the flow diagram:** `docs/architecture/GENAI_FLOW_MAPPING.md`
3. **Review folder structure:** `docs/PROJECT_STRUCTURE.md`

---

## Pro Tip: Create Cursor Bookmarks

Right-click these files → "Add to Favorites":
- `docs/START_HERE.md`
- `docs/WALKTHROUGH.md`
- `backend/lambdas/rag/handler.py`
- `frontend/app/page.tsx`

**Now you can access them instantly from the sidebar.**

---

**Your IDE is now clean and ready for learning. Start with: `docs/START_HERE.md`**
