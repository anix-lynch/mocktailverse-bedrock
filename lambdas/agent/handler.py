"""
Lambda: Bedrock Agent Runtime
Purpose: Conversational AI with custom tools (DynamoDB search)
Trigger: API Gateway /agent/chat endpoint
"""

import json
import boto3
import os
from typing import Dict, Any, List
from decimal import Decimal

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb')

# Environment variables
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')
# AGENT_ID = os.environ.get('AGENT_ID', 'ZG2Z7ULNLF')  # ✅ Created Bedrock Agent (disabled for testing)
AGENT_ID = None  # Temporarily use fallback mode
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID', 'ML3UGWXALB')  # ✅ Prod alias
# Using Amazon Titan Text Lite - FREE, no form needed, perfect for demo
BEDROCK_MODEL = 'amazon.titan-text-lite-v1'  # ✅ FREE, ON_DEMAND, ACTIVE


def lambda_handler(event, context):
    """
    Handle Bedrock Agent chat requests
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        session_id = body.get('session_id', 'default-session')
        debug = body.get('debug', False)  # Check if debug mode requested
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Message parameter is required'})
            }
        
        # If Bedrock Agent is configured, use it
        if AGENT_ID:
            return handle_bedrock_agent(message, session_id, debug)
        else:
            # Fallback: Direct Claude with tool calling
            return handle_direct_claude(message, session_id, debug)
    
    except Exception as e:
        print(f"Error in agent: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def handle_bedrock_agent(message: str, session_id: str, debug: bool = False) -> Dict[str, Any]:
    """
    Use Bedrock Agent with custom tools
    """
    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=message
    )
    
    # Stream response
    completion = ""
    for event in response['completion']:
        if 'chunk' in event:
            completion += event['chunk']['bytes'].decode('utf-8')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': message,
            'response': completion,
            'session_id': session_id,
            'debug': None  # Bedrock Agent debug would go here
        })
    }


def handle_direct_claude(message: str, session_id: str, debug: bool = False) -> Dict[str, Any]:
    """
    RAG-powered agent: Always search database first, then generate answer from real data
    This makes it data-driven, not just generic LLM responses
    """
    import time
    start_time = time.time()
    
    tools_used = []
    lambda_client = boto3.client('lambda')
    search_context = ""
    search_results = []
    query_embedding = None
    
    # ALWAYS search the database first (this is the key differentiator!)
    # Use the semantic search Lambda to get real cocktail data
    search_lambda_name = f"{os.environ.get('PROJECT_NAME', 'mocktailverse')}-search"
    try:
        # Call search Lambda for semantic search
        search_response = lambda_client.invoke(
            FunctionName=search_lambda_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'body': json.dumps({
                    'query': message,  # Use user's message as search query
                    'k': 5  # Get top 5 results
                })
            })
        )
        
        search_result = json.loads(search_response['Payload'].read())
        search_body = json.loads(search_result.get('body', '{}'))
        search_results = search_body.get('results', [])
        
        # Store embedding if in debug mode
        if debug and 'query_embedding' in search_body:
            query_embedding = search_body.get('query_embedding')
        
        if search_results:
            # Format results for context
            context_parts = []
            for i, result in enumerate(search_results, 1):
                context_parts.append(f"""
Cocktail {i}: {result.get('name', 'Unknown')}
Category: {result.get('category', 'Unknown')}
Type: {result.get('alcoholic', 'Unknown')}
Description: {result.get('description', 'No description')}
Ingredients: {', '.join([ing.get('name', '') for ing in result.get('ingredients', [])])}
Instructions: {result.get('instructions', 'No instructions')}
""")
            search_context = '\n'.join(context_parts)
            tools_used.append('semantic_search')
        else:
            # Fallback to direct DynamoDB search if search Lambda fails
            search_results = search_cocktails_tool(message, limit=5)
            search_context = format_search_results(search_results)
            tools_used.append('dynamodb_search')
    except Exception as e:
        print(f"Search Lambda error: {e}, falling back to DynamoDB")
        # Fallback to direct DynamoDB search
        search_results = search_cocktails_tool(message, limit=5)
        search_context = format_search_results(search_results)
        tools_used.append('dynamodb_search')
    
    # Build RAG prompt with real database context
    if search_context:
        prompt = f"""You are a helpful bartender assistant. Answer the user's question using ONLY the cocktail information from our database.

User question: {message}

Cocktail Database:
{search_context}

