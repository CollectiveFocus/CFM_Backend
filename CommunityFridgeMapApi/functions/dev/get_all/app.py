import os
import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_ddb_connection():
    ENV = os.environ['Environment']
    ddbclient=''
    if ENV == 'local':
        ddbclient = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000/')
    else:
        ddbclient = boto3.client('dynamodb')
    return ddbclient

def lambda_handler(event, context):
    try:
        ddbclient = get_ddb_connection()
        response = ddbclient.scan(TableName=os.environ['FRIDGE_TABLE_NAME'])
        if 'Items' in response:
            data = response['Items']
            logging.info(data)
            return {
                'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
                'headers': { 
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin':'*'
                },
                'body': json.dumps({
                    'message': data,
                }),
            }
        else:
            return {
                'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
                'headers': { 
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin':'*'
                },
                'body': json.dumps({
                    'message': "Table is Empty. No Items",
                }),
            }

    except ddbclient.exceptions.ResourceNotFoundException as e:
        logging.error('Cannot do operations on a non-existent table')
        raise e
    except ClientError as e:
        logging.error('Unexpected error')
        raise e
