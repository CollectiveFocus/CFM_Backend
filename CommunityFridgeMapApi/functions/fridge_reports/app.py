import os
import logging
import json

try:
    from db import get_ddb_connection, FridgeReport
except:
    # If it gets here it's because we are performing a unit test. It's a common error when using lambda layers
    # Here is an example of someone having a similar issue:
    # https://stackoverflow.com/questions/69592094/pytest-failing-in-aws-sam-project-due-to-modulenotfounderror
    from dependencies.python.db import get_ddb_connection, FridgeReport

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FridgReportHandler:
    def __init__():
        pass

    @staticmethod
    def lambda_handler(event: dict, ddbclient: "botocore.client.DynamoDB") -> dict:
        """
        Extracts the necessary data from events dict, and executes a function corresponding
        to the event httpMethod
        """
        body = json.loads(event["body"])
        httpMethod = event.get("httpMethod", None)
        body["fridgeId"] = event.get("pathParameters", {}).get("fridgeId", None)
        db_response = None
        if httpMethod == "POST":
            db_response = FridgeReport(
                db_client=ddbclient, fridge_report=body
            ).add_item()
        elif httpMethod == "GET":
            pass
        else:
            raise ValueError(f'Invalid httpMethod "{httpMethod}"')
        return db_response.api_format()


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    env = os.environ["Environment"]
    ddbclient = get_ddb_connection(env)
    return FridgReportHandler.lambda_handler(event, ddbclient)
