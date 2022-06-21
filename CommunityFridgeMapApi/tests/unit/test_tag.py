from multiprocessing import connection

from dependencies.python.db import layer_test
from dependencies.python.db import get_ddb_connection
import unittest
from dependencies.python.db import Tag

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



class TagTest(unittest.TestCase):

    def test_is_valid_tag_name(self):
        tag = Tag(tag_name='test&tag', db_client=None)
        self.assertFalse(tag.is_valid_tag_name('test&tag'))
        tag = Tag(tag_name='test-tag', db_client=None)
        self.assertTrue(tag.is_valid_tag_name('test-tag'))


    def test_set_tag(self):
        tag = Tag(tag_name='Test Tag', db_client=None)
        tag.set_tag('Test Tag')
        self.assertEqual(tag.tag_name, 'testtag')

    def test_has_required_fields(self):
        tag = Tag(tag_name=None, db_client=None)
        has_required_field, field = tag.has_required_fields()
        self.assertEqual(field, 'tag_name')
        self.assertFalse(has_required_field)
        tag = Tag(tag_name='test tag', db_client=None)
        self.assertTrue(tag.has_required_fields())


    def test_add_item(self):
        db_client = DynamoDbMockPutItem()
        tag = Tag(tag_name='Test_123-Tag', db_client=db_client)
        response = tag.add_item()
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Tag was succesfully added")
        self.assertEqual(response.status_code, 200)
