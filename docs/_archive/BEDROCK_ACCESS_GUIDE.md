# 🚀 Bedrock Access Request Guide

## ⚠️ Why GUI is Required

**Bedrock model access CANNOT be requested via CLI.** Anthropic requires a use case form that must be filled out in the AWS Console. This is a security/approval requirement.

## 🔗 Direct Console Links

### Option 1: Model Access Page (Recommended)
**Direct Link:**
```
https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess
```

### Option 2: Bedrock Dashboard
```
https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2
```
Then click "Model access" in left sidebar

## 📝 Step-by-Step (First Time)

### Step 1: Open Console
Click the link above (Option 1 is fastest)

### Step 2: Find Anthropic Section
- Scroll to "Anthropic" provider section
- You'll see models like:
  - Claude Sonnet 4 (newer, recommended)
  - Claude 3.5 Sonnet v2 (what we're using - LEGACY)
  - Claude Haiku 4.5
  - Claude Opus 4.5

### Step 3: Request Access
- Click "Request" or "Enable" button next to:
  - **Claude 3.5 Sonnet v2** (what our code uses)
  - OR **Claude Sonnet 4** (newer, better - we can update code)

### Step 4: Fill Out Form
**Use Case:** Select one:
- "Development/Testing" (recommended for personal projects)
- "Personal Project"
- "Educational"

**Description (optional but helpful):**
```
Building a GenAI data engineering platform (Mocktailverse) 
for cocktail recipe semantic search using Bedrock Agents 
and custom tools. Personal portfolio project.
```

### Step 5: Submit
- Click "Submit" or "Request access"
- You'll see a confirmation message

### Step 6: Wait
- **Wait time:** 15 minutes (usually instant, but can take up to 15 min)
- You'll get an email when approved

## ✅ Verify Access (After Approval)

### Test via CLI:
```bash
# Test Claude 3.5 Sonnet v2 (current code)
echo '{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}' | \
  base64 | \
  aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
    --body file:///dev/stdin \
    --region us-west-2 \
    /tmp/test.json && \
  cat /tmp/test.json | jq -r '.content[0].text'
```

### Test via API:
```bash
curl -X POST https://<API_GATEWAY_ID>.execute-api.us-west-2.amazonaws.com/prod/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test-123"}'
```

## 🎯 Recommended: Use Claude Sonnet 4 Instead

Since Claude 3.5 Sonnet v2 is LEGACY, consider updating to **Claude Sonnet 4**:

**Model ID:** `anthropic.claude-sonnet-4-20250514-v1:0`

**Benefits:**
- ✅ Newer model (better performance)
- ✅ Still ACTIVE (not legacy)
- ✅ Same API format

**Update needed:**
- Change model ID in `lambdas/agent/handler.py`
- Change model ID in `lambdas/rag/handler.py`
- Change model ID in `lambdas/ingest/handler.py`

## 📋 Current Status

**Available Models (can list):**
- ✅ Claude Sonnet 4 (ACTIVE) - **Recommended**
- ✅ Claude 3.5 Sonnet v2 (LEGACY) - Current code uses this
- ✅ Claude Haiku 4.5 (ACTIVE)
- ✅ Claude Opus 4.5 (ACTIVE)

**Access Status:**
- ❌ Cannot invoke (use case form not submitted)
- ✅ Can list models (access to Bedrock service)

## 🔧 After Access is Granted

Once approved, your agent endpoint will work:

```bash
curl -X POST https://<API_GATEWAY_ID>.execute-api.us-west-2.amazonaws.com/prod/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me a refreshing tropical drink",
    "session_id": "user-123"
  }'
```

**Expected Response:**
```json
{
  "message": "Find me a refreshing tropical drink",
  "response": "I found some great tropical drinks! Here are a few options...",
  "session_id": "user-123",
  "tools_used": ["search_cocktails"]
}
```

---

**TL;DR:** Must use GUI. Click link → Request access → Wait 15 min → Done! 🎉



