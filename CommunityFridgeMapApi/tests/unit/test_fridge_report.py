from CommunityFridgeMapApi.dependencies.python.db import DB_Response, Fridge
import unittest
from dependencies.python.db import FridgeReport


class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass


class FrdgeReportTest(unittest.TestCase):
    def test_required_fields(self):
        fridge_report = FridgeReport(
            fridge_report={
                "fridge_username": "test",
                "status": "working",
                "notes": "all good out here",
            },
            db_client=None,
        )
        success, field = fridge_report.has_required_fields()
        self.assertFalse(success)
        self.assertEqual(field, "fridge_percentage")

        fridge_report = FridgeReport(
            fridge_report={
                "fridge_username": "test",
                "status": "working",
                "notes": "all good out here",
                "fridge_percentage": "33",
            },
            db_client=None,
        )
        success, field = fridge_report.has_required_fields()
        self.assertTrue(success)

    def test_set_timestamp(self):
        fridge_report = FridgeReport(
            fridge_report={
                "fridge_username": "test",
                "status": "working",
                "notes": "all good out here",
                "fridge_percentage": "33",
            },
            db_client=None,
        )
        fridge_report.set_timestamp()
        self.assertIsNotNone(fridge_report.timestamp)

    def test_is_valid_status(self):
        self.assertFalse(FridgeReport.is_valid_status("i am a hacker, drop table"))
        valid_statuses = [
            "working",
            "needs cleaning",
            "needs servicing",
            "not at location",
        ]
        for status in valid_statuses:
            self.assertTrue(status)

    def test_is_valid_fridge_percentage(self):
        self.assertFalse(FridgeReport.is_valid_fridge_percentage("50"))
        valid_fridge_percentages = ["0", "33", "67", "100"]
        for fridge_percentage in valid_fridge_percentages:
            self.assertTrue(fridge_percentage)

    def test_is_valid_notes(self):
        valid_notes = [None, "", "t" * 256]
        for notes in valid_notes:
            self.assertTrue(FridgeReport.is_valid_notes(notes))
        self.assertFalse(FridgeReport.is_valid_notes("t" * 257))

    def test_add_item(self):
        test_data = [
            {
                "fridge_report": {},
                "message": "Missing Required Field: fridge_username",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "hi",
                    "status": "working",
                    "fridge_percentage": "33",
                },
                "message": "Username Must Have A Character Length >= 3 and <= 32",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "hi-",
                    "status": "working",
                    "fridge_percentage": "33",
                },
                "message": "Username Must Be Alphanumeric",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "valid",
                    "status": "hacking",
                    "fridge_percentage": "33",
                },
                "message": "Invalid Status, must to be one of",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "valid",
                    "status": "working",
                    "fridge_percentage": "50",
                },
                "message": "Invalid Fridge percentage, must to be one of",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "test",
                    "status": "working",
                    "fridge_percentage": "33",
                    "notes": "t" * 257,
                },
                "message": "Notes character length must be <= 256",
                "success": False,
            },
            {
                "fridge_report": {
                    "fridge_username": "test",
                    "status": "working",
                    "fridge_percentage": "33",
                },
                "message": "Fridge Report was succesfully added",
                "success": True,
            },
        ]

        for data in test_data:
            response = FridgeReport(
                fridge_report=data["fridge_report"], db_client=DynamoDbMockPutItem()
            ).add_item()
            self.assertEqual(response.success, data["success"])
            self.assertTrue(data["message"] in response.message)
