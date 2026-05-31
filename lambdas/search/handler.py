"""
Lambda: Vector Search
Purpose: Semantic search. Default path = real cosine similarity over Titan v2
         embeddings stored in S3 (cheap, no OpenSearch). OpenSearch Serverless KNN
         is an optional v2 path, used only if OPENSEARCH_ENDPOINT is configured.
Trigger: API Gateway /v1/search endpoint
"""

import json
import math
import boto3
import os
from typing import Dict, Any, List

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'cocktails')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')
EMBEDDINGS_BUCKET = os.environ.get('EMBEDDINGS_BUCKET', 'mocktailverse-embeddings')
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
        # Default path: real cosine similarity over S3-stored Titan v2 embeddings.
        return dynamodb_vector_search(query_embedding, k)
    
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


def dynamodb_vector_search(query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
    """
    Real semantic search without OpenSearch: scan embedded items in DynamoDB, load
    each item's stored Titan v2 embedding from S3, rank by cosine similarity to the
    query, return the true top-k. No mock scores.
    """
    table = dynamodb.Table(METADATA_TABLE)
    items = table.scan(FilterExpression='attribute_exists(embedding_id)').get('Items', [])

    scored_items = []
    for item in items:
        item_embedding = load_primary_embedding(item.get('embedding_id'))
        if not item_embedding:
            continue  # skip items whose embedding can't be loaded — never fake a score
        score = cosine_similarity(query_embedding, item_embedding)
        scored_items.append({
            'cocktail_id': item.get('cocktail_id'),
            'score': score,
            'name': item.get('name'),
            'category': item.get('category'),
            'description': item.get('enhanced_metadata', {}).get('description', '') if isinstance(item.get('enhanced_metadata'), dict) else ''
        })

    scored_items.sort(key=lambda x: x['score'], reverse=True)
    return scored_items[:k]


def load_primary_embedding(embedding_id: str) -> List[float]:
    """
    Load the primary-chunk embedding for an item from S3 (embeddings/<id>.json).
    Returns None if missing/unreadable so the caller can skip it cleanly.
    """
    if not embedding_id:
        return None
    try:
        obj = s3.get_object(Bucket=EMBEDDINGS_BUCKET, Key=f"embeddings/{embedding_id}.json")
        data = json.loads(obj['Body'].read())
        return data['chunks'][0]['embedding']
    except Exception as e:
        print(f"Could not load embedding {embedding_id}: {e}")
        return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Cosine similarity between two equal-length vectors (pure stdlib, no numpy)."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


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
