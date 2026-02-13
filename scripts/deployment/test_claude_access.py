#!/usr/bin/env python3
"""
Test if Claude access is ready
"""
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

print("🧪 Testing Claude 3 Haiku access...")
print(f"   Model: {MODEL_ID}")
print()

try:
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 20,
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello in 3 words"
                }
            ]
        })
    )
    
    response_body = json.loads(response['body'].read())
    message = response_body['content'][0]['text']
    
    print("✅ SUCCESS! Claude access is ACTIVE!")
    print(f"   Response: {message}")
    print()
    print("🎉 You can now update your Bedrock Agent to use Claude!")
    print("   Run: python3 scripts/update_agent_to_claude.py")
    
except Exception as e:
    error_str = str(e)
    if "AccessDeniedException" in error_str or "access" in error_str.lower():
        print("⏳ Access not ready yet (this is normal)")
        print("   Anthropic approval usually takes 5-15 minutes")
        print("   You should receive an email when approved")
        print()
        print("💡 In the meantime:")
        print("   - Check your email for approval notification")
        print("   - Wait 5-10 minutes and run this script again")
        print()
        print("   Run: python3 scripts/test_claude_access.py")
    else:
        print(f"❌ Error: {e}")
