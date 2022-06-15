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

class TagTest(unittest.TestCase):

    def test_is_valid_tag_name(self):
        tag = Tag(tag={'tag_name': 'one_love'}, db_client=None)
        self.assertTrue(tag.is_valid_tag_name())
        tag = Tag(tag={'tag_name': 'one#%@/love'}, db_client=None)
        self.assertFalse(tag.is_valid_display_name())
