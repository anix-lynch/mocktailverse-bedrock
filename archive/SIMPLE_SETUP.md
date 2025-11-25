# Mocktailverse - Simple Setup

## One Command Setup

```bash
cd /Users/anixlynch/dev/northstar/02_mocktailverse
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd api && python test_harness.py
```

## That's it.

The FastAPI test harness will start at http://localhost:8000/docs

### For AWS Deployment:
```bash
./scripts/s3_setup.sh && ./scripts/deploy_lambda.sh && aws dynamodb create-table --cli-input-json file://config/dynamo_schema.json
```

### For Local Database:
```bash
./setup_cockroachdb.sh setup && cd api && python test_harness_with_db.py
```

## Key Principles Implemented:
- ✅ Default to action: Single command setup
- ✅ Reduce friction: No multiple steps required
- ✅ Smart defaults: Assumes common paths
- ✅ Invisible automation: Background processing
- ✅ Token management: Environment variables

## Architecture:
```
FastAPI → S3 → Lambda → DynamoDB
```

## Test:
```bash
curl -X POST "http://localhost:8000/ingest" -H "Content-Type: application/json" -d @data/raw/sample_data.json
```

Done.