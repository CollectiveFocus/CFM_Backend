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
    def test_set_id(self):
        fridge = Fridge(fridge={"name": "The Friendly Fridge"}, db_client=None)
        fridge.set_id()
        self.assertEqual(fridge.id, "thefriendlyfridge")

    def test_set_last_edditted(self):
        fridge = Fridge(fridge={"name": "The Friendly Fridge"}, db_client=None)
        self.assertIsNone(fridge.last_edited)
        fridge.set_last_edited()
        self.assertIsNotNone(fridge.last_edited)

    def test_is_valid_name(self):
        fridge = Fridge(fridge={"name": "The Friendly Fridge"}, db_client=None)
        self.assertTrue(fridge.is_valid_name())
        fridge = Fridge(fridge={"name": "The Friendly Fridge #%@/"}, db_client=None)
        self.assertFalse(fridge.is_valid_name())

    def test_add_item_invalid_name(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(
            fridge={
                "name": "&^@(*#(&(*$",
                "location": {"geoLat": 124242, "geoLng": 2345235},
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertFalse(response.success)
        self.assertEqual(
            response.message, "Name Can Only Contain Letters, Numbers, and Spaces"
        )
        self.assertEqual(response.status_code, 400)

    def test_add_item_missing_required_field(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(
            fridge={
                "name": "test fridge",
                "location": {"geoLat": 12124},
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Missing Required Field: location/geoLng")
        self.assertEqual(response.status_code, 400)

    def test_add_item_min_length_failure(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(
            fridge={
                "name": "it",
                "location": {"geoLat": 12124, "geoLng": 232523},
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertFalse(response.success)
        self.assertEqual(response.message, "id character length must be >= 3")
        self.assertEqual(response.status_code, 400)

    def test_add_item_success(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(
            fridge={
                "name": "Test Fridge",
                "location": {"geoLat": 124242, "geoLng": 2345235},
            },
            db_client=db_client,
        )
        response = fridge.add_item()
        self.assertTrue(response.success)
        self.assertEqual(response.message, "fridge was succesfully added")
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(fridge.last_edited)

    def test_format_dynamodb_item_v2(self):
        fridge = {
            "id": "test",
            "name": "test",
            "tags": [],
            "location": {},
            "maintainer": {},
            "notes": "test",
            "food_accepts": [],
            "food_restrictions": [],
            "photoURL": "test",
            "last_edited": 2342353,
            "verified": True,
            "latest_report": {},
            "fake_field": {},
        }
        fridge_item = Fridge(fridge=fridge, db_client=None).format_dynamodb_item_v2()
        expected_response = {
            "id": {"S": "test"},
            "name": {"S": "test"},
            "tags": {"L": []},
            "location": {"S": "{}"},
            "maintainer": {"S": "{}"},
            "notes": {"S": "test"},
            "food_accepts": {"L": []},
            "food_restrictions": {"L": []},
            "photoURL": {"S": "test"},
            "last_edited": {"N": 2342353},
            "verified": {"B": True},
            "latest_report": {"S": "{}"},
        }
        self.assertEqual(fridge_item, expected_response)
        fridge_item = Fridge(
            fridge={"id": ""}, db_client=None
        ).format_dynamodb_item_v2()
        self.assertEqual(fridge_item, {})

    def test_is_valid_id(self):
        is_valid, message = Fridge.is_valid_id(None)
        self.assertEqual(message, "Missing Required Field: id")
        self.assertFalse(is_valid)

        is_valid, message = Fridge.is_valid_id("hi-there")
        self.assertEqual(message, "id Must Be Alphanumeric")
        self.assertFalse(is_valid)

        is_valid, message = Fridge.is_valid_id("hi")
        self.assertEqual(message, "id Must Have A Character Length >= 3 and <= 32")
        self.assertFalse(is_valid)

    def test_validate_fields_required_fields(self):
        fridge = Fridge(fridge={}, db_client=None)
        field_validator = fridge.validate_fields()
        self.assertFalse(field_validator.is_valid)
        self.assertEqual(field_validator.message, "Missing Required Field: id")

    def test_validate_fields_min_length(self):
        fridge = Fridge(fridge={"id": "x"}, db_client=None)
        field_validator = fridge.validate_fields()
        self.assertFalse(field_validator.is_valid)
        self.assertEqual(field_validator.message, "id character length must be >= 3")

    def test_validate_fields_max_length(self):
        fridge = Fridge(fridge={"id": "x" * 33}, db_client=None)
        field_validator = fridge.validate_fields()
        self.assertFalse(field_validator.is_valid)
        self.assertEqual(field_validator.message, "id character length must be <= 32")

    def test_validate_fields_success(self):
        fridge = Fridge(
            fridge={
                "id": "good",
                "name": "good",
                "location": {"geoLat": 232342, "geoLng": 2342342},
            },
            db_client=None,
        )
        field_validator = fridge.validate_fields()
        self.assertTrue(field_validator.is_valid)
        self.assertEqual(
            field_validator.message, "All Fields Were Successfully Validated"
        )
