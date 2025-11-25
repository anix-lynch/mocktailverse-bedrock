#!/usr/bin/env python3
"""
AWS Lambda Fetch Function - Cocktail Data Collector

🎯 PURPOSE: Fetches mocktail recipes from TheCocktailDB API, transforms and stores in AWS
📊 FEATURES: Multiple fetch types (random, mocktails, popular), API integration, data transformation
🏗️ ARCHITECTURE: Scheduled/Event trigger → Lambda → TheCocktailDB API → DynamoDB + S3
⚡ SCALE: 58+ recipes, free API, zero infrastructure costs
"""

import json
import boto3
import os
import requests
from datetime import datetime
from typing import Dict, Any, List

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
RAW_BUCKET = os.environ.get('RAW_BUCKET', 'mocktailverse-raw')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'mocktailverse-processed')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'mocktailverse-jobs')

# TheCocktailDB API base URL (free, no key needed)
COCKTAIL_API_BASE = "https://www.thecocktaildb.com/api/json/v1/1"

def lambda_handler(event, context):
    """
    Fetch cocktails from TheCocktailDB API and store in S3/DynamoDB
    """
    try:
        # Determine what to fetch from event or default to random cocktails
        fetch_type = event.get('fetch_type', 'random')
        limit = event.get('limit', 10)
        
        cocktails = []
        
        if fetch_type == 'random':
            # Fetch random cocktails
            for _ in range(limit):
                response = requests.get(f"{COCKTAIL_API_BASE}/random.php")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('drinks') and len(data['drinks']) > 0:
                        cocktails.append(data['drinks'][0])
        elif fetch_type == 'mocktails' or fetch_type == 'non_alcoholic':
            # Fetch non-alcoholic drinks (mocktails)
            response = requests.get(f"{COCKTAIL_API_BASE}/filter.php?a=Non_Alcoholic")
            if response.status_code == 200:
                data = response.json()
                drink_list = data.get('drinks', [])[:limit]
                # Get full details for each drink
                for drink in drink_list:
                    detail_response = requests.get(f"{COCKTAIL_API_BASE}/lookup.php?i={drink['idDrink']}")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('drinks') and len(detail_data['drinks']) > 0:
                            cocktails.append(detail_data['drinks'][0])
        elif fetch_type == 'popular':
            # Fetch popular cocktails
            response = requests.get(f"{COCKTAIL_API_BASE}/popular.php")
            if response.status_code == 200:
                data = response.json()
                cocktails = data.get('drinks', [])[:limit]
        elif fetch_type == 'search':
            # Search by name
            search_term = event.get('search_term', 'margarita')
            response = requests.get(f"{COCKTAIL_API_BASE}/search.php?s={search_term}")
            if response.status_code == 200:
                data = response.json()
                cocktails = data.get('drinks', [])[:limit]
        
        if not cocktails:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'No cocktails found',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
        # Transform and store cocktails
        transformed_cocktails = []
        for cocktail in cocktails:
            transformed = transform_cocktail_data(cocktail)
            transformed_cocktails.append(transformed)
            
            # Store in DynamoDB
            try:
                table = dynamodb.Table(DYNAMODB_TABLE)
                table.put_item(Item=transformed)
            except Exception as e:
                print(f"Error saving to DynamoDB: {str(e)}")
        
        # Save batch to S3 processed bucket
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"cocktails/{timestamp}_cocktails.json"
        
        s3.put_object(
            Bucket=PROCESSED_BUCKET,
            Key=s3_key,
            Body=json.dumps(transformed_cocktails, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully fetched and processed {len(transformed_cocktails)} cocktails',
                'count': len(transformed_cocktails),
                's3_key': s3_key,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error processing cocktails: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def transform_cocktail_data(cocktail: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform TheCocktailDB API response to our schema
    """
    # Extract ingredients and measures
    ingredients = []
    measures = []
    for i in range(1, 16):
        ingredient = cocktail.get(f'strIngredient{i}')
        measure = cocktail.get(f'strMeasure{i}')
        if ingredient:
            ingredients.append(ingredient.strip())
            if measure:
                measures.append(measure.strip())
    
    # Create ingredients list with measures
    ingredients_list = []
    for i, ing in enumerate(ingredients):
        if i < len(measures):
            ingredients_list.append(f"{measures[i]} {ing}")
        else:
            ingredients_list.append(ing)
    
    # Generate unique ID from cocktail ID
    cocktail_id = f"COCKTAIL_{cocktail.get('idDrink', 'UNKNOWN')}"
    
    transformed = {
        'job_id': cocktail_id,  # Reusing job_id field for cocktail_id
        'title': cocktail.get('strDrink', 'Unknown Cocktail'),
        'company': 'TheCocktailDB',  # Source
        'location': cocktail.get('strCategory', 'Unknown'),
        'salary_min': None,
        'salary_max': None,
        'salary_currency': 'USD',
        'remote': True,  # All cocktails are "remote" (available anywhere)
        'posted_date': datetime.utcnow().isoformat(),
        'description': cocktail.get('strInstructions', ''),
        'requirements': ingredients_list,  # Using requirements field for ingredients
        'contact_email': 'api@thecocktaildb.com',
        'processed_at': datetime.utcnow().isoformat(),
        'data_source': 'thecocktaildb_api',
        # Additional cocktail-specific fields
        'cocktail_data': {
            'id': cocktail.get('idDrink'),
            'category': cocktail.get('strCategory'),
            'alcoholic': cocktail.get('strAlcoholic'),
            'glass': cocktail.get('strGlass'),
            'image': cocktail.get('strDrinkThumb'),
            'tags': cocktail.get('strTags', '').split(',') if cocktail.get('strTags') else [],
            'iba': cocktail.get('strIBA'),
            'video': cocktail.get('strVideo')
        }
    }
    
    return transformed

# For local testing
if __name__ == "__main__":
    # Test with random cocktails
    test_event = {
        'fetch_type': 'random',
        'limit': 3
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(json.loads(result['body']), indent=2))

