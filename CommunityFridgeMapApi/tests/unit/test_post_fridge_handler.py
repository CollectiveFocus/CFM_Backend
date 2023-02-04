import unittest

import pytest

from CommunityFridgeMapApi.functions.fridges.v1.app import FridgeHandler
import json


class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass


class PostFridgeHandlerTest(unittest.TestCase):
    def test_lambda_handler_success(self):
        event = {
            "body": '{"name": "greenpointfridge", "location": {"address":"9 W. Elm St.", "geoLat": "40.730610", "geoLng": "-73.935242"}}',
            "httpMethod": "POST",
            "pathParameters": {},
            "queryStringParameters": {},
        }
        response = FridgeHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "fridge_ was succesfully added")
        self.assertEqual(response["statusCode"], 201)

    def test_lambda_handler_fail(self):
        event = {
            "body": '{"name": "greenpointfridge"}',
            "httpMethod": "POST",
            "pathParameters": {},
            "queryStringParameters": {},
        }
        response = FridgeHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "Missing Required Field: location")
        self.assertEqual(response["statusCode"], 400)

    def test_lambda_handler_exception(self):
        event = {
            "body": '{"name": "greenpointfridge", "location": {"address":"9 W. Elm St.", "geoLat": "40.730610", "geoLng": "-73.935242"}}',
            "pathParameters": {},
            "queryStringParameters": {},
        }
        response = FridgeHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        self.assertEqual(response["statusCode"], 400)
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "httpMethod missing")
