from CommunityFridgeMapApi.dependencies.python.db import DB_Item

import unittest


class DB_Item_Test(unittest.TestCase):
    def test_remove_whitespace(self):
        result = DB_Item.remove_whitespace("   h  i th er  h o w    ")
        self.assertEqual(result, "h i th er h o w")

    def test_process_fields(self):
        object_dict = {"1": "  h  i  ", "2": {"test": "  h  i  "}, "3": ["  h  i  "]}
        result = DB_Item.process_fields(object_dict=object_dict)
        self.assertEqual(result, {"1": "h i", "2": {"test": "h i"}, "3": ["h i"]})
