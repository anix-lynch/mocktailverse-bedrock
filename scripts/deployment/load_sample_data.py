#!/usr/bin/env python3
"""
Load sample cocktail data to DynamoDB for demo purposes
"""
import boto3
import json
import os

def load_sample_data():
    # Load AWS credentials from environment
    dynamodb = boto3.client(
        'dynamodb',
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-west-2'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    
    # Load sample data (NDJSON format - one JSON object per line)
    cocktails = []
    with open('margarita_recipes.json', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                cocktails.append(json.loads(line))
    
    print(f"📊 Loading {len(cocktails)} cocktails to DynamoDB...")
    
    # Add sample enrichment fields and load
    for idx, cocktail in enumerate(cocktails):
        drink_name = cocktail.get('strDrink', f'Cocktail {idx}')
        
        item = {
            'id': {'S': cocktail.get('idDrink', f'cocktail_{idx}')},
            'name': {'S': drink_name},
            'category': {'S': cocktail.get('strCategory', 'Cocktail')},
            'spirit_type': {'S': 'tequila' if 'margarita' in drink_name.lower() else 'rum'},
            'complexity_score': {'N': str(5.0 + (idx % 5))},
            'estimated_calories': {'N': str(150 + (idx * 20))},
            'is_alcoholic': {'BOOL': cocktail.get('strAlcoholic', 'Alcoholic') == 'Alcoholic'}
        }
        
        try:
            dynamodb.put_item(TableName='mocktailverse-cocktails', Item=item)
            print(f"✅ Loaded: {drink_name}")
        except Exception as e:
            print(f"❌ Failed to load {drink_name}: {e}")
    
    print("\n🎉 Sample data loaded successfully!")

if __name__ == "__main__":
    load_sample_data()
