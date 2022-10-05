import unittest

import pytest

from CommunityFridgeMapApi.functions.fridge_reports.app import FridgReportHandler
import json


class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass

    def get_item(self, TableName=None, Key=None):
        return {"Item": {"json_data": {"S": '{"id": {"S": "test"}}'}}}

    def update_item(
        self,
        TableName=None,
        Key=None,
        ExpressionAttributeNames=None,
        ExpressionAttributeValues=None,
        UpdateExpression=None,
    ):
        pass


class FrdgeReportHandlerTest(unittest.TestCase):
    def test_lambda_handler_success(self):
        event = {
            "body": '{"condition": "working", "foodPercentage": 33}',
            "pathParameters": {"fridgeId": "thefriendlyfridge"},
            "httpMethod": "POST",
        }
        response = FridgReportHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        self.assertEqual(response["statusCode"], 201)
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "fridge_report was succesfully added")

    def test_lambda_handler_fail(self):
        event = {
            "body": '{"condition": "working"}',
            "pathParameters": {"fridgeId": "thefriendlyfridge"},
            "httpMethod": "POST",
        }
        response = FridgReportHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        self.assertEqual(response["statusCode"], 400)
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "Missing Required Field: foodPercentage")

    def test_lambda_handler_exception(self):
        event = {
            "body": '{"condition": "working", "foodPercentage": 33}',
            "pathParameters": {"fridgeId": "thefriendlyfridge"},
        }
        with pytest.raises(ValueError):
            FridgReportHandler.lambda_handler(
                event=event, ddbclient=DynamoDbMockPutItem()
            )
