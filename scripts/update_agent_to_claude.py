#!/usr/bin/env python3
"""
Update Bedrock Agent to use Claude 3 Haiku
Run this after Claude access is approved
"""
import boto3
import json
import time

bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')

# Configuration
AGENT_ID = 'ZG2Z7ULNLF'
NEW_FOUNDATION_MODEL = 'anthropic.claude-3-haiku-20240307-v1:0'  # Cheapest agent-capable model

print("🔄 Updating Bedrock Agent to use Claude 3 Haiku...")
print(f"   Agent ID: {AGENT_ID}")
print(f"   New Model: {NEW_FOUNDATION_MODEL}")
print()

# Step 1: Get current agent configuration
print("📋 Step 1: Getting current agent configuration...")
try:
    agent_response = bedrock_agent.get_agent(agentId=AGENT_ID)
    agent = agent_response['agent']
    current_model = agent['foundationModel']
    print(f"   Current model: {current_model}")
    print(f"   Status: {agent['agentStatus']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Update agent with Claude
print("\n🔄 Step 2: Updating agent foundation model...")
try:
    update_response = bedrock_agent.update_agent(
        agentId=AGENT_ID,
        agentName=agent['agentName'],
        instruction=agent['instruction'],
        foundationModel=NEW_FOUNDATION_MODEL,
        agentResourceRoleArn=agent['agentResourceRoleArn'],
        description=agent.get('description', 'Mocktail agent with Claude')
    )
    print(f"   ✅ Updated to {NEW_FOUNDATION_MODEL}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 3: Prepare the agent
print("\n🔨 Step 3: Preparing agent with new model...")
try:
    prepare_response = bedrock_agent.prepare_agent(agentId=AGENT_ID)
    print(f"   ✅ Preparation started")
    
    # Wait for preparation
    print("   ⏳ Waiting for preparation...")
    for i in range(30):
        time.sleep(2)
        agent_status = bedrock_agent.get_agent(agentId=AGENT_ID)
        status = agent_status['agent']['agentStatus']
        if status == 'PREPARED':
            print(f"   ✅ Agent is PREPARED with Claude!")
            break
        elif status == 'FAILED':
            print(f"   ❌ Preparation failed!")
            exit(1)
        if i % 5 == 0:
            print(f"   ⏳ Status: {status}...")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ AGENT UPDATED TO CLAUDE 3 HAIKU!")
print("="*60)
print(f"\nAgent ID: {AGENT_ID}")
print(f"Model: {NEW_FOUNDATION_MODEL}")
print("\n🧪 Test the agent:")
print('curl -X POST "https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/agent/chat" \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"message": "Find me a refreshing drink", "session_id": "test-claude"}\'')
print("\n💰 New cost: ~$0.16/month (was $0.10)")
print("="*60)
