import os
import logging
import json

try:
    from db import get_ddb_connection, Fridge
except:
    # If it gets here it's because we are performing a unit test. It's a common error when using lambda layers
    # Here is an example of someone having a similar issue:
    # https://stackoverflow.com/questions/69592094/pytest-failing-in-aws-sam-project-due-to-modulenotfounderror
    from dependencies.python.db import get_ddb_connection, Fridge

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FridgeHandler:
    @staticmethod
    def lambda_handler(event: dict, ddbclient: "botocore.client.DynamoDB") -> dict:
        """
        Extracts the necessary data from events dict, and executes a function corresponding
        to the event httpMethod
        """
        httpMethod = event.get("httpMethod", None)
        pathParameters = event["pathParameters"] or {}
        queryStringParameters = event["queryStringParameters"] or {}
        tag = queryStringParameters.get("tag", None)
        fridgeId = pathParameters.get("fridgeId", None)
        db_response = None
        if httpMethod == "GET":
            if fridgeId:
                db_response = Fridge(db_client=ddbclient).get_item(fridgeId)
            else:
                db_response = Fridge(db_client=ddbclient).get_items(tag=tag)
        elif httpMethod == "POST":
            pass
        else:
            raise ValueError(f'Invalid httpMethod "{httpMethod}"')
        return db_response.api_format()


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    env = os.environ["Environment"]
    ddbclient = get_ddb_connection(env)
    return FridgeHandler.lambda_handler(event, ddbclient)
