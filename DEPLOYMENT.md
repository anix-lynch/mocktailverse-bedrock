# 🚀 AWS Deployment Guide - Mocktailverse ETL Pipeline

Complete deployment guide for running the full AWS ETL pipeline (Airflow + Glue + Lambda + dbt) on AWS Free Tier.

---

## 🎯 What You'll Deploy

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Amazon S3     │───▶│   AWS Glue      │───▶│  DynamoDB       │
│   (Extract)     │    │   (Transform)   │    │   (Load)        │
│   5GB Free      │    │   1 DPU-hr/mo   │    │   25GB Free     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS Lambda    │    │ EC2 t2.micro    │    │     dbt-core    │
│ (Enrichment)    │    │  (Airflow)      │    │   (Modeling)    │
│   1M req/mo     │    │  750 hrs/mo     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Live Components Recruiters Will See
✅ **EC2 Instance** running Apache Airflow at `http://<public-ip>:8080`
✅ **AWS Lambda** processing data with CloudWatch logs
✅ **AWS Glue** ETL jobs with execution history
✅ **DynamoDB** tables with actual cocktail data
✅ **S3 Buckets** with raw/processed data
✅ **Streamlit Dashboard** monitoring pipeline in real-time

---

## 💰 Cost Breakdown (100% Free Tier)

| Service | Usage | Free Tier Limit | Cost |
|---------|-------|-----------------|------|
| EC2 t2.micro | Airflow host | 750 hrs/month | **$0/mo** |
| AWS Lambda | Data transform | 1M requests/month | **$0/mo** |
| AWS Glue | PySpark ETL | 1 DPU-hour/month | **$0/mo** |
| S3 Storage | Data lake | 5GB + 20K GET | **$0/mo** |
| DynamoDB | NoSQL DB | 25GB + 200M req | **$0/mo** |
| **TOTAL** | | | **$0/mo** |

