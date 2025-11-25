"""
Lambda: RAG Retrieval
Purpose: Retrieval-Augmented Generation using Bedrock Claude
Trigger: API Gateway /v1/rag endpoint
"""

import json
import boto3
import os
from typing import Dict, Any, List

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
lambda_client = boto3.client('lambda')

# Environment variables
SEARCH_LAMBDA = os.environ.get('SEARCH_LAMBDA', 'mocktailverse-search')
BEDROCK_MODEL = 'anthropic.claude-3-5-sonnet-20241022-v2:0'


def lambda_handler(event, context):
    """
    Handle RAG requests
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        question = body.get('question', '')
        k = body.get('k', 3)  # Number of context documents
        
        if not question:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Question parameter is required'})
            }
        
        # Step 1: Retrieve relevant cocktails
        context_docs = retrieve_context(question, k=k)
        
        # Step 2: Build context string
        context = build_context(context_docs)
        
        # Step 3: Generate answer with Claude
        answer = generate_answer(question, context)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'question': question,
                'answer': answer,
                'sources': [
                    {
                        'name': doc['name'],
                        'relevance_score': doc['relevance_score']
                    }
                    for doc in context_docs
                ],
                'context_count': len(context_docs)
            })
        }
    
    except Exception as e:
        print(f"Error in RAG: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def retrieve_context(question: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve relevant cocktails using search Lambda
    """
    # Call search Lambda
    response = lambda_client.invoke(
        FunctionName=SEARCH_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'body': json.dumps({
                'query': question,
                'k': k
            })
        })
    )
    
    result = json.loads(response['Payload'].read())
    body = json.loads(result['body'])
    
    return body.get('results', [])


def build_context(docs: List[Dict[str, Any]]) -> str:
    """
    Build context string from retrieved documents
    """
    context_parts = []
    
    for i, doc in enumerate(docs, 1):
        # Format each cocktail as a context block
        ingredients_text = ', '.join([
            f"{ing.get('measure', '')} {ing['name']}".strip()
            for ing in doc.get('ingredients', [])
        ])
        
        context_block = f"""
Cocktail {i}: {doc['name']}
Category: {doc.get('category', 'Unknown')}
Type: {doc.get('alcoholic', 'Unknown')}
Description: {doc.get('description', 'No description available')}
Ingredients: {ingredients_text}
Instructions: {doc.get('instructions', 'No instructions available')}
Flavor Profile: {', '.join(doc.get('flavor_profile', []))}
Best for: {', '.join(doc.get('occasions', []))}
Difficulty: {doc.get('difficulty', 'Unknown')}
Preparation Time: {doc.get('prep_time_minutes', 'Unknown')} minutes
"""
        context_parts.append(context_block.strip())
    
    return '\n\n---\n\n'.join(context_parts)


def generate_answer(question: str, context: str) -> str:
    """
    Generate answer using Bedrock Claude with RAG
    """
    prompt = f"""You are an expert bartender and mixologist. Answer the user's question based ONLY on the provided cocktail information. If the information doesn't contain the answer, say so.

Context (Cocktail Database):
{context}

User Question: {question}

Instructions:
- Provide a helpful, accurate answer based on the context above
- If recommending cocktails, explain why they match the request
- Include specific details like ingredients, flavors, and preparation tips
- If the context doesn't have relevant information, politely say you don't have that information
- Be conversational but professional
- Keep your answer concise (2-3 paragraphs max)

Answer:"""

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        return answer
    
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        raise
