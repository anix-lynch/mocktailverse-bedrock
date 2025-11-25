# 📸 Phase 1: Screenshot Guide

## Quick Start

1. **Run the commands script:**
   ```bash
   chmod +x B_turn/phase1_screenshot_commands.sh
   ./B_turn/phase1_screenshot_commands.sh
   ```

2. **Or run commands individually** (see below)

3. **Take screenshots** of each output

4. **Save screenshots** to `docs/images/` folder

5. **Update README** with image paths

---

## 📋 Screenshots Needed (10 total)

### 1. DynamoDB Table - Sample Records
**Command:**
```bash
aws dynamodb scan --table-name mocktailverse-jobs --limit 5 \
  --query 'Items[*].[job_id.S,title.S,company.S,processed_at.S]' \
  --output table
```

**What to capture:** Table showing sample records with job_id, title, company, processed_at

**Save as:** `docs/images/dynamodb-records.png`

---

### 2. DynamoDB Table - Record Count
**Command:**
```bash
aws dynamodb scan --table-name mocktailverse-jobs --select COUNT
```

**What to capture:** Count number showing total records

**Save as:** `docs/images/dynamodb-count.png`

---

### 3. S3 Raw Bucket - File List
**Command:**
```bash
aws s3 ls s3://mocktailverse-raw/ --recursive --human-readable
```

**What to capture:** List of files in raw bucket

**Save as:** `docs/images/s3-raw-files.png`

---

### 4. S3 Processed Bucket - File List
**Command:**
```bash
aws s3 ls s3://mocktailverse-processed/ --recursive --human-readable
```

**What to capture:** List of processed files

**Save as:** `docs/images/s3-processed-files.png`

---

### 5. S3 Buckets - Storage Summary
**Command:**
```bash
aws s3 ls s3://mocktailverse-raw/ --recursive --summarize --human-readable | tail -2
aws s3 ls s3://mocktailverse-processed/ --recursive --summarize --human-readable | tail -2
```

**What to capture:** Total objects and size for both buckets

**Save as:** `docs/images/s3-storage-summary.png`

---

### 6. Lambda Functions - Status
**Command:**
```bash
aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, `mocktailverse`)].{Name:FunctionName,Status:State,LastModified:LastModified}' \
  --output table
```

**What to capture:** Table showing Lambda function status

**Save as:** `docs/images/lambda-status.png`

---

### 7. CloudWatch Logs - Recent Activity
**Command:**
```bash
aws logs tail /aws/lambda/mocktailverse-transform --since 24h --format short | head -20
```

**What to capture:** Recent log entries showing pipeline activity

**Save as:** `docs/images/cloudwatch-logs.png`

---

### 8. Lambda - Invocation Metrics
**Command:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=mocktailverse-transform \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

**What to capture:** Metrics showing Lambda invocations

**Save as:** `docs/images/lambda-metrics.png`

---

### 9. ETL Metrics - Quick Summary
**Command:**
```bash
echo "Records in DynamoDB:" && \
aws dynamodb scan --table-name mocktailverse-jobs --select COUNT --query 'Count' --output text && \
echo "Files in S3 Processed:" && \
aws s3 ls s3://mocktailverse-processed/ --recursive | wc -l
```

**What to capture:** Quick summary of records and files

**Save as:** `docs/images/etl-summary.png`

---

### 10. Pipeline Health - All Services
**Command:**
```bash
echo "Lambda Functions:" && \
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mocktailverse`)].FunctionName' --output text | wc -w && \
echo "S3 Buckets:" && \
aws s3 ls | grep mocktailverse | wc -l && \
echo "DynamoDB Table:" && \
aws dynamodb describe-table --table-name mocktailverse-jobs --query 'Table.TableStatus' --output text
```

**What to capture:** Health check showing all services operational

**Save as:** `docs/images/pipeline-health.png`

---

## 📁 Folder Structure

Create the images folder:
```bash
mkdir -p docs/images
```

## 🖼️ Adding Images to README

After taking screenshots, add to README:

```markdown
## 📊 Live Metrics

![DynamoDB Records](docs/images/dynamodb-records.png)
![S3 Storage](docs/images/s3-storage-summary.png)
![Lambda Status](docs/images/lambda-status.png)
```

---

## ✅ Checklist

- [ ] Run all 10 commands
- [ ] Take screenshots
- [ ] Save to `docs/images/` folder
- [ ] Update README with image paths
- [ ] Verify images display correctly

---

**Time Estimate:** 15-20 minutes

