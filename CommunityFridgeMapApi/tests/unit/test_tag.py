import unittest
from dependencies.python.db import Tag

class DynamoDbMockPutItem():
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass

class TagTest(unittest.TestCase):

    def test_is_valid_tag_name(self):
        tag = Tag(tag_name='', db_client=None)
        self.assertFalse(tag.is_valid_tag_name('')[0])
        self.assertEqual(tag.is_valid_tag_name('')[1], 'tag_name is an empty string')
        tag = Tag(tag_name=None, db_client=None)
        self.assertFalse(tag.is_valid_tag_name(None)[0])
        self.assertEqual(tag.is_valid_tag_name(None)[1], 'tag_name is None')
        tag = Tag(tag_name='ab', db_client=None)
        self.assertFalse(tag.is_valid_tag_name('ab')[0])
        self.assertEqual(tag.is_valid_tag_name('ab')[1], 'Length of the tag_name is 2. It should be >= 3 but <= 32.')
        tag = Tag(tag_name='test&tag', db_client=None)
        self.assertFalse(tag.is_valid_tag_name('test&tag')[0])
        self.assertEqual(tag.is_valid_tag_name('test&tag')[1], 'tag_name contains invalid characters')
        tag = Tag(tag_name='test-tag', db_client=None)
        self.assertTrue(tag.is_valid_tag_name('test-tag')[0])
        self.assertEqual(tag.is_valid_tag_name('test-tag')[1], '')
        tag = Tag(tag_name='TEST-tag_tag123xyui1234567890__--', db_client=None)
        self.assertFalse(tag.is_valid_tag_name('TEST-tag_tag123xyui1234567890__--')[0])
        self.assertEqual(tag.is_valid_tag_name('TEST-tag_tag123xyui1234567890__--')[1],
         'Length of the tag_name is 33. It should be >= 3 but <= 32.')

    def test_format_tag(self):
        tag = Tag(tag_name='Test Tag', db_client=None)
        tag.format_tag('Test Tag')
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
