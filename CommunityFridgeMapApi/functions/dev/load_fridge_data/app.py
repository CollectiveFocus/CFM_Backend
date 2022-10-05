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
    ddbclient = get_ddb_connection()
    try:
        response = ddbclient.batch_write_item(
        RequestItems={
            os.environ['FRIDGE_TABLE_NAME']: [
                {
                    'PutRequest': {
                        'Item': {
                            'state': {'S': 'NY'},
                            'fridge_name': {'S': 'The Friendly Fridge'},
                            'address': {'S': '1046 Broadway Brooklyn, NY 11221'},
                            'instagram': {'S': 'https://www.instagram.com/thefriendlyfridge/'}
                        }
                    }
                },
                {
                    'PutRequest': {
                        'Item': {
                            'state': {'S': 'NY'},
                            'fridge_name': {'S': '2 Fish 5 Loaves Fridge'},
                            'address': {'S': '63 Whipple St, Brooklyn, NY 11206'},
                            'instagram': {'S': 'https://www.instagram.com/2fish5loavesfridge/'}
                        }
                    }
                },
            ]}
        )

        return {
            'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps({
                'message': 'Filled DynamoDB',
            }),
        }

    except ddbclient.exceptions.ResourceNotFoundException as e:
        logging.error('Cannot do operations on a non-existent table')
        raise e
    except ClientError as e:
        logging.error('Unexpected error')
        raise e
