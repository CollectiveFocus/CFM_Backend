from CommunityFridgeMapApi.dependencies.python.db import DB_Response

import unittest


class DB_Response_Test(unittest.TestCase):
    def test_api_format(self):
        db_response = DB_Response(success=True, status_code=201, message="testing")
        api_format = db_response.api_format()
        self.assertEqual(api_format["statusCode"], 201)
        self.assertEqual(api_format["body"], '{"message": "testing"}')
