import os
import json
import logging
from botocore.exceptions import ClientError
from db import get_ddb_connection
logger = logging.getLogger()
logger.setLevel(logging.INFO)

FRIDGE_DATA = [
                {
                    'PutRequest': {
                        'Item': {
                            'state': {'S': 'NY'},
                            'name': {'S': 'thefriendlyfridge'},
                            'display_name': {'S': 'The Friendly Fridge'},
                            'address': {'S': '1046 Broadway Brooklyn, NY 11221'},
                            'instagram': {'S': 'https://www.instagram.com/thefriendlyfridge/'}
                        }
                    }
                },
                {
                    'PutRequest': {
                        'Item': {
                            'state': {'S': 'NY'},
                            'name': {'S': '2fish5loavesfridge'},
                            'display_name': {'S': '2 Fish 5 Loaves Fridge'},
                            'address': {'S': '63 Whipple St, Brooklyn, NY 11206'},
                            'instagram': {'S': 'https://www.instagram.com/2fish5loavesfridge/'}
                        }
                    }
                },
            ]


FRIDGE_CHECK_IN_DATA = []
FRIDGE_HISTORY_DATA = []

def lambda_handler(event: dict, context: 'awslambdaric.lambda_context.LambdaContext') -> dict:
    ddbclient = get_ddb_connection(env=os.environ['Environment'])
    try:
        response = ddbclient.batch_write_item(
        RequestItems={
            os.environ['FRIDGE_TABLE_NAME']: FRIDGE_DATA}
        )

        return {
            'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps({
                'message': 'Filled DynamoDB',
            }),
        }

    except ddbclient.exceptions.ResourceNotFoundException as e:
        logging.error('Table does not exist')
        raise e
    except ClientError as e:
        logging.error('Unexpected error')
        raise e

