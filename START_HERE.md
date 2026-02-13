# 🚀 Mocktailverse - Start Here

## For Learning (You)

1. **See structure:** [`STRUCTURE.md`](STRUCTURE.md) - Folder layout + data flow
2. **Read flow diagram:** [`docs/architecture/GENAI_FLOW_MAPPING.md`](docs/architecture/GENAI_FLOW_MAPPING.md)
3. **Read code:** Start with `backend/lambdas/` (read handlers in any order)

**That's it. Learn from code, not docs.**

---

## For AI Agents (Future)

Read: [`AI_CONTEXT.md`](AI_CONTEXT.md)

Everything you need:
- AWS credentials location
- Deployed resources
- Secrets management
- Deployment workflows
- Common commands

---

## Quick Test

```bash
# Test API
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/search \
  -H "Content-Type: application/json" \
  -d '{"query":"mojito"}'
```

---

**Live:** https://gozeroshot.dev/mocktailverse
