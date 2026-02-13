# Actual Folder Tree (As of 2025-02-12)

## Full ASCII Tree Output

```
mocktailverse-bedrock/
|
|-- GIT_SECURITY_CHECKLIST.md
|-- PROJECT_STRUCTURE.md
|-- README.md
|-- REORGANIZATION_SUMMARY.md
|-- REPO_ASCII_COMPARISON.md
|-- TEMPLATE_VS_REALITY.md
|-- WALKTHROUGH.md                    👈 Interview prep guide
|
|-- backend/                          👈 PRODUCTION CODE
|   `-- lambdas/
|       |-- agent/
|       |   |-- handler.py
|       |   `-- requirements.txt
|       |-- embed/
|       |   |-- handler.py
|       |   `-- requirements.txt
|       |-- ingest/
|       |   |-- handler.py
|       |   `-- requirements.txt
|       |-- rag/
|       |   |-- handler.py
|       |   `-- requirements.txt
|       |-- search/
|       |   |-- handler.py
|       |   `-- requirements.txt
|       `-- search_tool/
|           |-- handler.py
|           `-- requirements.txt
|
|-- frontend/                         👈 PRODUCTION UI
|   |-- app/
|   |   |-- components/
|   |   |   `-- DebugPanel.tsx
|   |   |-- globals.css
|   |   |-- layout.tsx
|   |   `-- page.tsx                  👈 Main UI
|   |-- next.config.js
|   |-- package.json
|   |-- public/
|   |   `-- favicon.ico
|   `-- tsconfig.json
|
|-- infra/                            👈 INFRASTRUCTURE
|   `-- terraform/
|       `-- main.tf
|
|-- workflows/                        👈 ORCHESTRATION
|   `-- README.md
|
|-- docs/                             👈 DOCUMENTATION
|   |-- architecture/
|   |   |-- ARCHITECTURE.md
|   |   |-- GENAI_FLOW_MAPPING.md     👈 Key doc
|   |   `-- README.md
|   |-- ARCHITECTURE_MAPS.md
|   |-- BEDROCK_ACCESS_GUIDE.md
|   |-- DEPLOYMENT_GUIDE.md
|   `-- TECHNICAL_OVERVIEW.md
|
|-- scripts/                          👈 DEVOPS (10+ scripts)
|   |-- deployment/
|   |   |-- deploy-lambdas.sh
|   |   |-- deploy_mvp.sh
|   |   |-- load_sample_data.py
|   |   `-- [20+ other scripts]
|   |-- deploy-lambdas.sh
|   |-- deploy_mvp.sh
|   |-- load_sample_data.py
|   `-- [duplicates in root - can clean up]
|
|-- data/                             👈 SAMPLE DATA
|   |-- dynamodb_schema.json
|   |-- margarita_recipes.json
|   |-- test_payload.json
|   `-- raw/
|
|-- lambdas/                          👈 OLD STRUCTURE (reference)
|   |-- agent/
|   |-- embed/
|   |-- ingest/
|   |-- rag/
|   |-- search/
|   `-- search_tool/
|
|-- _deprecated/                      👈 ARCHIVED CODE
|   |-- lambda/
|   `-- legacy/
|
`-- archive/                          👈 OLD DOCS/EXPERIMENTS
    |-- B_turn/
    `-- [old project docs]

```

---

## Clean View (Interview-Friendly)

### Production Code (Show These)
```
backend/lambdas/               # 6 Lambda functions
  ├── agent/                   # Bedrock Agent
  ├── embed/                   # Titan Embeddings
  ├── ingest/                  # Data pipeline
  ├── rag/                     # RAG retrieval
  ├── search/                  # Vector search
  └── search_tool/             # Agent tool wrapper

frontend/app/                  # Next.js UI
  ├── page.tsx                 # Main interface
  ├── layout.tsx               # Root layout
  ├── components/              # React components
  └── globals.css              # Styles

infra/terraform/               # Infrastructure
  └── main.tf                  # AWS resources

docs/architecture/             # System design
  ├── GENAI_FLOW_MAPPING.md    # Mental model
  └── ARCHITECTURE.md          # Diagrams

scripts/deployment/            # DevOps
  ├── deploy-lambdas.sh        # Lambda deploy
  └── load_sample_data.py      # Seed data
```

### Skip for Interviews
```
lambdas/                       # Old structure (use backend/ instead)
_deprecated/                   # Legacy code
archive/                       # Old experiments
data/                          # Sample data files
```

---

## File Count by Category

| Category | Files | Status |
|----------|-------|--------|
| **Backend Lambdas** | 12 files (6 handlers + 6 requirements) | ✅ Production |
| **Frontend** | 8 files (page, layout, config, etc.) | ✅ Production |
| **Infrastructure** | 1 file (main.tf) | ✅ Production |
| **Scripts** | 20+ files | ✅ DevOps utilities |
| **Docs** | 8 files | ✅ Architecture guides |
| **Interview Guides** | 4 files (WALKTHROUGH.md, etc.) | ✅ Ready |
| **Deprecated** | ~30 files | ⚠️ Skip for interviews |
| **Archive** | ~20 files | ⚠️ Old experiments |

**Total:** 117 files in 41 directories

---

## Duplicates to Clean Up (Optional)

**Problem:** You have duplicate scripts in two places:
- `scripts/` (root level)
- `scripts/deployment/` (subfolder)

**Solution:**
```bash
# Move everything to deployment/ and remove root duplicates
mv scripts/*.sh scripts/*.py scripts/deployment/ 2>/dev/null
```

**Or leave it** - doesn't affect interviews.

---

## What Interviewer Will See

When you share screen and run `tree -L 2`:

```
.
├── backend/lambdas/           ← "Here's my GenAI runtime"
├── frontend/app/              ← "Here's my Next.js UI"
├── infra/terraform/           ← "Here's my infrastructure"
├── docs/architecture/         ← "Here's my system design"
├── scripts/deployment/        ← "Here's my DevOps"
└── WALKTHROUGH.md             ← "Here's my prep guide"
```

**Clean. Organized. Professional.**

---

## Commands for Interview

### Show Clean Structure
```bash
tree -L 2 -I 'node_modules|.git|_deprecated|archive|lambdas'
```

### Show Production Lambdas
```bash
ls -lh backend/lambdas/
```

### Show Frontend
```bash
ls -lh frontend/app/
```

### Show Docs
```bash
ls -lh docs/architecture/
```

---

## Summary

**Your structure is interview-ready.**

- ✅ 41 directories, 117 files
- ✅ Clean separation: backend / frontend / infra / docs
- ✅ 6 production Lambda functions
- ✅ 8 architecture documents
- ✅ 20+ deployment scripts

**Focus on:** `backend/`, `frontend/`, `infra/`, `docs/architecture/`

**Ignore:** `_deprecated/`, `archive/`, `lambdas/` (old)

**You're ready.**
