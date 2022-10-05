import os
import json
import logging
from botocore.exceptions import ClientError
from db import get_ddb_connection
from db import Fridge

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FRIDGE_DATA = [
    {
        "name": "The Friendly Fridge",
        "location": {
            "geoLat": 124242,
            "geoLng": 2345235,
            "street": "1046 Broadway",
            "zip": "11221",
            "state": "NY",
            "city": "Brooklyn",
        },
        "maintainer": {"instagram": "https://www.instagram.com/thefriendlyfridge/"},
    },
    {
        "name": "2 Fish 5 Loaves Fridge",
        "location": {
            "geoLat": 40.701730,
            "geoLng": -73.944530,
            "street": "63 Whipple St",
            "zip": "11206",
            "state": "NY",
            "city": "Brooklyn",
        },
        "maintainer": {"instagram": "https://www.instagram.com/2fish5loavesfridge/"},
    },
]


FRIDGE_REPORT_DATA = []
FRIDGE_HISTORY_DATA = []


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    db_client = get_ddb_connection(env=os.environ["Environment"])
    try:
        responses = []
        response = None
        for fridge in FRIDGE_DATA:
            response = Fridge(fridge=fridge, db_client=db_client).add_item()
            responses.append(response.get_dict_form())
            if response.status_code != 201:
                break

        return {
            "statusCode": response.status_code,
            "isBase64Encoded": "false",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "responses": responses,
                }
            ),
        }

    except db_client.exceptions.ResourceNotFoundException as e:
        logging.error("Table does not exist")
        raise e
    except ClientError as e:
        logging.error("Unexpected error")
        raise e
