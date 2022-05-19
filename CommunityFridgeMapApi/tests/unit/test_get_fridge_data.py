from functions.dev.get_all.app import format_api_response

TEST_DB_RESPONSE = {
    'Items': {
        "fridge_name": {"S": "2 Fish 5 Loaves Fridge"},
        "state": {"S": "NY"},
        "address": {"S": "63 Whipple St, Brooklyn, NY 11206"},
        "instagram": {"S": "https://www.instagram.com/2fish5loavesfridge/"}
    },
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    }
}


def test_format_api_response():
    response = format_api_response(db_response=TEST_DB_RESPONSE, response_type='Items')
    assert response == {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': '{"message": {"fridge_name": {"S": "2 Fish 5 Loaves Fridge"}, "state": {"S": "NY"}, "address": {"S": "63 Whipple St, Brooklyn, NY 11206"}, "instagram": {"S": "https://www.instagram.com/2fish5loavesfridge/"}}}'
    }
