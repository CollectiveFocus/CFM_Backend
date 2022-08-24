import pytest
import base64
from unittest.mock import patch, ANY
from functions.image.v1.app import ImageHandler
from tests.assert_resposne import assert_response


def test_upload(storage_stub):
    blob = b'123123123'
    b64encoded_blob = base64.b64encode(blob).decode("ascii")
    with patch.object(storage_stub, "write", wraps=storage_stub.write) as write_spy:
        with patch.object(storage_stub, "generate_file_url", wraps=storage_stub.generate_file_url) as generate_file_url_spy:
            response = ImageHandler.lambda_handler(
                event={
                    "isBase64Encoded": True,
                    "body": b64encoded_blob,
                },
                storage=storage_stub
            )

            write_spy.assert_called_once_with(ANY, "webp", blob)
            generate_file_url_spy.assert_called_once()
            assert_response(
                response,
                status=200,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                body={
                    "photoURL": ANY
                }
            )
