#!/usr/bin/env python3
"""
Complete Bedrock Agent setup - add action group and prepare
Run this after agent creation
"""
import boto3
import json
import time

bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
lambda_client = boto3.client('lambda', region_name='us-west-2')

# Configuration from previous creation
AGENT_ID = 'ZG2Z7ULNLF'  # Created agent
SEARCH_TOOL_LAMBDA_NAME = 'mocktailverse-search-tool'

print("🔧 Completing Bedrock Agent setup...")
print(f"   Agent ID: {AGENT_ID}")

# Get Lambda ARN
lambda_response = lambda_client.get_function(FunctionName=SEARCH_TOOL_LAMBDA_NAME)
lambda_arn = lambda_response['Configuration']['FunctionArn']
print(f"   Lambda: {lambda_arn}")

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

# Check agent status
print("\n📊 Checking agent status...")
agent_status = bedrock_agent.get_agent(agentId=AGENT_ID)
status = agent_status['agent']['agentStatus']
print(f"   Status: {status}")

if status not in ['NOT_PREPARED', 'PREPARED']:
    print(f"   ⏳ Waiting for agent to be ready...")
    for i in range(30):
        time.sleep(2)
        agent_status = bedrock_agent.get_agent(agentId=AGENT_ID)
        status = agent_status['agent']['agentStatus']
        if status in ['NOT_PREPARED', 'PREPARED']:
            print(f"   ✅ Agent ready (status: {status})")
            break
        print(f"   ⏳ Still waiting... (status: {status})")

# Create or update action group
print("\n⚙️  Creating action group...")
try:
    action_groups = bedrock_agent.list_agent_action_groups(agentId=AGENT_ID, agentVersion='DRAFT')
    existing_ag = None
    for ag in action_groups.get('actionGroupSummaries', []):
        if ag['actionGroupName'] == 'search-action-group':
            existing_ag = ag
            break
    
    if existing_ag:
        print(f"   ℹ️  Updating existing action group...")
        bedrock_agent.update_agent_action_group(
            agentId=AGENT_ID,
            agentVersion='DRAFT',
            actionGroupId=existing_ag['actionGroupId'],
            actionGroupName='search-action-group',
            description='Search cocktails using semantic search',
            actionGroupExecutor={'lambda': lambda_arn},
            apiSchema={'payload': json.dumps(api_schema)},
            actionGroupState='ENABLED'
        )
        print(f"   ✅ Updated action group")
    else:
        print(f"   ℹ️  Creating new action group...")
        bedrock_agent.create_agent_action_group(
            agentId=AGENT_ID,
            agentVersion='DRAFT',
            actionGroupName='search-action-group',
            description='Search cocktails using semantic search',
            actionGroupExecutor={'lambda': lambda_arn},
            apiSchema={'payload': json.dumps(api_schema)},
            actionGroupState='ENABLED'
        )
        print(f"   ✅ Created action group")

except Exception as e:
    print(f"   ❌ Error with action group: {e}")
    exit(1)

# Prepare the agent
print("\n🔨 Preparing agent...")
try:
    bedrock_agent.prepare_agent(agentId=AGENT_ID)
    print(f"   ✅ Agent preparation started")
    
    # Wait for preparation
    print("   ⏳ Waiting for preparation to complete...")
    for i in range(30):
        time.sleep(2)
        agent_status = bedrock_agent.get_agent(agentId=AGENT_ID)
        status = agent_status['agent']['agentStatus']
        if status == 'PREPARED':
            print(f"   ✅ Agent is PREPARED!")
            break
        elif status == 'FAILED':
            print(f"   ❌ Preparation failed!")
            exit(1)
        if i % 5 == 0:
            print(f"   ⏳ Status: {status}...")
    
except Exception as e:
    print(f"   ❌ Error preparing agent: {e}")
    exit(1)

# Create alias
print("\n🏷️  Creating alias...")
alias_name = 'prod'
try:
    aliases = bedrock_agent.list_agent_aliases(agentId=AGENT_ID)
    existing_alias = None
    for alias in aliases.get('agentAliasSummaries', []):
        if alias['agentAliasName'] == alias_name:
            existing_alias = alias
            break
    
    if existing_alias:
        alias_id = existing_alias['agentAliasId']
        print(f"   ✅ Alias exists: {alias_id}")
    else:
        alias_response = bedrock_agent.create_agent_alias(
            agentId=AGENT_ID,
            agentAliasName=alias_name,
            description='Production alias'
        )
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"   ✅ Created alias: {alias_id}")

except Exception as e:
    print(f"   ❌ Error with alias: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ BEDROCK AGENT READY!")
print("="*60)
print(f"\nAgent ID:       {AGENT_ID}")
print(f"Agent Alias ID: {alias_id}")
print("\n🔧 Update lambdas/agent/handler.py:")
print(f"   AGENT_ID = '{AGENT_ID}'")
print(f"   AGENT_ALIAS_ID = '{alias_id}'")
print("="*60)
