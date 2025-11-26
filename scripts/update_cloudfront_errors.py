import boto3
import json

def update_cloudfront_error_pages():
    client = boto3.client('cloudfront')
    dist_id = 'EC5XY1KCUYTL3'
    
    # Get current config
    dist = client.get_distribution_config(Id=dist_id)
    etag = dist['ETag']
    config = dist['DistributionConfig']
    
    # Define error responses
    error_responses = {
        'Quantity': 2,
        'Items': [
            {
                'ErrorCode': 403,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 10
            },
            {
                'ErrorCode': 404,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 10
            }
        ]
    }
    
    # Update config
    config['CustomErrorResponses'] = error_responses
    
    # Update distribution
    response = client.update_distribution(
        Id=dist_id,
        IfMatch=etag,
        DistributionConfig=config
    )
    print("CloudFront distribution updated successfully!")

if __name__ == '__main__':
    update_cloudfront_error_pages()