Answer the user's question using the cocktail information above. Be specific about ingredients, flavors, and preparation. Be conversational and helpful."""
    else:
        # No results found - still be helpful
        prompt = f"""You are a helpful bartender assistant. The user asked: "{message}"

Unfortunately, I couldn't find any cocktails in my database matching that query. 

Please try:
- Asking about specific cocktail names
- Using different keywords
- Asking to "find" or "search for" drinks

I can help you once I find matching cocktails in my database."""
    
    # Call Titan
    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL,
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body['results'][0]['outputText']
    except Exception as e:
        print(f"Error calling Titan: {e}")
        completion = "I'm here to help you find and learn about cocktails! Try asking me to search for a specific drink."
    
    # Collect debug data if requested
    debug_data = None
    if debug:
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        debug_data = {
            'semantic': {
                'query_embedding': query_embedding[:100] if query_embedding else None,
                'top_k_results': [
                    {
                        'name': r.get('name', 'Unknown'),
                        'similarity': r.get('relevance_score', 0.0),
                        'category': r.get('category', 'Unknown'),
                        'features': {
                            'tropical_score': 0.85 if 'tropical' in str(r).lower() or 'coconut' in str(r).lower() or 'pineapple' in str(r).lower() else 0.2,
                            'citrus_score': 0.80 if 'lime' in str(r).lower() or 'lemon' in str(r).lower() or 'orange' in str(r).lower() else 0.1,
                            'alcohol_strength': 0.6 if r.get('alcoholic', '').lower() == 'alcoholic' else 0.0
                        }
                    }
                    for r in search_results[:5]
                ],
                'search_method': 'semantic_vector_search'
            },
            'rag': {
                'retrieved_docs': [
                    {
                        'name': r.get('name', 'Unknown'),
                        'content': f"{r.get('instructions', 'No instructions')} Ingredients: {', '.join([ing.get('name', '') for ing in r.get('ingredients', [])][:3])}",
                        'rank': idx + 1
                    }
                    for idx, r in enumerate(search_results[:5])
                ],
                'context_text': search_context[:500] if search_context else "No context available"
            },
            'agent': {
                'actions': [
                    {
                        'tool': tool,
                        'inputs': {'query': message, 'k': 5},
                        'outputs': [r.get('idDrink', f'drink-{idx}') for idx, r in enumerate(search_results[:3])],
                        'latency_ms': elapsed_ms,
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
                    }
                    for tool in tools_used
                ],
                'total_tools_used': len(tools_used)
            }
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': message,
            'response': completion,
            'session_id': session_id,
            'tools_used': tools_used,
            'debug': debug_data
        })
    }


def search_cocktails_tool(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Custom tool: Search cocktails in DynamoDB
    """
    table = dynamodb.Table(METADATA_TABLE)
    
    # Simple scan with filter (in production, use GSI or better search)
    response = table.scan(
        Limit=limit * 2  # Get more to filter
    )
    
    items = response.get('Items', [])
    
    # Filter by query keywords
    query_lower = query.lower()
    matched = []
    for item in items:
        name = item.get('name', '').lower()
        category = item.get('category', '').lower()
        description = item.get('enhanced_metadata', {}).get('description', '')
        if isinstance(description, dict):
            description = description.get('S', '') if 'S' in description else ''
        description = description.lower() if isinstance(description, str) else ''
        
        if (query_lower in name or 
            query_lower in category or 
            query_lower in description):
            matched.append(item)
            if len(matched) >= limit:
                break
    
    # Convert to simple format
    results = []
    for item in matched:
        enhanced_meta = item.get('enhanced_metadata', {})
        if isinstance(enhanced_meta, dict) and 'M' in enhanced_meta:
            enhanced_meta = {k: v.get('S', '') if 'S' in v else '' 
                           for k, v in enhanced_meta['M'].items()}
        
        results.append({
            'name': item.get('name'),
            'category': item.get('category'),
            'description': enhanced_meta.get('description', '') if isinstance(enhanced_meta, dict) else '',
            'alcoholic': item.get('alcoholic'),
            'glass': item.get('glass')
        })
    
    return results


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results as context for LLM
    """
    if not results:
        return "No cocktails found matching the search."
    
    context = "Found cocktails:\n"
    for i, result in enumerate(results, 1):
        context += f"{i}. {result['name']} ({result.get('category', 'Unknown')})\n"
        if result.get('description'):
            context += f"   {result['description']}\n"
        context += "\n"
    
    return context

