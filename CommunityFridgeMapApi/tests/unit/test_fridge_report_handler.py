import unittest

import pytest

from CommunityFridgeMapApi.functions.fridge_reports.app import FridgReportHandler
import json


class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass


class FrdgeReportHandlerTest(unittest.TestCase):
    def test_lambda_handler_success(self):
        event = {
            "body": '{"status": "working", "fridge_percentage": 33}',
            "pathParameters": {"fridge_id": "thefriendlyfridge"},
            "httpMethod": "POST",
        }
        response = FridgReportHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        self.assertEqual(response["statusCode"], 201)
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "Fridge Report was succesfully added")

    def test_lambda_handler_fail(self):
        event = {
            "body": '{"status": "working"}',
            "pathParameters": {"fridge_id": "thefriendlyfridge"},
            "httpMethod": "POST",
        }
        response = FridgReportHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        self.assertEqual(response["statusCode"], 400)
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "Missing Required Field: fridge_percentage")

    def test_lambda_handler_exception(self):
        event = {
            "body": '{"status": "working", "fridge_percentage": 33}',
            "pathParameters": {"fridge_id": "thefriendlyfridge"},
        }
        with pytest.raises(ValueError):
            FridgReportHandler.lambda_handler(
                event=event, ddbclient=DynamoDbMockPutItem()
            )

    def test_get_fridge_id(self):
        self.assertEqual(FridgReportHandler.get_fridge_id({}), None)
        self.assertEqual(
            FridgReportHandler.get_fridge_id({"pathParameters": {"fridge_id": "hi"}}),
            "hi",
        )
