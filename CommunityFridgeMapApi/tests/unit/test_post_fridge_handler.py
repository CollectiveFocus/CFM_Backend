#how to test post request
# Here are some tips for testing POST requests:
#
# Create a resource with a POST request and ensure a 200 status code is returned.
# Next, make a GET request for that resource, and ensure the data was saved correctly.
# Add tests that ensure POST requests fail with incorrect or ill-formatted data.


#Good example of error code and status handling
# {
#   "code": 21211,
#   "message": "The 'To' number 5551234567 is not a valid phone number.",
#   "more_info": "https://www.twilio.com/docs/errors/21211",
#   "status": 400
# }

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
            "httpMethod": "POST"
        }
        response = FridgeHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "fridge was succesfully added")
        self.assertEqual(response["statusCode"], 201)

    def test_lambda_handler_fail(self):
        event = {
            "body": '{"name": "greenpointfridge"}',
            "httpMethod": "POST"
        }
        response = FridgeHandler.lambda_handler(
            event=event, ddbclient=DynamoDbMockPutItem()
        )
        message = json.loads(response["body"])["message"]
        self.assertEqual(message, "Missing Required Field: location")
        self.assertEqual(response["statusCode"], 400)

    def test_lambda_handler_exception(self):
        event = {
            "body": '{"name": "greenpointfridge", "location": {"address":"9 W. Elm St.", "geoLat": "40.730610", "geoLng": "-73.935242"}}'
        }
        with pytest.raises(ValueError):
            FridgeHandler.lambda_handler(
                event=event, ddbclient=DynamoDbMockPutItem()
            )
