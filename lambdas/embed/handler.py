"""
Lambda: Chunk & Embed
Purpose: Generate vector embeddings using Bedrock Titan
Trigger: Step Functions workflow after ingestion
"""

import json
import boto3
import os
from typing import Dict, Any, List
import hashlib

# AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
s3 = boto3.client('s3')

# Environment variables
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')
EMBEDDINGS_BUCKET = os.environ.get('EMBEDDINGS_BUCKET', 'mocktailverse-embeddings')
BEDROCK_EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'


def lambda_handler(event, context):
    """
    Generate embeddings for cocktails
    """
    try:
        # Get cocktail IDs to process
        cocktail_ids = event.get('cocktail_ids', [])
        
        if not cocktail_ids:
            # Process all cocktails without embeddings
            cocktail_ids = get_unembedded_cocktails()
        
        results = []
        for cocktail_id in cocktail_ids:
            result = process_cocktail_embedding(cocktail_id)
            results.append(result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Generated embeddings for {len(results)} cocktails',
                'count': len(results),
                'results': results
            })
        }
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_unembedded_cocktails() -> List[str]:
    """
    Get cocktails that don't have embeddings yet
    """
    table = dynamodb.Table(METADATA_TABLE)
    
    # Scan for items without embedding_id
    response = table.scan(
        FilterExpression='attribute_not_exists(embedding_id)'
    )
    
    return [item['cocktail_id'] for item in response.get('Items', [])]


def process_cocktail_embedding(cocktail_id: str) -> Dict[str, Any]:
    """
    Generate and store embedding for a cocktail
    """
    # Get cocktail metadata
    table = dynamodb.Table(METADATA_TABLE)
    response = table.get_item(Key={'cocktail_id': cocktail_id})
    
    if 'Item' not in response:
        raise ValueError(f"Cocktail {cocktail_id} not found")
    
    cocktail = response['Item']
    
    # Create text chunks for embedding
    chunks = create_text_chunks(cocktail)
    
    # Generate embeddings for each chunk
    embeddings = []
    for chunk in chunks:
        embedding = generate_embedding(chunk['text'])
        embeddings.append({
            'chunk_id': chunk['id'],
            'chunk_type': chunk['type'],
            'text': chunk['text'],
            'embedding': embedding,
            'dimension': len(embedding)
        })
    
    # Check for duplicates using cosine similarity
    is_duplicate, similar_to = check_duplicate(embeddings[0]['embedding'])
    
    # Store embeddings
    embedding_id = f"EMB_{cocktail_id}_{hashlib.md5(cocktail['name'].encode()).hexdigest()[:8]}"
    
    embedding_data = {
        'embedding_id': embedding_id,
        'cocktail_id': cocktail_id,
        'cocktail_name': cocktail['name'],
        'chunks': embeddings,
        'is_duplicate': is_duplicate,
        'similar_to': similar_to,
        'created_at': cocktail.get('ingested_at')
    }
    
    # Save to S3
    s3.put_object(
        Bucket=EMBEDDINGS_BUCKET,
        Key=f"embeddings/{embedding_id}.json",
        Body=json.dumps(embedding_data),
        ContentType='application/json'
    )
    
    # Update metadata table with embedding reference
    table.update_item(
        Key={'cocktail_id': cocktail_id},
        UpdateExpression='SET embedding_id = :eid, has_embedding = :he',
        ExpressionAttributeValues={
            ':eid': embedding_id,
            ':he': True
        }
    )
    
    print(f"Generated embedding for {cocktail['name']} (ID: {embedding_id})")
    
    return {
        'cocktail_id': cocktail_id,
        'embedding_id': embedding_id,
        'chunks_count': len(embeddings),
        'is_duplicate': is_duplicate
    }


def create_text_chunks(cocktail: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Create text chunks from cocktail data for embedding
    """
    chunks = []
    
    # Chunk 1: Name + Description
    description = cocktail.get('enhanced_metadata', {}).get('description', '')
    chunks.append({
        'id': 'name_desc',
        'type': 'primary',
        'text': f"{cocktail['name']}. {description}"
    })
    
    # Chunk 2: Ingredients + Instructions
    ingredients = cocktail.get('ingredients', [])
    ingredient_text = ', '.join([f"{ing.get('measure', '')} {ing['name']}".strip() for ing in ingredients])
    instructions = cocktail.get('instructions', '')
    
    chunks.append({
        'id': 'recipe',
        'type': 'recipe',
        'text': f"Ingredients: {ingredient_text}. Instructions: {instructions}"
    })
    
    # Chunk 3: Flavor profile + Occasions
    metadata = cocktail.get('enhanced_metadata', {})
    flavor_profile = ', '.join(metadata.get('flavor_profile', []))
    occasions = ', '.join(metadata.get('occasions', []))
    tasting_notes = ', '.join(metadata.get('tasting_notes', []))
    
    chunks.append({
        'id': 'flavor',
        'type': 'metadata',
        'text': f"Flavor: {flavor_profile}. Best for: {occasions}. Tasting notes: {tasting_notes}"
    })
    
    return chunks


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding using Bedrock Titan
    """
    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL,
            body=json.dumps({
                "inputText": text
            })
        )
        
        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']
        
        return embedding
    
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise


def check_duplicate(embedding: List[float], threshold: float = 0.95) -> tuple:
    """
    Check if this embedding is a duplicate using cosine similarity
    """
    try:
        # Get all existing embeddings from S3
        response = s3.list_objects_v2(
            Bucket=EMBEDDINGS_BUCKET,
            Prefix='embeddings/'
        )
        
        if 'Contents' not in response:
            return False, None
        
        # Check similarity with existing embeddings
        for obj in response['Contents'][:100]:  # Limit to 100 for performance
            existing_data = s3.get_object(Bucket=EMBEDDINGS_BUCKET, Key=obj['Key'])
            existing_embedding_data = json.loads(existing_data['Body'].read())
            
            # Compare with primary chunk
            existing_embedding = existing_embedding_data['chunks'][0]['embedding']
            similarity = cosine_similarity(embedding, existing_embedding)
            
            if similarity > threshold:
                return True, existing_embedding_data['cocktail_id']
        
        return False, None
    
    except Exception as e:
        print(f"Error checking duplicates: {str(e)}")
        return False, None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    """
    import math
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)
