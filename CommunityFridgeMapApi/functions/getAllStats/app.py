import os
import logging
import json

try:
    from db import get_fridge_stats
except:
    from dependencies.python.db import get_fridge_stats

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FridgeStatsHandler:
    @staticmethod
    def lambda_handler(event: dict) -> dict:
        """
        Handles GET request to fetch fridge statistics.
        """
        httpMethod = event.get("httpMethod", None)
        if httpMethod == "GET":
            result = get_fridge_stats()
            return {
                "statusCode": result.status_code,
                "body": json.dumps({
                    "message": result.message,
                    "stats": json.loads(result.json_data)
                }),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"message": "Method Not Allowed"}),
                "headers": {
                    "Content-Type": "application/json"
                }
            }


def lambda_handler(event: dict, context: "awslambdaric.lambda_context.LambdaContext") -> dict:
    return FridgeStatsHandler.lambda_handler(event)
