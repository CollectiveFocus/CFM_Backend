from multiprocessing import connection

from dependencies.python.db import layer_test
from dependencies.python.db import get_ddb_connection
import unittest
from dependencies.python.db import Fridge


def test_layer_test():

    ret = layer_test()
    assert ret == "hello world"


def test_get_ddb_connection():
    connection = get_ddb_connection()
    assert str(type(connection)) == "<class 'botocore.client.DynamoDB'>"
    connection = get_ddb_connection(env="local")
    assert str(type(connection)) == "<class 'botocore.client.DynamoDB'>"


class DynamoDbMockPutItem:
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass


class FridgeTest(unittest.TestCase):
    def test_required_fields(self):
        fridge = Fridge(fridge={}, db_client=None)
        has_required_field, field = fridge.has_required_fields()
        self.assertEqual(field, "display_name")
        self.assertFalse(has_required_field)
        fridge = Fridge(
            fridge={
                "display_name": "test fridge",
                "address": "63 Whipple St, Brooklyn, NY 11206",
                "lat": 23.4523,
                "long": 14.452,
            },
            db_client=None,
        )
        self.assertTrue(fridge.has_required_fields())

    def test_set_username(self):
        fridge = Fridge(fridge={"display_name": "The Friendly Fridge"}, db_client=None)
        fridge.set_username()
        self.assertEqual(fridge.username, "thefriendlyfridge")

    def test_set_last_edditted(self):
        fridge = Fridge(fridge={"display_name": "The Friendly Fridge"}, db_client=None)
        self.assertIsNone(fridge.last_edited)
        fridge.set_last_edited()
        self.assertIsNotNone(fridge.last_edited)

    def test_is_valid_display_name(self):
        fridge = Fridge(fridge={"display_name": "The Friendly Fridge"}, db_client=None)
        self.assertTrue(fridge.is_valid_display_name())
        fridge = Fridge(
            fridge={"display_name": "The Friendly Fridge #%@/"}, db_client=None
        )
        self.assertFalse(fridge.is_valid_display_name())

    def test_add_item(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(
            fridge={
                "display_name": "test fridge",
                "address": "63 Whipple St, Brooklyn, NY 11206",
                "lat": 23.4523,
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Missing Required Field: long")
        self.assertEqual(response.status_code, 400)
        fridge = Fridge(
            fridge={
                "display_name": "Test Fridge",
                "address": "63 Whipple St, Brooklyn, NY 11206",
                "lat": 23.4523,
                "long": 14.452,
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Fridge was succesfully added")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(fridge.last_edited)

    def test_format_dynamodb_item(self):
        fridge = {
            "display_name": "test",
            "username": "test",
            "address": "test",
            "instagram": "test",
            "info": "test",
            "url": "test",
            "neighborhood": "test",
            "organizer_email": "test",
            "tags": [],
            "food_accepts": [],
            "food_restrictions": [],
            "lat": "test",
            "long": "test",
            "last_edited": 2342353,
            "profile_image": "test",
            "report_timestamp": "test",
            "report_notes": "test",
            "report_status": "test",
            "report_image": "test",
        }
        fridge_item = Fridge(fridge=fridge, db_client=None).format_dynamodb_item()
        expected_response = {
            "display_name": {"S": "test"},
            "username": {"S": "test"},
            "address": {"S": "test"},
            "instagram": {"S": "test"},
            "info": {"S": "test"},
            "url": {"S": "test"},
            "neighborhood": {"S": "test"},
            "organizer_email": {"S": "test"},
            "tags": {"L": []},
            "food_accepts": {"L": []},
            "food_restrictions": {"L": []},
            "lat": {"S": "test"},
            "long": {"S": "test"},
            "last_edited": {"N": 2342353},
            "profile_image": {"S": "test"},
            "report_timestamp": {"S": "test"},
            "report_notes": {"S": "test"},
            "report_status": {"S": "test"},
            "report_image": {"S": "test"},
        }
        self.assertEqual(fridge_item, expected_response)

    def test_is_valid_username(self):
        is_valid, message = Fridge.is_valid_username(None)
        self.assertEqual(message, "Missing Required Field: username")
        self.assertFalse(is_valid)

        is_valid, message = Fridge.is_valid_username("hi-there")
        self.assertEqual(message, "Username Must Be Alphanumeric")
        self.assertFalse(is_valid)

        is_valid, message = Fridge.is_valid_username("hi")
        self.assertEqual(
            message, "Username Must Have A Character Length >= 3 and <= 32"
        )
        self.assertFalse(is_valid)
