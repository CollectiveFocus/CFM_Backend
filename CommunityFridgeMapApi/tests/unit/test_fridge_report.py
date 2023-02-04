import unittest
from dependencies.python.db import FridgeReport


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
                "message": "fridge_report was succesfully added",
                "success": True,
            },
        ]

        for data in test_data:
            response = FridgeReport(
                fridge_report=data["fridge_report"], db_client=DynamoDbMockPutItem()
            ).add_item()
            self.assertEqual(response.success, data["success"])
            self.assertTrue(data["message"] in response.message)
