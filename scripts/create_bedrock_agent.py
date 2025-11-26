#!/usr/bin/env python3
"""
Create Bedrock Agent for Mocktailverse
Uses Titan Text Lite as foundation model
Attaches search-tool Lambda as custom tool
"""
import boto3
import json
import time
from datetime import datetime

# Initialize clients
bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
lambda_client = boto3.client('lambda', region_name='us-west-2')
iam = boto3.client('iam', region_name='us-west-2')
sts = boto3.client('sts', region_name='us-west-2')

# Get AWS account ID
account_id = sts.get_caller_identity()['Account']
region = 'us-west-2'

# Configuration
AGENT_NAME = 'mocktailverse-agent'
FOUNDATION_MODEL = 'amazon.titan-text-lite-v1'  # FREE, ON_DEMAND
SEARCH_TOOL_LAMBDA_NAME = 'mocktailverse-search-tool'

print("🚀 Creating Bedrock Agent for Mocktailverse...")
print(f"   Account: {account_id}")
print(f"   Region: {region}")
print(f"   Foundation Model: {FOUNDATION_MODEL}")
print()

# Step 1: Get Lambda ARN
print("📦 Step 1: Getting Lambda ARN...")
try:
    lambda_response = lambda_client.get_function(FunctionName=SEARCH_TOOL_LAMBDA_NAME)
    lambda_arn = lambda_response['Configuration']['FunctionArn']
    print(f"   ✅ Found Lambda: {lambda_arn}")
except Exception as e:
    print(f"   ❌ Error: Lambda '{SEARCH_TOOL_LAMBDA_NAME}' not found!")
    print(f"   {e}")
    exit(1)

# Step 2: Create IAM role for Bedrock Agent
print("\n🔐 Step 2: Creating IAM role for Bedrock Agent...")
role_name = f"{AGENT_NAME}-role"

# Trust policy for Bedrock to assume the role
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": account_id
                }
            }
        }
    ]
}

# Role permissions
role_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": f"arn:aws:bedrock:{region}::foundation-model/{FOUNDATION_MODEL}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": lambda_arn
        }
    ]
}

try:
    # Try to create role
    role_response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description=f"Role for {AGENT_NAME} Bedrock Agent",
        Tags=[
            {'Key': 'Project', 'Value': 'mocktailverse'},
            {'Key': 'ManagedBy', 'Value': 'script'}
        ]
    )
    role_arn = role_response['Role']['Arn']
    print(f"   ✅ Created role: {role_arn}")
    
    # Attach inline policy
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{AGENT_NAME}-policy",
        PolicyDocument=json.dumps(role_policy)
    )
    print(f"   ✅ Attached permissions policy")
    
    # Wait for role to propagate
    print("   ⏳ Waiting 10 seconds for IAM role to propagate...")
    time.sleep(10)
    
except iam.exceptions.EntityAlreadyExistsException:
    # Role already exists, get its ARN
    role_response = iam.get_role(RoleName=role_name)
    role_arn = role_response['Role']['Arn']
    print(f"   ℹ️  Role already exists: {role_arn}")
    
    # Update policy
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{AGENT_NAME}-policy",
        PolicyDocument=json.dumps(role_policy)
    )
    print(f"   ✅ Updated permissions policy")

# Step 3: Add Lambda permission for Bedrock to invoke it
print("\n🔗 Step 3: Adding Lambda permission for Bedrock Agent...")
try:
    lambda_client.add_permission(
        FunctionName=SEARCH_TOOL_LAMBDA_NAME,
        StatementId=f'BedrockAgentInvoke-{int(time.time())}',
        Action='lambda:InvokeFunction',
        Principal='bedrock.amazonaws.com',
        SourceAccount=account_id
    )
    print(f"   ✅ Added Lambda permission")
except lambda_client.exceptions.ResourceConflictException:
    print(f"   ℹ️  Permission already exists")

# Step 4: Create the Bedrock Agent
print("\n🤖 Step 4: Creating Bedrock Agent...")

agent_instruction = """You are a helpful cocktail expert assistant. You have access to a database of mocktails and cocktails.
When users ask about drinks, recipes, or recommendations, use the search_cocktails tool to find relevant cocktails.

Be friendly, knowledgeable, and concise. Format your responses nicely with ingredients and instructions clearly separated.
"""

try:
    # Check if agent already exists
    agents = bedrock_agent.list_agents()
    existing_agent = None
    for agent in agents.get('agentSummaries', []):
        if agent['agentName'] == AGENT_NAME:
            existing_agent = agent
            break
    
    if existing_agent:
        agent_id = existing_agent['agentId']
        print(f"   ℹ️  Agent already exists: {agent_id}")
        
        # Update the agent
        update_response = bedrock_agent.update_agent(
            agentId=agent_id,
            agentName=AGENT_NAME,
            instruction=agent_instruction,
            foundationModel=FOUNDATION_MODEL,
            agentResourceRoleArn=role_arn,
            description="Mocktail and cocktail recommendation agent"
        )
        print(f"   ✅ Updated agent configuration")
    else:
        # Create new agent
        create_response = bedrock_agent.create_agent(
            agentName=AGENT_NAME,
            instruction=agent_instruction,
            foundationModel=FOUNDATION_MODEL,
            agentResourceRoleArn=role_arn,
            description="Mocktail and cocktail recommendation agent",
            idleSessionTTLInSeconds=600  # 10 minutes
        )
        agent_id = create_response['agent']['agentId']
        print(f"   ✅ Created agent: {agent_id}")
        
        # Wait for agent to be ready for action group creation
        print("   ⏳ Waiting for agent to be ready...")
        for i in range(60):  # Wait up to 60 seconds
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            if status in ['NOT_PREPARED', 'PREPARED']:
                print(f"   ✅ Agent is ready (status: {status})")
                break
            elif status == 'FAILED':
                print(f"   ❌ Agent creation failed!")
                exit(1)
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"   ⏳ Waiting... (status: {status})")

