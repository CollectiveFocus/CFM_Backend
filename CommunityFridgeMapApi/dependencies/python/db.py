import os
import string
import boto3

def get_ddb_connection(env:str=os.getenv('Environment', '')) -> 'botocore.client.DynamoDB':
    ddbclient=''
    if env == 'local':
        ddbclient = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000/')
    else:
        ddbclient = boto3.client('dynamodb')
    return ddbclient

def layer_test() -> str:
    return "layer test"