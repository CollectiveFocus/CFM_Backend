import unittest
from dependencies.python.db import FridgeReport
import json

class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass

    def get_item(self, TableName=None, Key=None):
        return {"Item": {"json_data": {"S": '{"id": {"S": "test"}}'}}}
    def query(TableName=None,
            KeyConditionExpression=None,
            ExpressionAttributeValues=None,
            ProjectionExpression=None,
            Limit=None,ExclusiveStartKey=None):
        if ExclusiveStartKey is None:
            return {'Items': [{'json_data': {'S': '{"notes": "Filled with Mars bars and M&M candy.", "fridgeId": "fakeData", "photoUrl": "https://s3.amazonaws.com/bucket/path/food.webp", "epochTimestamp": "1678749326", "timestamp": "2023-03-13T23:15:26Z", "condition": "dirty", "foodPercentage": 3}'}}, {'json_data': {'S': '{"notes": "Milk, so much milk", "fridgeId": "greenpointfridge", "photoUrl": "https://s3.amazonaws.com/bucket/path/food.webp", "epochTimestamp": "1678749354", "timestamp": "2023-03-13T23:15:54Z", "condition": "good", "foodPercentage": 2}'}}], 'Count': 2, 'ScannedCount': 2, 'LastEvaluatedKey': {'fridgeId': {'S': 'greenpointfridge'}, 'epochTimestamp': {'N': '1678749354'}}}
        else :
            return {'Items': [{'json_data': {'S': '{"notes": "6 dozen eggs", "fridgeId": "fakeData", "photoUrl": "https://s3.amazonaws.com/bucket/path/food.webp", "epochTimestamp": "1678749411", "timestamp": "2023-03-13T23:16:51Z", "condition": "good", "foodPercentage": 1}'}}, {'json_data': {'S': '{"notes": "Berries, peanut butter, bananas, and butter.", "fridgeId": "greenpointfridge", "photoUrl": "https://s3.amazonaws.com/bucket/path/food.webp", "epochTimestamp": "1678749609", "timestamp": "2023-03-13T23:20:09Z", "condition": "good", "foodPercentage": 3}'}}], 'Count': 2, 'ScannedCount': 2, 'LastEvaluatedKey': {'fridgeId': {'S': 'greenpointfridge'}, 'epochTimestamp': {'N': '1678749609'}}}
        
    def update_item(
        self,
        TableName=None,
        Key=None,
        ExpressionAttributeNames=None,
        ExpressionAttributeValues=None,
        UpdateExpression=None,
    ):
        pass


class FrdgeReportTest(unittest.TestCase):
    def test_set_timestamp(self):
        fridge_report = FridgeReport(
            fridge_report={
                "fridgeId": "test",
                "condition": "good",
                "notes": "all good out here",
                "foodPercentage": 2,
            },
            db_client=None,
        )
        fridge_report.set_timestamp()
        self.assertIsNotNone(fridge_report.epochTimestamp)
        self.assertIsNotNone(fridge_report.timestamp)

    def test_validate_fields(self):
        test_data = [
            {
                "fridge_report": {
                    "notes": "all good",
                    "fridgeId": "thefriendlyfridge",
                    "photoUrl": "s3.url",
                    "epochTimestamp": 34234,
                    "timestamp": "good",
                    "condition": "good",
                    "foodPercentage": 3,
                },
                "valid": True,
                "message": "All Fields Were Successfully Validated",
            },
            {
                "fridge_report": {},
                "valid": False,
                "message": "Missing Required Field: fridgeId",
            },
            {
                "fridge_report": {"fridgeId": "thefriendlyfridge"},
                "valid": False,
                "message": "Missing Required Field: condition",
            },
            {
                "fridge_report": {"fridgeId": "thefriendlyfridge", "condition": "fake"},
                "valid": False,
                "message": "condition must to be one of",
            },
            {
                "fridge_report": {
                    "fridgeId": "thefriendlyfridge",
                    "condition": "good",
                },
                "valid": False,
                "message": "Missing Required Field: foodPercentage",
            },
            {
                "fridge_report": {
                    "fridgeId": "thefriendlyfridge",
                    "condition": "good",
                    "foodPercentage": 99,
                },
                "valid": False,
                "message": "foodPercentage must to be one of",
            },
            {
                "fridge_report": {
                    "fridgeId": "thefriendlyfridge",
                    "condition": "good",
                    "foodPercentage": 3,
                },
                "valid": True,
                "message": "All Fields Were Successfully Validated",
            },
            {
                "fridge_report": {
                    "fridgeId": "thefriendlyfridge",
                    "condition": "good",
                    "foodPercentage": 3,
                    "notes": "x" * 257,
                },
                "valid": False,
                "message": "notes character length must be <= 256",
            },
            {
                "fridge_report": {
                    "fridgeId": "thefriendlyfridge",
                    "condition": "good",
                    "foodPercentage": 3,
                    "photoUrl": "x" * 2049,
                },
                "valid": False,
                "message": "photoUrl character length must be <= 2048",
            },
        ]

        for data in test_data:
            validator = FridgeReport(
                db_client=None, fridge_report=data["fridge_report"]
            ).validate_fields()
            self.assertEqual(validator.is_valid, validator.is_valid)
            self.assertTrue(data["message"] in validator.message)

    def test_add_item(self):
        test_data = [
            {
                "fridge_report": {},
                "message": "Missing Required Field: fridgeId",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridgeId": "hi",
                    "condition": "good",
                    "foodPercentage": 2,
                },
                "message": "fridgeId character length must be >= 3",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridgeId": "valid",
                    "condition": "hacking",
                    "foodPercentage": 2,
                },
                "message": "condition must to be one of",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridgeId": "valid",
                    "condition": "good",
                    "foodPercentage": 50,
                },
                "message": "foodPercentage must to be one of",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridgeId": "test",
                    "condition": "good",
                    "foodPercentage": 2,
                    "notes": "t" * 257,
                },
                "message": "notes character length must be <= 256",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridgeId": "test",
                    "condition": "good",
                    "foodPercentage": 2,
                },
                "fridgeId": "test",
                "success": True,
            },
        ]

        for data in test_data:
            response = FridgeReport(
                fridge_report=data["fridge_report"], db_client=DynamoDbMockPutItem()
            ).add_item()
            self.assertEqual(response.success, data["success"])
            if "message" in data:
                self.assertTrue(data["message"] in response.message)
            else:
                response_dict_data = json.loads(response.json_data)
                self.assertEqual(response_dict_data['fridgeId'], data['fridgeId'])
                self.assertTrue("timestamp" in response_dict_data)

    def test_get_all_reports(self):
        response = FridgeReport(fridge_report=None, db_client=DynamoDbMockPutItem()).get_all_reports(fridgeId='fakeFridge',lastEvaluatedKey=None)
        self.assertTrue(response.success)