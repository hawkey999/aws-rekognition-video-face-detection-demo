import json
import boto3

rekognition_client = boto3.client('rekognition')

print('Loading function')

def lambda_handler(event, context):
    #print("Received event: ", event)
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    JobTag = event['Records'][0]['s3']['object']['eTag']
    ClientRequestToken = event['Records'][0]['s3']['object']['sequencer']
    
    # Call rekognition to analyze video start_face_search
    response = rekognition_client.start_face_search(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        ClientRequestToken=ClientRequestToken,
        FaceMatchThreshold=75,
        CollectionId='video-face-search',
        NotificationChannel={
            'SNSTopicArn': 'arn:aws:sns:us-west-2:968464439421:rekognition-demo-video-face-search',
            'RoleArn': 'arn:aws:iam::968464439421:role/Rekognition_service_role'
        },
        #FaceAttributes='ALL', #只有face_detection才有这参数
        JobTag=JobTag
    )
    print("response: ",response)
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