except Exception as e:
    print(f"   ❌ Error creating agent: {e}")
    exit(1)

# Step 5: Define Action Group Schema
print("\n⚙️  Step 5: Creating Action Group with search_cocktails tool...")

# OpenAPI schema for the search tool
api_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Cocktail Search API",
        "version": "1.0.0",
        "description": "API for searching cocktails and mocktails"
    },
    "paths": {
        "/search": {
            "post": {
                "summary": "Search for cocktails",
                "description": "Search the cocktail database by ingredients, keywords, or categories",
                "operationId": "search_cocktails",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query (ingredients, flavors, or keywords)"
                                    },
                                    "limit": {
                                        "type": "integer",
                                        "description": "Maximum number of results to return",
                                        "default": 5
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful search",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "results": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

try:
    # Check for existing action group
    action_groups = bedrock_agent.list_agent_action_groups(agentId=agent_id, agentVersion='DRAFT')
    existing_ag = None
    for ag in action_groups.get('actionGroupSummaries', []):
        if ag['actionGroupName'] == 'search-action-group':
            existing_ag = ag
            break
    
    if existing_ag:
        # Update existing action group
        bedrock_agent.update_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupId=existing_ag['actionGroupId'],
            actionGroupName='search-action-group',
            description='Search cocktails using semantic search',
            actionGroupExecutor={
                'lambda': lambda_arn
            },
            apiSchema={
                'payload': json.dumps(api_schema)
            },
            actionGroupState='ENABLED'
        )
        print(f"   ✅ Updated action group: search-action-group")
    else:
        # Create action group
        bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='search-action-group',
            description='Search cocktails using semantic search',
            actionGroupExecutor={
                'lambda': lambda_arn
            },
            apiSchema={
                'payload': json.dumps(api_schema)
            },
            actionGroupState='ENABLED'
        )
        print(f"   ✅ Created action group: search-action-group")

except Exception as e:
    print(f"   ❌ Error creating action group: {e}")
    print(f"   Details: {e}")
    exit(1)

# Step 6: Prepare the agent
print("\n🔨 Step 6: Preparing agent...")
try:
    prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
    print(f"   ✅ Agent prepared successfully")
    
    # Wait for preparation to complete
    print("   ⏳ Waiting for agent preparation...")
    for i in range(30):  # Wait up to 30 seconds
        agent_status = bedrock_agent.get_agent(agentId=agent_id)
        status = agent_status['agent']['agentStatus']
        if status == 'PREPARED':
            print(f"   ✅ Agent is ready!")
            break
        elif status == 'FAILED':
            print(f"   ❌ Agent preparation failed!")
            exit(1)
        time.sleep(1)
        if i % 5 == 0:
            print(f"   ⏳ Status: {status}...")
    
except Exception as e:
    print(f"   ❌ Error preparing agent: {e}")
    exit(1)

# Step 7: Create an alias
print("\n🏷️  Step 7: Creating agent alias...")
alias_name = 'prod'
try:
    # Check for existing alias
    aliases = bedrock_agent.list_agent_aliases(agentId=agent_id)
    existing_alias = None
    for alias in aliases.get('agentAliasSummaries', []):
        if alias['agentAliasName'] == alias_name:
            existing_alias = alias
            break
    
    if existing_alias:
        alias_id = existing_alias['agentAliasId']
        print(f"   ℹ️  Alias '{alias_name}' already exists: {alias_id}")
    else:
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName=alias_name,
            description='Production alias for mocktailverse agent'
        )
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"   ✅ Created alias: {alias_id}")

except Exception as e:
    print(f"   ❌ Error creating alias: {e}")
    exit(1)

# Step 8: Output configuration
print("\n" + "="*60)
print("✅ BEDROCK AGENT CREATED SUCCESSFULLY!")
print("="*60)
print()
print(f"Agent ID:       {agent_id}")
print(f"Agent Alias ID: {alias_id}")
print(f"Agent Name:     {AGENT_NAME}")
print(f"Foundation:     {FOUNDATION_MODEL}")
print(f"Lambda Tool:    {SEARCH_TOOL_LAMBDA_NAME}")
print()
print("🔧 Next Steps:")
print("1. Update lambdas/agent/handler.py with these values:")
print(f"   AGENT_ID = '{agent_id}'")
print(f"   AGENT_ALIAS_ID = '{alias_id}'")
print()
print("2. Redeploy the agent Lambda:")
print("   cd lambdas/agent && zip -r agent.zip . && aws lambda update-function-code \\")
print("     --function-name mocktailverse-agent --zip-file fileb://agent.zip")
print()
print("3. Test the agent:")
print('   curl -X POST "https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod/agent/chat" \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"message": "Find me a refreshing tropical drink", "session_id": "test-123"}\'')
print()
print("💰 Estimated cost: < $1/month for portfolio usage")
print("="*60)

# Save config to file
config = {
    'agent_id': agent_id,
    'agent_alias_id': alias_id,
    'agent_name': AGENT_NAME,
    'foundation_model': FOUNDATION_MODEL,
    'lambda_arn': lambda_arn,
    'created_at': datetime.now().isoformat()
}

with open('/tmp/bedrock_agent_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n💾 Configuration saved to: /tmp/bedrock_agent_config.json")
