import os
import logging
import json

try:
    from db import get_ddb_connection, Fridge, DB_Response
except:
    # If it gets here it's because we are performing a unit test. It's a common error when using lambda layers
    # Here is an example of someone having a similar issue:
    # https://stackoverflow.com/questions/69592094/pytest-failing-in-aws-sam-project-due-to-modulenotfounderror
    from dependencies.python.db import (
        get_ddb_connection,
        Fridge,
        DB_Response,
    )

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GetLatestFridgeReportHandler:
    def __init__():
        pass

    @staticmethod
    def lambda_handler(event: dict, ddbclient: "botocore.client.DynamoDB") -> dict:
        """
        Extracts the necessary data from events dict, and executes a function corresponding
        to the event httpMethod
        """
        httpMethod = event.get("httpMethod", None)
        db_response = None
        if httpMethod == "GET":
            db_response = Fridge(db_client=ddbclient).get_latest_fridge_reports()
        else:
            db_response = DB_Response(False, 400, "httpMethod missing")
        return db_response.api_format()


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    env = os.environ["Environment"]
    ddbclient = get_ddb_connection(env)
    return GetLatestFridgeReportHandler.lambda_handler(event, ddbclient)
