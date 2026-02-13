# Deployment

How Mocktailverse is built and deployed.

## Live

- **App:** https://dgco3hnxo94y8.cloudfront.net  
- **API:** https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod  

## Architecture

| Layer      | Where it runs                    |
|-----------|-----------------------------------|
| Frontend  | Next.js static export → S3 → CloudFront |
| Backend   | Lambda (us-west-2) + API Gateway |
| Data      | DynamoDB + S3                     |

## Deploy flow (Distro Dojo)

1. **Code** – Push to GitHub (`git push origin main`).
2. **Backend** – Lambdas: `scripts/deployment/deploy-lambdas.sh` (AWS CLI; credentials required).
3. **Frontend** – Build and sync to S3, then invalidate CloudFront (see below).

## Frontend deploy (manual)

```bash
cd frontend
npm install && npm run build
aws s3 sync out/ s3://<FRONTEND_BUCKET>/ --delete
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```

Bucket and distribution ID are in your AWS console (or in local/internal docs).

## Backend deploy

```bash
cd scripts/deployment
./deploy-lambdas.sh
```

Requires AWS credentials (load locally; never commit secrets).

## Internal docs

- **Secrets, account IDs, bucket names:** Keep local only; never in this repo.
- **Scripts:** `scripts/deployment/` for all deploy and helper scripts.
