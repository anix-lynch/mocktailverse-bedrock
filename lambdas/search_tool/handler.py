"""
Lambda: Search Cocktails Tool
Purpose: Custom tool for Bedrock Agents - searches DynamoDB
This Lambda is invoked as a tool by the Bedrock Agent
"""

import json
import boto3
import os
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')


def lambda_handler(event, context):
    """
    Handle tool invocation from Bedrock Agent
    Event format from Bedrock Agent:
    {
        "actionGroup": "search_cocktails",
        "function": "search",
        "parameters": {
            "query": "tropical drinks"
        }
    }
    """
    try:
        # Parse tool invocation
        query = event.get('parameters', {}).get('query', '')
        limit = event.get('parameters', {}).get('limit', 5)
        
        if not query:
            return {
                "statusCode": 400,
                "message": "Query parameter is required"
            }
        
        # Search DynamoDB
        results = search_cocktails(query, limit)
        
        # Format response for Bedrock Agent
        return {
            "statusCode": 200,
            "message": format_results_for_agent(results)
        }
    
    except Exception as e:
        print(f"Error in search_tool: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Error: {str(e)}"
        }


def search_cocktails(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search cocktails in DynamoDB
    """
    table = dynamodb.Table(METADATA_TABLE)
    
    # Scan with filter (simple keyword search)
    response = table.scan(Limit=limit * 3)
    items = response.get('Items', [])
    
    # Filter by query keywords
    query_lower = query.lower()
    matched = []
    
    for item in items:
        name = item.get('name', '').lower()
        category = item.get('category', '').lower()
        
        # Get description from enhanced_metadata
        enhanced_meta = item.get('enhanced_metadata', {})
        description = ''
        if isinstance(enhanced_meta, dict):
            if 'M' in enhanced_meta:
                desc_obj = enhanced_meta['M'].get('description', {})
                description = desc_obj.get('S', '') if isinstance(desc_obj, dict) else ''
            elif isinstance(enhanced_meta.get('description'), str):
                description = enhanced_meta.get('description', '')
        
        description = description.lower() if description else ''
        
        # Match if query appears in name, category, or description
        if (query_lower in name or 
            query_lower in category or 
            query_lower in description or
            any(word in name for word in query_lower.split())):
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


def format_results_for_agent(results: List[Dict[str, Any]]) -> str:
    """
    Format search results as text for Bedrock Agent
    """
    if not results:
        return "No cocktails found matching your search."
    
    formatted = f"Found {len(results)} cocktail(s):\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"{i}. **{result['name']}** ({result.get('category', 'Unknown')})\n"
        if result.get('description'):
            formatted += f"   {result['description']}\n"
        if result.get('alcoholic'):
            formatted += f"   Type: {result['alcoholic']}\n"
        formatted += "\n"
    
    return formatted




