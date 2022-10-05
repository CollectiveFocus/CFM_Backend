import pytest
import base64
from unittest.mock import patch, ANY
from functions.image.v1.app import ImageHandler
from tests.assert_resposne import assert_response
from tests.s3_service_stub import S3ServiceStub


def test_upload(s3_service_stub: S3ServiceStub):
    blob = base64.b64decode(
        "UklGRmh2AABXRUJQVlA4IFx2AADSvgGd"
    )  # Minimal blob with webp magic number.
    b64encoded_blob = base64.b64encode(blob).decode("ascii")
    with patch.object(
        s3_service_stub, "write", wraps=s3_service_stub.write
    ) as write_spy:
        with patch.object(
            s3_service_stub,
            "generate_file_url",
            wraps=s3_service_stub.generate_file_url,
        ) as generate_file_url_spy:
            response = ImageHandler.lambda_handler(
                event={
                    "isBase64Encoded": True,
                    "body": b64encoded_blob,
                },
                s3=s3_service_stub,
            )

            write_spy.assert_called_once_with(
                "community-fridge-map-images", "webp", blob
            )
            generate_file_url_spy.assert_called_once()
            assert_response(
                response,
                status=200,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                body={"photoUrl": ANY},
            )


def test_upload_invalid_binary(s3_service_stub: S3ServiceStub):
    blob = b"notwebp"
    b64encoded_blob = base64.b64encode(blob).decode("ascii")
    response = ImageHandler.lambda_handler(
        event={
            "isBase64Encoded": True,
            "body": b64encoded_blob,
        },
        s3=s3_service_stub,
    )

    assert_response(
        response,
        status=400,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        body={
            "message": "Request could not be understood due to incorrect syntax. Image type must be webp."
        },
    )
