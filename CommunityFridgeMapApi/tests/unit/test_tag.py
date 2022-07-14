import unittest
from dependencies.python.db import Tag

class DynamoDbMockPutItem():
    def __init__(self):
        pass

    def put_item(self, TableName=None, Item=None, ConditionExpression=None):
        pass

class TagTest(unittest.TestCase):

    def test_is_valid_tag_name(self):
        self.assertTrue(Tag.is_valid_tag_name('test-tag')[0])
        self.assertEqual(Tag.is_valid_tag_name('test-tag')[1], '')
        expected_false = [
            Tag.is_valid_tag_name('')[0],
            Tag.is_valid_tag_name(None)[0],
            Tag.is_valid_tag_name('ab')[0],
            Tag.is_valid_tag_name('test&tag')[0],
            Tag.is_valid_tag_name('TEST-tag_tag123xyui1234567890__--')[0]
        ]
        expected_equal = [
            (Tag.is_valid_tag_name('')[1], 'Length of tag_name is 0. It should be >= 3 but <= 32.'),
            (Tag.is_valid_tag_name(None)[1], 'Missing required fields: tag_name'),
            (Tag.is_valid_tag_name('ab')[1], 'Length of tag_name is 2. It should be >= 3 but <= 32.'),
            (Tag.is_valid_tag_name('test&tag')[1], 'tag_name contains invalid characters'),
            (Tag.is_valid_tag_name('TEST-tag_tag123xyui1234567890__--')[1],
                'Length of tag_name is 33. It should be >= 3 but <= 32.')
        ]
        for i in range(5):
            self.assertFalse(expected_false[i])
            self.assertEqual(expected_equal[i][0], expected_equal[i][1])


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
