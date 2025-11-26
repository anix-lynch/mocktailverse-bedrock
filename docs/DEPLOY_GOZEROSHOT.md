# Deploy Mocktailverse to gozeroshot.dev

## Current Setup
- **CloudFront Distribution ID:** `<CLOUDFRONT_DIST_ID>`
- **Current URL:** `https://<CLOUDFRONT_DOMAIN>.cloudfront.net`
- **Target Domain:** `gozeroshot.dev` (or subdomain like `mocktailverse.gozeroshot.dev`)

## Steps to Deploy

### Option 1: Subdomain (Recommended)
Deploy to `mocktailverse.gozeroshot.dev` or `cocktails.gozeroshot.dev`

### Option 2: Path-based
Deploy to `gozeroshot.dev/mocktailverse` (requires different setup)

---

## Step 1: Request ACM Certificate

```bash
# Request certificate for subdomain
aws acm request-certificate \
  --domain-name mocktailverse.gozeroshot.dev \
  --validation-method DNS \
  --region us-east-1  # CloudFront requires certs in us-east-1

# Get validation DNS records
aws acm describe-certificate \
  --certificate-arn <CERT_ARN> \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
```

**Add DNS records to gozeroshot.dev DNS provider** (NameSilo, Route53, etc.)

---

## Step 2: Update CloudFront Distribution

### Via AWS Console:
1. Go to CloudFront → Distribution `<CLOUDFRONT_DIST_ID>`
2. Click "Edit"
3. Under "Alternate domain names (CNAMEs)": Add `mocktailverse.gozeroshot.dev`
4. Under "Custom SSL certificate": Select your ACM certificate
5. Save changes

### Via Terraform (Recommended):
Add to `terraform/main.tf`:

```hcl
resource "aws_acm_certificate" "mocktailverse" {
  domain_name       = "mocktailverse.gozeroshot.dev"
  validation_method = "DNS"
  provider          = aws.us-east-1  # CloudFront requires us-east-1

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  # ... existing config ...
  
  aliases = ["mocktailverse.gozeroshot.dev"]
  
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.mocktailverse.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
```

---

## Step 3: Update DNS Records

Add CNAME record in your DNS provider (NameSilo, Route53, etc.):

```
Type: CNAME
Name: mocktailverse (or cocktails)
Value: <CLOUDFRONT_DOMAIN>.cloudfront.net
TTL: 3600
```

---

## Step 4: Verify Deployment

```bash
# Wait 5-10 minutes for DNS propagation
curl -I https://mocktailverse.gozeroshot.dev

# Should return 200 OK
```

---

## Quick Deploy Script

```bash
#!/bin/bash
# deploy-to-gozeroshot.sh

set -e

# 1. Build frontend
cd frontend
npm run build
cd ..

# 2. Deploy to S3
source ~/.config/secrets/global.env
aws s3 sync frontend/out/ s3://mocktailverse-frontend-<AWS_ACCOUNT_ID>/ --delete

# 3. Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id <CLOUDFRONT_DIST_ID> \
  --paths "/*"

echo "✅ Deployed! Visit: https://mocktailverse.gozeroshot.dev"
```

---

## Current Status

- ✅ Frontend deployed to S3
- ✅ CloudFront distribution active
- ⏳ Custom domain setup needed
- ⏳ DNS records to be added

**Next:** Follow steps above to add custom domain.