**⚠️ Important:** Monitor usage at [AWS Billing Dashboard](https://console.aws.amazon.com/billing)

---

## 📋 Prerequisites

### 1. AWS Account Setup
```bash
# Check AWS credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDXXXXXXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/yourname"
# }
```

### 2. Required Tools
- AWS CLI v2
- Git
- Python 3.11+
- Bash shell

---

## 🚀 One-Command Deployment

### Deploy Everything
```bash
cd /path/to/mocktailverse
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

**What This Does:**
1. Creates CloudFormation stack (~10 minutes)
2. Provisions EC2, S3, DynamoDB, Lambda, Glue
3. Installs Airflow on EC2
4. Uploads Lambda function code
5. Uploads Glue job scripts
6. Loads sample cocktail data
7. Outputs all access URLs

### Expected Output
```
🎉 Deployment Complete!
========================================

📊 Access Your Infrastructure:
   Airflow UI: http://3.234.567.89:8080
   Username: admin
   Password: admin

🗄️ AWS Resources:
   Raw Data Bucket: mocktailverse-raw-data-123456789012
   Processed Bucket: mocktailverse-processed-data-123456789012
   DynamoDB Table: mocktailverse-cocktails
   Lambda Function: mocktailverse-transform-lambda
```

---

## 🔧 Post-Deployment Steps

### 1. Access Airflow UI
```bash
# Get Airflow URL from CloudFormation output
aws cloudformation describe-stacks \
    --stack-name mocktailverse-etl-stack \
    --query 'Stacks[0].Outputs[?OutputKey==`AirflowURL`].OutputValue' \
    --output text

# Open in browser: http://<ec2-ip>:8080
# Login: admin / admin
```

### 2. Trigger First Pipeline Run
1. Navigate to **DAGs** tab in Airflow UI
2. Find `mocktailverse_etl_pipeline`
3. Click **▶️ Trigger DAG**
4. Monitor execution in **Graph View**

### 3. Verify Data in DynamoDB
```bash
# Query DynamoDB table
aws dynamodb scan \
    --table-name mocktailverse-cocktails \
    --limit 5 \
    --region us-east-1

# Expected: JSON output with cocktail records
```

### 4. Launch Streamlit Dashboard
```bash
# Run locally (connects to AWS resources)
streamlit run streamlit_app.py

# Or deploy to Streamlit Cloud:
# 1. Push to GitHub (already done)
# 2. Go to https://share.streamlit.io/
# 3. Connect repo: anix-lynch/mocktailverse
# 4. Main file: streamlit_app.py
```

---

## 📊 Monitoring & Validation

### CloudWatch Logs
```bash
# View Lambda logs
aws logs tail /aws/lambda/mocktailverse-transform-lambda --follow

# View Glue job logs
aws glue get-job-runs --job-name mocktailverse-etl-transform
```

### DynamoDB Data Check
```bash
# Count records
aws dynamodb describe-table \
    --table-name mocktailverse-cocktails \
    --query 'Table.ItemCount'
```

### S3 Data Check
```bash
# List raw data
aws s3 ls s3://mocktailverse-raw-data-$ACCOUNT_ID/ --recursive

# List processed data
aws s3 ls s3://mocktailverse-processed-data-$ACCOUNT_ID/ --recursive
```

---

## 🧹 Teardown (When Done)

### Remove All Resources
```bash
chmod +x deploy/destroy.sh
./deploy/destroy.sh

# Confirm with: yes
```

**What This Does:**
1. Empties all S3 buckets
2. Deletes CloudFormation stack
3. Removes EC2, Lambda, Glue, DynamoDB
4. Zero cost after deletion

---

## 🎓 For Recruiters & Hiring Managers

### How to Validate This Project

1. **Check GitHub Repository**
   - URL: https://github.com/anix-lynch/mocktailverse
   - Look for: CloudFormation templates, Airflow DAG, Lambda functions, dbt models

2. **Request Live Demo** (if deployed)
   - Airflow UI: Pipeline orchestration and scheduling
   - DynamoDB: Query cocktail data via AWS Console
   - CloudWatch: View Lambda execution logs
   - Streamlit: Live monitoring dashboard

3. **Verify Free Tier Compliance**
   - All components stay within AWS Free Tier limits
   - Cost-conscious architecture design
   - Production-ready but budget-friendly

4. **Review Code Quality**
   - Type hints and docstrings
   - Error handling and logging
   - Infrastructure as Code (CloudFormation)
   - CI/CD ready (GitHub Actions compatible)

### Key Takeaways
✅ **Enterprise ETL Skills**: Airflow, Glue, Lambda, dbt orchestration
✅ **AWS Expertise**: Multi-service integration, IAM roles, CloudFormation
✅ **Cost Optimization**: $0/month using Free Tier efficiently
✅ **Production-Ready**: Monitoring, logging, error handling, scalability
✅ **Data Engineering**: ETL/ELT patterns, data quality, pipeline design

---

## 🐛 Troubleshooting

### Issue: Airflow UI Not Loading
```bash
# SSH into EC2 instance
INSTANCE_ID=$(aws cloudformation describe-stack-resources \
    --stack-name mocktailverse-etl-stack \
    --query 'StackResources[?LogicalResourceId==`AirflowInstance`].PhysicalResourceId' \
    --output text)

# Check Airflow status
aws ssm start-session --target $INSTANCE_ID
sudo systemctl status airflow-webserver
sudo systemctl status airflow-scheduler

# Restart if needed
sudo systemctl restart airflow-webserver
```

### Issue: Lambda Function Failing
```bash
# Check logs
aws logs tail /aws/lambda/mocktailverse-transform-lambda --since 1h

# Test function manually
aws lambda invoke \
    --function-name mocktailverse-transform-lambda \
    --payload '{"test": true}' \
    response.json
```

### Issue: DynamoDB Access Denied
```bash
# Verify IAM role permissions
aws iam get-role-policy \
    --role-name mocktailverse-lambda-role \
    --policy-name DynamoDBAccess
```

---

## 📚 Additional Resources

- [AWS Free Tier Guide](https://aws.amazon.com/free/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

---

## 💡 Next Steps

Once deployed, you can:
1. **Add More Data Sources**: Extend DAG to pull from APIs
2. **Enhance dbt Models**: Create more analytics tables
3. **Set Up Alerts**: SNS notifications for pipeline failures
4. **Add CI/CD**: GitHub Actions for automated deployments
5. **Scale Up**: Increase DynamoDB/Lambda capacity as needed

---

**Questions?** Open an issue on [GitHub](https://github.com/anix-lynch/mocktailverse/issues)
