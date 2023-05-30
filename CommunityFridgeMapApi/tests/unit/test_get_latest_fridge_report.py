import unittest
from dependencies.python.db import Fridge
import json

class DynamoDbMockScanItem:
    def __init__(self):
        pass
    
    def scan(
        self,
        TableName=None,
        FilterExpression=None,
        ExpressionAttributeValues=None,
        ProjectionExpression=None,
    ):
        return {'Items': [{'json_data': {'S': '{"latestFridgeReport": {"fridgeId": "2fish5loavesfridge", "epochTimestamp": "1685405973", "timestamp": "2023-05-30T00:19:33Z", "condition": "good", "foodPercentage": 2}}'}},
                          {'json_data': {'S': '{"latestFridgeReport": {"fridgeId": "thefriendlyfridge", "epochTimestamp": "1685406040", "timestamp": "2023-05-30T00:20:40Z", "condition": "dirty", "foodPercentage": 1}}'}}]}


class FrdgeReportTest(unittest.TestCase):

    def test_get_latest_fridge_report(self):
        fridge = Fridge(db_client=DynamoDbMockScanItem())
        response = fridge.get_latest_fridge_reports()
        json_data = json.loads(response.json_data)
        self.assertEqual(response.message, "Successfully found fridge reports")
        self.assertEqual(len(json_data), 2)
        


