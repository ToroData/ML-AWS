"""
Some references that you should consult.
https://docs.python.org/3/library/logging.html
https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-lambda.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_labels
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
Please be aware that this tutorial has been generated based on Amazon's official documentation. 
You can find more examples similar to this in the same official documentation.
https://docs.aws.amazon.com/code-samples/latest/catalog/code-catalog-python-example_code-rekognition.html
"""

import json
import logging
from logging import Logger
from typing import Dict, Union, List, Any

import boto3

logger: Logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Parameters
LABEL: str = 'dog'

# Boto3 S3 Client to connect to S3
s3_client: object = boto3.client('s3')


def lambda_handler(event, context):
    """
    Function to get attributes from S3 and process the rekognition API

    Args:
        event (object): capture event
    """
    logger.info(event)
    bucket: object = event['Records'][0]['s3']['bucket']['name']
    image: object = event['Records'][0]['s3']['object']['key']
    output_key: str = 'output/rekognition_response.json'
    response: dict = {'Status': 'Not Found', 'body': []}

    # Rekognition connection
    rekognition_client: object = boto3.client('rekognition')
    # Use try except to capture an error
    try:
        response_rekognition: object = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image
                }
            },
            MinConfidence=65  # Choose your minimum confidence  
        )

        detected_labels: list = []  # Declaring empty label lists.

        if response_rekognition['Labels']:
            for label in response_rekognition['Labels']:
                detected_labels.append(label['Name'].lower())
            print(detected_labels)

            if LABEL in detected_labels:
                # The structure of the JSON would be like this
                # {
                #     "Status": "Success! dog found",
                #     "body": [
                #         [
                #             {
                #                 "Name": "Animal",
                #                 "Confidence": 99.9502182006836,
                #                 "Instances": [],
                #                 "Parents": []
                #             }
                #         ]
                # }
                # Change the status message to make it more suitable for your app
                response['Status'] = f"Success! {LABEL} found"
                response['body'].append(response_rekognition['Labels'])
            else:
                response['Status'] = f"Failed! {LABEL} Not found"
                response['body'].append(response_rekognition['Labels'])

    except Exception as error:
        print(error)

    # Put the json response to the ouput bucket
    s3_client.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(response, indent=4)
    )

    return response


'''
According to the official documentation, 
you could use this code to test the function. 
Keep in mind to put an image in the desired folder.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<bucket-name>"
                    },
                    "object": {
                    "key": "input/<change for your image>.<png>"
                    }
                }
                }
            ]
}
'''
