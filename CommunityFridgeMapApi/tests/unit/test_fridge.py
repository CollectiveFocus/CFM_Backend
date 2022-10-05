from multiprocessing import connection

from dependencies.python.db import layer_test
from dependencies.python.db import get_ddb_connection
import unittest
from dependencies.python.db import Fridge
from dependencies.python.db import InvalidStateException
from dependencies.python.db import RequiredFieldMissingException

def test_layer_test():

    ret = layer_test()
    assert ret == "hello world"

def test_get_ddb_connection():
    connection = get_ddb_connection()
    assert str(type(connection)) == "<class 'botocore.client.DynamoDB'>"
    connection = get_ddb_connection(env="local")
    assert str(type(connection)) == "<class 'botocore.client.DynamoDB'>"

class DynamoDbMockPutItem():
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass
    


class FrdgeTest(unittest.TestCase):

    def test_required_fields(self):
        fridge = Fridge(fridge={}, db_client=None)
        self.assertRaises(RequiredFieldMissingException, fridge.has_required_fields)
        fridge = Fridge(fridge={'display_name': 'test fridge', 'fridge_state': 'NY', 'address': '63 Whipple St, Brooklyn, NY 11206', 'lat': 23.4523, 'long': 14.452}, db_client=None)
        self.assertTrue(fridge.has_required_fields())

    def test_is_valid_fridge_state(self):
        fridge = Fridge(fridge={'fridge_state': 'fake'}, db_client=None)
        self.assertRaises(InvalidStateException, fridge.is_valid_fridge_state)
        fridge = Fridge(fridge={'fridge_state': 'ny'}, db_client=None)
        self.assertTrue(fridge.is_valid_fridge_state())
        fridge = Fridge(fridge={'fridge_state': 'NY'}, db_client=None)
        self.assertTrue(fridge.is_valid_fridge_state())

    def test_set_username(self):
        fridge = Fridge(fridge={'display_name': 'The Friendly Fridge'}, db_client=None)
        fridge.set_username()
        self.assertEqual(fridge.username, 'thefriendlyfridge')

    def test_add_fridge(self):
        db_client = DynamoDbMockPutItem()
        fridge = Fridge(fridge={'display_name': 'The Friendly Fridge'}, db_client=db_client)
        self.assertRaises(RequiredFieldMissingException, fridge.add_fridge)
        fridge = Fridge(fridge={'display_name': 'test fridge', 'fridge_state': 'nyc', 'address': '63 Whipple St, Brooklyn, NY 11206', 'lat': 23.4523, 'long': 14.452}, db_client=db_client)
        self.assertRaises(InvalidStateException, fridge.is_valid_fridge_state)
        fridge = Fridge(fridge={'display_name': 'Test Fridge', 'fridge_state': 'ny', 'address': '63 Whipple St, Brooklyn, NY 11206', 'lat': 23.4523, 'long': 14.452}, db_client=db_client)
        fridge.add_fridge()
        self.assertEqual(fridge.username, 'testfridge')

    def test_build_fridge_item(self):
        fridge = {
            'display_name': 'test',
            'username': 'test',
            'fridge_state': 'test',
            'address': 'test',
            'instagram': 'test',
            'info': 'test',
            'url': 'test',
            'neighborhood': 'test',
            'organizer_email': 'test',
            'tags': [],
            'food_accepts': [],
            'food_restrictions': [],
            'lat': 'test',
            'long': 'test',
            'last_editted': 2342353,
            'profile_image': 'test',
            'check_in_time': 'test',
            'check_in_notes': 'test',
            'check_in_status': 'test',
            'check_in_image': 'test'
        }
        fridge_item = Fridge(fridge=fridge, db_client=None).build_fridge_item()
        expected_response = {
            'display_name': {'S': 'test'},
            'username': {'S': 'test'},
            'fridge_state': {'S': 'TEST'},
            'address': {'S': 'test'},
            'instagram': {'S': 'test'},
            'info': {'S': 'test'},
            'url': {'S': 'test'},
            'neighborhood': {'S': 'test'},
            'organizer_email':{'S': 'test'},
            'tags':{'L': []},
            'food_accepts': {'L': []},
            'food_restrictions':{'L': []},
            'lat':{'S': 'test'},
            'long': {'S': 'test'},
            'last_editted': {'N': 2342353},
            'profile_image':{'S': 'test'},
            'check_in_time':{'S': 'test'},
            'check_in_notes':{'S': 'test'},
            'check_in_status':{'S': 'test'},
            'check_in_image':{'S': 'test'},
        }
        self.assertEqual(fridge_item, expected_response)