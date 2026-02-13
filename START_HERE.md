# Mocktailverse

## Quick Start

**Structure:** See [STRUCTURE.md](STRUCTURE.md) for folder layout

**Architecture:** See [docs/architecture/](docs/architecture/) for system design

**Code:** Production code is in `backend/lambdas/` and `frontend/app/`

## Local Development

```bash
# Test API
curl -X POST https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/search \
  -H "Content-Type: application/json" \
  -d '{"query":"mojito"}'
```

## Deployment

See `scripts/deployment/` for deploy scripts.

**Live:** https://gozeroshot.dev/mocktailverse
