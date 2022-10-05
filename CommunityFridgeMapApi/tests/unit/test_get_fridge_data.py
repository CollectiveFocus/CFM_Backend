# from functions.dev.get_all.app import format_api_response
from functions.dev.get_all.app import GetAllFridgesHandler

TEST_DB_RESPONSE_SUCCESS = {
    'Items': {
        "name": {"S": "2 Fish 5 Loaves Fridge"},
        "state": {"S": "NY"},
        "address": {"S": "63 Whipple St, Brooklyn, NY 11206"},
        "instagram": {"S": "https://www.instagram.com/2fish5loavesfridge/"}
    },
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    }
}

TEST_DB_RESPONSE_FAILED = {
    'ResponseMetadata': {
        'HTTPStatusCode': 400
    }
}

class DynamoDbMockSuccess():
    def __init__(self):
        pass
    
    def scan(TableName: str):
        return TEST_DB_RESPONSE_SUCCESS


def test_format_api_response_success():
    handler = GetAllFridgesHandler(env="", table_name="", ddbclient={})
    response = handler.format_api_response(db_response=TEST_DB_RESPONSE_SUCCESS, response_type='Items')
    assert response == {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': '{"message": {"name": {"S": "2 Fish 5 Loaves Fridge"}, "state": {"S": "NY"}, "address": {"S": "63 Whipple St, Brooklyn, NY 11206"}, "instagram": {"S": "https://www.instagram.com/2fish5loavesfridge/"}}}'
    }

def test_format_api_response_failed():
    handler = GetAllFridgesHandler(env="", table_name="", ddbclient={})
    response = handler.format_api_response(db_response=TEST_DB_RESPONSE_FAILED, response_type='Items')
    assert response == {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin':'*'},
                'body': '{"message": "Item(s) not found"}'
    }

def test_handler_success():
    handler = GetAllFridgesHandler(env="", table_name="", ddbclient=DynamoDbMockSuccess)
    response = handler.lambda_handler(event=None, context=None)
    assert response == {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': '{"message": {"name": {"S": "2 Fish 5 Loaves Fridge"}, "state": {"S": "NY"}, "address": {"S": "63 Whipple St, Brooklyn, NY 11206"}, "instagram": {"S": "https://www.instagram.com/2fish5loavesfridge/"}}}'
    }

