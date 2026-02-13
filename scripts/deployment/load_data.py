#!/usr/bin/env python3
"""
Load sample cocktail data to DynamoDB
"""
import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('mocktailverse-metadata')

def load_sample_data():
    """Load sample cocktails from margarita_recipes.json"""
    
    cocktails = []
    with open('margarita_recipes.json', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                cocktails.append(json.loads(line))
    
    print(f"📊 Loading {len(cocktails)} cocktails to DynamoDB...")
    
    for idx, cocktail in enumerate(cocktails):
        cocktail_id = cocktail.get('idDrink', f'COCKTAIL_{idx}')
        name = cocktail.get('strDrink', f'Cocktail {idx}')
        
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
        
        # Create enhanced metadata
        enhanced_metadata = {
            'description': f"A delicious {name.lower()} perfect for any occasion",
            'flavor_profile': ['refreshing', 'citrusy', 'smooth'],
            'occasions': ['party', 'dinner', 'relaxation'],
            'difficulty': 'Easy',
            'prep_time_minutes': 5
        }
        
        # Prepare item
        item = {
            'cocktail_id': f'COCKTAIL_{cocktail_id}',
            'name': name,
            'category': cocktail.get('strCategory', 'Cocktail'),
            'alcoholic': cocktail.get('strAlcoholic', 'Alcoholic'),
            'glass': cocktail.get('strGlass', 'Cocktail glass'),
            'instructions': cocktail.get('strInstructions', ''),
            'ingredients': ingredients,
            'image_url': cocktail.get('strDrinkThumb'),
            'enhanced_metadata': enhanced_metadata,
            'ingested_at': datetime.utcnow().isoformat(),
            'data_source': 'sample_data'
        }
        
        try:
            table.put_item(Item=item)
            print(f"✅ Loaded: {name}")
        except Exception as e:
            print(f"❌ Failed to load {name}: {e}")
    
    print(f"\n🎉 Loaded {len(cocktails)} cocktails successfully!")

if __name__ == "__main__":
    load_sample_data()



