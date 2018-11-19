import json
import boto3

DDB_client = boto3.client('dynamodb')
rekognition_client = boto3.client('rekognition')
s3_client = boto3.client('s3')

print('Loading function')


def lambda_handler(event, context):
    #print("Received event: ", event)
    # Get message in SNS
    message = json.loads(event['Records'][0]['Sns']['Message'])
    JobID = message['JobId']
    s3key = message['Video']['S3ObjectName'].replace(
        "video-input", "video-result")+".json"
    bucket = message['Video']['S3Bucket']

    # invoke rekognition to get result
    rekognition_response = rekognition_client.get_face_search(
        JobId=JobID,
        MaxResults=1000,
        SortBy='INDEX'
    )
    #NextToken = response['NextToken']
    #print ("response: ", rekognition_response)

    # write result to s3 and result index in DDB
    s3object = json.dumps(rekognition_response)
    s3_response = s3_client.put_object(
        Body=s3object,
        Bucket=bucket,
        Key=s3key,
        ContentType='application/json',
    )
    #print("s3 response: ", s3_response)

    DDB_response = DDB_client.put_item(
        Item={
            's3key': {'S': s3key},
            'JobStatus': {'S': rekognition_response['JobStatus']},
            'Codec': {'S': rekognition_response['VideoMetadata']['Codec']},
            'DurationMillis': {'S': repr(rekognition_response['VideoMetadata']['DurationMillis'])},
            'Format': {'S': rekognition_response['VideoMetadata']['Format']},
            'FrameRate': {'S': repr(rekognition_response['VideoMetadata']['FrameRate'])},
            'FrameHeight': {'S': repr(rekognition_response['VideoMetadata']['FrameHeight'])},
            'FrameWidth': {'S': repr(rekognition_response['VideoMetadata']['FrameWidth'])},
        },
        TableName='rekognition-demo-video-result',
    )
    #print("ddb response: ", DDB_response)
    #wirte result detail to DDB
    for Persons in rekognition_response['Persons']:
        if 'FaceMatches' in Persons:
            for faceMatch in Persons['FaceMatches']:
                DDB2_response = DDB_client.put_item(
                    Item={
                        'id': {'S': str(Persons['Timestamp'])+faceMatch['Face']['ExternalImageId']},
                        's3key': {'S': s3key},
                        'Timestamp': {'S': str(Persons['Timestamp'])},
                        'Similarity': {'S': str(faceMatch['Similarity'])},
                        'FaceId': {'S': faceMatch['Face']['FaceId']},
                        'Width': {'S': str(faceMatch['Face']['BoundingBox']['Width'])},
                        'Height': {'S': str(faceMatch['Face']['BoundingBox']['Height'])},
                        'Left': {'S': str(faceMatch['Face']['BoundingBox']['Left'])},
                        'Top': {'S': str(faceMatch['Face']['BoundingBox']['Top'])},
                        'ImageId': {'S': faceMatch['Face']['ImageId']},
                        'ExternalImageId': {'S': faceMatch['Face']['ExternalImageId']},
                        'Confidence': {'S': str(faceMatch['Face']['Confidence'])}
                    },
                    TableName='rekognition-demo-video-face-matched',
                )

    return {
        "statusCode": 200,
        "body": "complete"
    }
