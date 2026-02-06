import unittest
import json
import logging
from unittest.mock import MagicMock
from dependencies.python.db import Fridge, FridgeReport, DB_Response


class FridgeStatsTest(unittest.TestCase):
    def setUp(self):
        # mock DynamoDB client
        self.mock_db = MagicMock()
        self.fridge = Fridge(db_client=self.mock_db)

    def parse_stats(self, resp: DB_Response):
        self.assertTrue(resp.is_successful())
        self.assertEqual(resp.status_code, 200)
        return json.loads(resp.json_data)
    def make_item(self, condition=None, include_report=True):
        data = {}
        if include_report:
            report = {}
            if condition is not None:
                report["condition"] = condition
            data["latestFridgeReport"] = report
        return {"json_data": {"S": json.dumps(data)}}

    def test_no_items(self):
        self.mock_db.scan.return_value = {}
        stats = self.parse_stats(self.fridge.get_fridge_stats())
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["no_report"], 0)
        self.assertEqual(stats["unknown"], 0)

    def test_known_condition(self):
        known = next(iter(FridgeReport.VALID_CONDITIONS))
        self.mock_db.scan.return_value = {"Items": [self.make_item(known)]}
        stats = self.parse_stats(self.fridge.get_fridge_stats())
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats[known], 1)
        self.assertEqual(stats["unknown"], 0)

    def test_no_report(self):
        self.mock_db.scan.return_value = {"Items": [{"json_data": {"S": "{}"}}]}
        stats = self.parse_stats(self.fridge.get_fridge_stats())
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["no_report"], 1)

    def test_unknown_condition(self):
        self.mock_db.scan.return_value = {"Items": [self.make_item("mystery")]}
        with self.assertLogs(level=logging.ERROR) as log:
            stats = self.parse_stats(self.fridge.get_fridge_stats())
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["unknown"], 1)
        self.assertIn("Unknown condition encountered: 'mystery'", "".join(log.output))

    def test_mixed_items(self):
        known = next(iter(FridgeReport.VALID_CONDITIONS))
        items = [
            self.make_item(known),
            self.make_item("alien"),
            {"json_data": {"S": "{}"}},
        ]
        self.mock_db.scan.return_value = {"Items": items}
        stats = self.parse_stats(self.fridge.get_fridge_stats())
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats[known], 1)
        self.assertEqual(stats["no_report"], 1)
        self.assertEqual(stats["unknown"], 1)
