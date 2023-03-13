import os
import logging
import json

try:
    from db import get_ddb_connection, FridgeReport, Fridge, DB_Response
except:
        # If it gets here it's because we are performing a unit test. It's a common error when using lambda layers
        # goal: return reports in descending order by timestamp
        # - return 10 reports at a time (sort by timestamp)
        # - what does one report look like?

        # get_all_reports
    from dependencies.python.db import (
        get_ddb_connection,
        FridgeReport,
        Fridge,
        DB_Response,
    )

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class FridgeReportsHandler:
    def __init__(self) -> None:
        pass

    @staticmethod
    def lambda_handler(event: dict, ddbclient: "botocore.client.DynamoDB") -> dict:
        """
        Extracts the necessary data from events dict, and executes a function corresponding
        to the event httpMethod
        """
        httpMethod = event.get("httpMethod", None)
        body = event.get("body", None)
        fridge_id = event.get("pathParameters", {}).get("fridgeId", None)
        last_evaluated_key = None
        if json.dumps(event['queryStringParameters']) != 'null':
            ##Todo: Make sure last_evaluated_key is formatted correctly. Currently there are superfluous \\
            last_evaluated_key = json.dumps(event['queryStringParameters']['lastEvaluatedKey']) if 'lastEvaluatedKey' in event['queryStringParameters'] else None
        db_response = None
        if body is not None:
            body = json.loads(body)
            body["fridgeId"] = fridge_id
        if httpMethod == "POST":
            db_response = FridgeReport(
                db_client=ddbclient, fridge_report=body
            ).add_item()
        elif httpMethod == "GET":
            db_response = FridgeReport(db_client=ddbclient).get_all_reports(
                fridgeId=fridge_id,
                lastEvaluatedKey=last_evaluated_key
            )
        else:
            FridgeReport(db_client=ddbclient).warm_lambda()
            db_response = DB_Response(False, 400, "httpMethod missing")
        return db_response.api_format()


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    env = os.environ["Environment"]
    ddbclient = get_ddb_connection(env)
    return FridgeReportsHandler.lambda_handler(event, ddbclient)
