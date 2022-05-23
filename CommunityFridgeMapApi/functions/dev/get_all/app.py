import os
import logging
from botocore.exceptions import ClientError
import json
import sys
try:
    from db import get_ddb_connection
except:
    #If it gets here it's because we are performing a unit test. Here is an example of someone having a similar issue
    #https://stackoverflow.com/questions/69592094/pytest-failing-in-aws-sam-project-due-to-modulenotfounderror
    from dependencies.python.db import get_ddb_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GetAllFridgesHandler:

    def __init__(self, env: str, table_name: str, ddbclient: 'botocore.client.DynamoDB'):
        self.ddbclient = ddbclient
        self.env = env
        self.table_name = table_name

    
    def lambda_handler(self, event: dict, context: 'awslambdaric.lambda_context.LambdaContext') -> dict:
        try:
            db_response = self.ddbclient.scan(TableName=self.table_name)
            return self.format_api_response(db_response=db_response, response_type='Items')

        except self.ddbclient.exceptions.ResourceNotFoundException as e:
            logging.error('Cannot do operations on a non-existent table')
            raise e
        except ClientError as e:
            logging.error('Unexpected error')
            raise e

    def format_api_response(self, db_response: dict, response_type: str) -> dict:
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

def lambda_handler(event: dict, context: 'awslambdaric.lambda_context.LambdaContext') -> dict:
    env = os.environ['Environment']
    ddbclient = get_ddb_connection(env)
    handler = GetAllFridgesHandler(
        env=env,
        table_name=os.environ['FRIDGE_TABLE_NAME'],
        ddbclient=ddbclient
    )
    return handler.lambda_handler(event, context)
