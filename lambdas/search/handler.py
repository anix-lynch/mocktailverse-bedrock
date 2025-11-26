"""
Lambda: Vector Search
Purpose: Semantic search using OpenSearch Serverless
Trigger: API Gateway /v1/search endpoint
"""

import json
import boto3
import os
from typing import Dict, Any, List

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb')

# Environment variables
OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'cocktails')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')
BEDROCK_EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'

# OpenSearch client (optional - only if opensearchpy is available)
opensearch_client = None
try:
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    
    if OPENSEARCH_ENDPOINT:
        region = 'us-west-2'
        service = 'aoss'  # OpenSearch Serverless
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token
        )
        
        opensearch_client = OpenSearch(
            hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
except ImportError:
    # opensearchpy not available - will use DynamoDB fallback
    pass


def lambda_handler(event, context):
    """
    Handle semantic search requests
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        k = body.get('k', 5)  # Number of results
        filters = body.get('filters', {})
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Search OpenSearch
        results = search_vectors(query_embedding, k=k, filters=filters)
        
        # Enrich with metadata
        enriched_results = enrich_results(results)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'query': query,
                'results': enriched_results,
                'count': len(enriched_results)
            })
        }
    
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for search query
    """
    response = bedrock.invoke_model(
        modelId=BEDROCK_EMBEDDING_MODEL,
        body=json.dumps({"inputText": text})
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embedding']


def search_vectors(
    query_embedding: List[float],
    k: int = 5,
    filters: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Search OpenSearch using KNN
    """
    if not opensearch_client:
        # Fallback: simple DynamoDB scan (for testing without OpenSearch)
        return fallback_search(query_embedding, k)
    
    # Build OpenSearch query
    query_body = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": k
                }
            }
        }
    }
    
    # Add filters if provided
    if filters:
        must_clauses = []
        if 'category' in filters:
            must_clauses.append({"term": {"category": filters['category']}})
        if 'alcoholic' in filters:
            must_clauses.append({"term": {"alcoholic": filters['alcoholic']}})
        
        if must_clauses:
            query_body["query"] = {
                "bool": {
                    "must": must_clauses,
                    "should": [query_body["query"]]
                }
            }
    
    # Execute search
    response = opensearch_client.search(
        index=OPENSEARCH_INDEX,
        body=query_body
    )
    
    # Parse results
    results = []
    for hit in response['hits']['hits']:
        results.append({
            'cocktail_id': hit['_source']['cocktail_id'],
            'score': hit['_score'],
            'name': hit['_source']['name'],
            'category': hit['_source'].get('category'),
            'description': hit['_source'].get('description')
        })
    
    return results


def fallback_search(query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
    """
    Fallback search using DynamoDB scan (for testing)
    Returns all items with mock relevance scores
    """
    table = dynamodb.Table(METADATA_TABLE)
    response = table.scan()
    
    items = response.get('Items', [])
    
    # Return all items with mock scores (since we don't have embeddings yet)
    scored_items = []
    for item in items:
        # Use a mock score based on name/description matching
        # In production, you'd load the embedding from S3 and calculate cosine similarity
        score = 0.8  # Mock score for all items
        scored_items.append({
            'cocktail_id': item.get('cocktail_id'),
            'score': score,
            'name': item.get('name'),
            'category': item.get('category'),
            'description': item.get('enhanced_metadata', {}).get('description', '') if isinstance(item.get('enhanced_metadata'), dict) else ''
        })
    
    # Sort by score and return top k
    scored_items.sort(key=lambda x: x['score'], reverse=True)
    return scored_items[:k]


def enrich_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich search results with full metadata from DynamoDB
    """
    from decimal import Decimal
    
    def convert_decimal(obj):
        """Convert Decimal to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_decimal(item) for item in obj]
        return obj
    
    table = dynamodb.Table(METADATA_TABLE)
    
    enriched = []
    for result in results:
        # Get full metadata
        response = table.get_item(Key={'cocktail_id': result['cocktail_id']})
        
        if 'Item' in response:
            item = response['Item']
            enhanced_meta = item.get('enhanced_metadata', {})
            if isinstance(enhanced_meta, dict):
                enhanced_meta = convert_decimal(enhanced_meta)
            
            enriched.append({
                'cocktail_id': result['cocktail_id'],
                'name': item.get('name'),
                'category': item.get('category'),
                'alcoholic': item.get('alcoholic'),
                'glass': item.get('glass'),
                'image_url': item.get('image_url'),
                'description': enhanced_meta.get('description', '') if isinstance(enhanced_meta, dict) else '',
                'flavor_profile': enhanced_meta.get('flavor_profile', []) if isinstance(enhanced_meta, dict) else [],
                'occasions': enhanced_meta.get('occasions', []) if isinstance(enhanced_meta, dict) else [],
                'difficulty': enhanced_meta.get('difficulty', '') if isinstance(enhanced_meta, dict) else '',
                'prep_time_minutes': enhanced_meta.get('prep_time_minutes') if isinstance(enhanced_meta, dict) else None,
                'ingredients': convert_decimal(item.get('ingredients', [])),
                'instructions': item.get('instructions', ''),
                'relevance_score': float(result['score'])
            })
    
    return enriched
