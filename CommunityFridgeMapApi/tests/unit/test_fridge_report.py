from multiprocessing import connection
from CommunityFridgeMapApi.dependencies.python.db import DB_Response

from dependencies.python.db import layer_test
from dependencies.python.db import get_ddb_connection
import unittest
from dependencies.python.db import FridgeReport

class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass

class FrdgeReportTest(unittest.TestCase):

    def test_required_fields(self):
        fridge_report = FridgeReport(fridge_report={'fridge_username': 'test', 'status': 'working', 'notes': 'all good out here'}, db_client=None)
        success, field = fridge_report.has_required_fields()
        self.assertFalse(success)
        self.assertEqual(field, "fridge_percentage")

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'test', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=None)
        success, field = fridge_report.has_required_fields()
        self.assertTrue(success)

    def test_set_timestamp(self):
        fridge_report = FridgeReport(fridge_report={'fridge_username': 'test', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=None)
        fridge_report.set_timestamp()
        self.assertIsNotNone(fridge_report.timestamp)
    
    def test_is_valid_status(self):
        fridge_report = FridgeReport(fridge_report={'status': 'i am a hacker, drop table'}, db_client=None)
        self.assertFalse(fridge_report.is_valid_status())

        fridge_report.status = "working"
        self.assertTrue(fridge_report.is_valid_status())

        fridge_report.status = "needs cleaning"
        self.assertTrue(fridge_report.is_valid_status())

        fridge_report.status = "needs servicing"
        self.assertTrue(fridge_report.is_valid_status())

        fridge_report.status = "not at location"
        self.assertTrue(fridge_report.is_valid_status())
    
    def test_is_valid_fridge_percentage(self):
        fridge_report = FridgeReport(fridge_report={'fridge_percentage': '50'}, db_client=None)
        self.assertFalse(fridge_report.is_valid_status())

        fridge_report.fridge_percentage = "0"
        self.assertTrue(fridge_report.is_valid_fridge_percentage())

        fridge_report.fridge_percentage = "33"
        self.assertTrue(fridge_report.is_valid_fridge_percentage())

        fridge_report.fridge_percentage = "66"
        self.assertTrue(fridge_report.is_valid_fridge_percentage())

        fridge_report.fridge_percentage = "100"
        self.assertTrue(fridge_report.is_valid_fridge_percentage())
    
    def test_add_item(self):
        fridge_report = FridgeReport(fridge_report={}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertFalse(db_reponse.success)
        self.assertEqual(db_reponse.message, "Missing Required Field: fridge_username")

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'hi', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertFalse(db_reponse.success)
        self.assertEqual(db_reponse.message, "Username Must Have A Character Length >= 3 and <= 32")

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'hi-', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertFalse(db_reponse.success)
        self.assertEqual(db_reponse.message, "Username Must Be Alphanumeric")

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'valid', 'status': 'hacking', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertFalse(db_reponse.success)
        self.assertTrue("Invalid Status, must to be one of" in db_reponse.message)

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'valid', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '50'}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertFalse(db_reponse.success)
        self.assertTrue("Invalid Fridge Percetage, must to be one of:" in db_reponse.message)

        fridge_report = FridgeReport(fridge_report={'fridge_username': 'test', 'status': 'working', 'notes': 'all good out here', 'fridge_percentage': '33'}, db_client=DynamoDbMockPutItem())
        db_reponse = fridge_report.add_item()
        self.assertTrue(db_reponse.success)
        self.assertEqual(db_reponse.message, "Fridge Report was succesfully added")