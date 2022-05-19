import os
import logging
from botocore.exceptions import ClientError
import json
try:
    from db import get_ddb_connection
except:
    #For Unit Testing Purposes
    import sys
    sys.path.append(os.getcwdb().decode() + '/dependencies/python')
    from db import get_ddb_connection


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: dict, context: 'awslambdaric.lambda_context.LambdaContext') -> dict:
    try:
        ddbclient = get_ddb_connection(env=os.environ['Environment'])
        db_response = ddbclient.scan(TableName=os.environ['FRIDGE_TABLE_NAME'])
        return format_api_response(db_response=db_response, response_type='Items')

    except ddbclient.exceptions.ResourceNotFoundException as e:
        logging.error('Cannot do operations on a non-existent table')
        raise e
    except ClientError as e:
        logging.error('Unexpected error')
        raise e

def format_api_response(db_response: dict, response_type: str) -> dict:
    if response_type in db_response:
        data = db_response[response_type]
        logging.info(data)
        return {
            'statusCode': db_response['ResponseMetadata']['HTTPStatusCode'],
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
            'statusCode': db_response['ResponseMetadata']['HTTPStatusCode'],
            'headers': { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin':'*'
            },
            'body': json.dumps({
                'message': "Item(s) not found",
            }),
        }
