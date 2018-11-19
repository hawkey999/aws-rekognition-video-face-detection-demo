import json
import boto3

DDB_client = boto3.client('dynamodb')
rekognition_client = boto3.client('rekognition')

print('Loading function')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Get user_id from DDB as ExternalImageId to rekognition
    response = DDB_client.get_item(
        Key={'s3key': {'S': key}},
        TableName='rekognition-demo-user-img-index',
    )
    user_id = response['Item']['user_id']['S']

    # call rekognition to index image 
    rekognition_response = rekognition_client.index_faces(
        CollectionId='video-face-search',
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        ExternalImageId=user_id,
        DetectionAttributes=['ALL']
    )
    
    print("response from rekognition: ", rekognition_response)
    
    # write response into DDB
    FaceId = rekognition_response['FaceRecords'][0]['Face']['FaceId']
    ImageId = rekognition_response['FaceRecords'][0]['Face']['ImageId']
    DDB_response = DDB_client.put_item(
            Item={
            's3key': {
                'S': key,
            },
            'user_id': {
                'S': user_id,
            },
            'FaceId': {
                'S': FaceId,
            },
            'ImageId': {
                'S': ImageId,
            }
        },
        ReturnConsumedCapacity='TOTAL',
        TableName='rekognition-demo-user-img-index',
        )
    
    return {
        "statusCode": 200,
        "body": json.dumps('upload image index complete')
    }
