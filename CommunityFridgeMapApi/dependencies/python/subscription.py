import boto3
import os
import logging
import json
from dataclasses import dataclass


from db import DB_Response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_ddb_connection(
    env: str = os.getenv("Environment", "")
) -> "boto3.resource":
    """Returns a connection to the DynamoDB table"""
    if env == "local":
        return boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:4566",
        )
    else:
        return boto3.resource("dynamodb")



@dataclass
class Field_Validator:
    is_valid: str
    message: str

class Subscription():
    FIELD_VALIDATION = {
        "fridgeId": {"required": True, "type": "S"},
        "statusType": {"required": True, "type": "S"},
        "notificationLimit": {"required": True, "type": "N"},
        "listOfUsers": {"required": True, "type": "L"},
        "users/$/userId": {"required": True, "type": "S"},
        "users/$/phone": {"required": True, "type": "S"},
        "users/$/email": {"required": True, "type": "S"},
        "users/$/lastNotified": {"required": True, "type": "N"},
    }

    TABLE_NAME = f"subscription_dev"

    def __init__(self, db_client: "boto3.resource('dynamodb')", subscription: dict = None):
        self.table = db_client.Table(self.TABLE_NAME)
        if subscription is not None:
            self.fridgeId = subscription.get("fridgeId", None)
            self.statusType = subscription.get("statusType", None)
            self.notificationLimit = subscription.get(
                "notificationLimit", None)
            self.listOfUsers = subscription.get("listOfUsers", None)

    
    def add_item(self) -> DB_Response:
        """
        adds item to database
            Parameters:
                conditional_expression (str): conditional expression for boto3 function put_item

            Returns:
                db_response (DB_Response): returns a DB_Response
        """
        item = {
            "fridgeId": self.fridgeId,
            "statusType": self.statusType,
            "notificationLimit": self.notificationLimit,
            "listOfUsers": self.listOfUsers}

        return self.table.put_item(Item=item)