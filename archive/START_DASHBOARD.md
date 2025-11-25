# 🚀 Start Your Dashboard

## Quick Start (Web Dashboard)

### Option 1: Local Web Dashboard (Easiest)

```bash
cd api
python view_dashboard.py
```

Then open: **http://localhost:8000**

You'll see:
- Total record count
- Table of all your data
- Auto-refresh button

---

## All Ways to View Your Data

### 1. **Web Dashboard** (Best for viewing)
```bash
cd api && python view_dashboard.py
# Open http://localhost:8000
```

### 2. **Command Line Viewer** (Quick check)
```bash
./view_data.sh
```

### 3. **AWS Console** (Official AWS interface)
- DynamoDB: https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables
- S3: https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1
- Lambda: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions

### 4. **Command Line** (For developers)
```bash
# View table
aws dynamodb scan --table-name mocktailverse-jobs --limit 10

# Count records
aws dynamodb scan --table-name mocktailverse-jobs --select COUNT
```

---

## What You'll See

**In the Dashboard:**
- Total number of records
- Table showing: ID, Title, Company, Location, Processed Date
- Refresh button to update

**In AWS Console:**
- Full DynamoDB interface
- Can edit/delete records
- See detailed metrics
- View CloudWatch logs

---

## Troubleshooting

**Dashboard won't start?**
- Make sure you're in the `api` directory
- Check AWS credentials: `aws sts get-caller-identity`
- Install dependencies: `pip install fastapi uvicorn boto3`

**No data showing?**
- Run: `./view_data.sh` to check if data exists
- Fetch some data: See `VIEW_YOUR_DATA.md`

