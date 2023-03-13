from CommunityFridgeMapApi.functions.fridges.v1.app import FridgeHandler
from dependencies.python.db import layer_test
from dependencies.python.db import get_ddb_connection
import unittest


class DynamoDbMockGetItem:
    def __init__(self):
        pass

    def get_item(self, TableName=None, Key=None):
        return {"Item": {"json_data": {"S": '{"id": {"S": "test"}}'}}}
    
class DynamoDbMockGetItemFail:
    def __init__(self):
        pass

    def get_item(self, TableName=None, Key=None):
        return {} 


class DynamoDbMockScan:
    def __init__(self):
        pass

    def scan(
        self,
        TableName=None,
        FilterExpression=None,
        ExpressionAttributeValues=None,
        ProjectionExpression=None,
    ):
        return {"Items": [{"json_data": {"S": '{"id": {"S": "test"}}'}}]}


class FridgeHandlerTest(unittest.TestCase):
    def test_get_item_success(self):
        json_data = '{"id": {"S": "test"}}'
        response = FridgeHandler.lambda_handler(
            event={
                "httpMethod": "GET",
                "pathParameters": {"fridgeId": "test"},
                "queryStringParameters": None,
            },
            ddbclient=DynamoDbMockGetItem(),
        )
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], json_data)

    def test_get_item_failure(self):
        response = FridgeHandler.lambda_handler(
            event={
                "httpMethod": "GET",
                "pathParameters": {"fridgeId": "hi"},
                "queryStringParameters": None,
            },
            ddbclient=DynamoDbMockGetItemFail(),
        )
        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(
            response["body"],
            '{"message": "Fridge was not found"}',
        )

    def test_get_items(self):
        json_data = '[{"id": {"S": "test"}}]'
        response = FridgeHandler.lambda_handler(
            event={
                "httpMethod": "GET",
                "pathParameters": None,
                "queryStringParameters": None,
            },
            ddbclient=DynamoDbMockScan(),
        )
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], json_data)
