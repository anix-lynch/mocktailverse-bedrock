"""
Lambda: Ingest & Extract
Purpose: Fetch cocktail data and use Bedrock Claude to extract/enrich metadata
Trigger: EventBridge schedule or S3 upload
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, List
import requests

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

# Environment variables
RAW_BUCKET = os.environ.get('RAW_BUCKET', 'mocktailverse-raw')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'mocktailverse-metadata')
BEDROCK_MODEL = 'anthropic.claude-3-5-sonnet-20241022-v2:0'


def lambda_handler(event, context):
    """
    Main handler for ingestion pipeline
    """
    try:
        # Determine source
        if 'Records' in event and event['Records'][0]['eventSource'] == 'aws:s3':
            # Triggered by S3 upload
            return process_s3_upload(event)
        else:
            # Scheduled fetch from API
            return fetch_from_api(event)
    
    except Exception as e:
        print(f"Error in ingestion: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def fetch_from_api(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch cocktails from TheCocktailDB API
    """
    fetch_type = event.get('fetch_type', 'mocktails')
    limit = event.get('limit', 10)
    
    cocktails = []
    
    if fetch_type == 'mocktails':
        # Fetch non-alcoholic drinks
        response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Non_Alcoholic')
        drinks = response.json().get('drinks', [])[:limit]
        
        # Get full details for each
        for drink in drinks:
            detail_response = requests.get(
                f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink['idDrink']}"
            )
            cocktails.append(detail_response.json()['drinks'][0])
    
    elif fetch_type == 'random':
        # Fetch random cocktails
        for _ in range(limit):
            response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/random.php')
            cocktails.append(response.json()['drinks'][0])
    
    # Process each cocktail
    results = []
    for cocktail in cocktails:
        result = process_cocktail(cocktail)
        results.append(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Successfully processed {len(results)} cocktails',
            'count': len(results),
            'cocktails': results
        })
    }


def process_s3_upload(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process cocktail data uploaded to S3
    """
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    # Get object from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(response['Body'].read())
    
    # Process cocktails
    results = []
    cocktails = data if isinstance(data, list) else [data]
    
    for cocktail in cocktails:
        result = process_cocktail(cocktail)
        results.append(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Successfully processed {len(results)} cocktails from S3',
            'count': len(results)
        })
    }


def process_cocktail(cocktail: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single cocktail: extract metadata with LLM and store
    """
    # Extract basic info
    cocktail_id = cocktail.get('idDrink')
    name = cocktail.get('strDrink')
    category = cocktail.get('strCategory')
    alcoholic = cocktail.get('strAlcoholic')
    glass = cocktail.get('strGlass')
    instructions = cocktail.get('strInstructions', '')
    
    # Extract ingredients
    ingredients = []
    for i in range(1, 16):
        ingredient = cocktail.get(f'strIngredient{i}')
        measure = cocktail.get(f'strMeasure{i}')
        if ingredient:
            ingredients.append({
                'name': ingredient,
                'measure': measure or ''
            })
    
    # Use Bedrock Claude to extract enhanced metadata
    enhanced_metadata = extract_metadata_with_llm(
        name=name,
        category=category,
        ingredients=ingredients,
        instructions=instructions
    )
    
    # Prepare metadata record
    metadata = {
        'cocktail_id': f'COCKTAIL_{cocktail_id}',
        'name': name,
        'category': category,
        'alcoholic': alcoholic,
        'glass': glass,
        'instructions': instructions,
        'ingredients': ingredients,
        'image_url': cocktail.get('strDrinkThumb'),
        'raw_data': cocktail,
        'enhanced_metadata': enhanced_metadata,
        'ingested_at': datetime.utcnow().isoformat(),
        'data_source': 'thecocktaildb_api'
    }
    
    # Store in DynamoDB
    table = dynamodb.Table(METADATA_TABLE)
    table.put_item(Item=metadata)
    
    # Store raw data in S3
    s3_key = f"cocktails/{cocktail_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=s3_key,
        Body=json.dumps(cocktail),
        ContentType='application/json'
    )
    
    print(f"Processed cocktail: {name} (ID: {cocktail_id})")
    
    return {
        'cocktail_id': cocktail_id,
        'name': name,
        's3_key': s3_key
    }


def extract_metadata_with_llm(
    name: str,
    category: str,
    ingredients: List[Dict],
    instructions: str
) -> Dict[str, Any]:
    """
    Use Bedrock Claude to extract enhanced metadata
    """
    # Build ingredient list for prompt
    ingredient_list = ', '.join([ing['name'] for ing in ingredients])
    
    prompt = f"""Analyze this cocktail and extract enhanced metadata:

Name: {name}
Category: {category}
Ingredients: {ingredient_list}
Instructions: {instructions}

Please provide:
1. A concise description (2-3 sentences)
2. Flavor profile (e.g., sweet, sour, bitter, refreshing)
3. Occasion suggestions (e.g., summer party, brunch, evening cocktail)
4. Difficulty level (easy, medium, hard)
5. Preparation time estimate
6. Key tasting notes

Return as JSON with keys: description, flavor_profile, occasions, difficulty, prep_time_minutes, tasting_notes"""

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Parse JSON from response
        # Claude might wrap it in markdown, so extract JSON
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        metadata = json.loads(content)
        return metadata
    
    except Exception as e:
        print(f"Error extracting metadata with LLM: {str(e)}")
        # Return basic metadata if LLM fails
        return {
            'description': f'A {category.lower()} cocktail',
            'flavor_profile': ['unknown'],
            'occasions': ['any'],
            'difficulty': 'medium',
            'prep_time_minutes': 5,
            'tasting_notes': []
        }
