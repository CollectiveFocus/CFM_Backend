try:
    from db import get_ddb_connection, Fridge
except:
    from dependencies.python.db import get_ddb_connection, Fridge


def lambda_handler(event: dict, context: 'awslambdaric.lambda_context.LambdaContext') -> dict:
    request_params: dict = {
        "fridge_state": "NY",
        "fridge_name": "test"
    }
    response: dict = create_api_response(request_params)
    return response


def create_api_response(params: dict) -> dict:
    db_response_item = get_db_response(params)


def get_db_response() -> dict:
    db_client = get_ddb_connection()
    db_response_item = Fridge(db_client).get_item()
