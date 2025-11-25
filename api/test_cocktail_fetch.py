#!/usr/bin/env python3
"""
Test script to invoke the cocktail fetch Lambda function
"""
import boto3
import json

lambda_client = boto3.client('lambda')

# Test fetching mocktails (non-alcoholic drinks)
payload = {
    'fetch_type': 'mocktails',  # Use 'mocktails' or 'non_alcoholic' for non-alcoholic drinks
    'limit': 5
}

print("Fetching mocktails (non-alcoholic drinks) from TheCocktailDB...")
response = lambda_client.invoke(
    FunctionName='mocktailverse-fetch-cocktails',
    InvocationType='RequestResponse',
    Payload=json.dumps(payload)
)

result = json.loads(response['Payload'].read())
print(json.dumps(result, indent=2))

