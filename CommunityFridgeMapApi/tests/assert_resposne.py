import json
from typing import Union, Optional

def assert_response(
    response: dict,
    status: Optional[int]=None,
    headers: Optional[dict]=None,
    body: Union[str, bytes, dict, None]=None,
):
    """
    Make assertions against a lambda response.

    Only specified parameters are checked.
        Parameters:
            status: expected status code
            headers: expected headers
            body: expected body. It can be a string, dict (json), or (base64 encoded) bytes.
    """
    if status is not None:
        assert response["statusCode"] == status
    if headers is not None:
        assert response["headers"] == headers
    if body is not None:
        if type(body) == str or type(body) == bytes:
            assert response["body"] == body
        elif type(body) == dict:
            assert json.loads(response["body"]) == body
