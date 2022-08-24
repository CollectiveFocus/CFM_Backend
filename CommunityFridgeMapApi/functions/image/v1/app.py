import json
import base64

try:
    from storage import Storage
except:
    from dependencies.python.storage import Storage

class ImageHandler:
    @staticmethod
    def get_binary_body_from_event(event: dict) -> bytes:
        """Extract binary data from request body"""
        assert event["isBase64Encoded"]
        return base64.b64decode(event["body"])

    @staticmethod
    def encode_binary_file_for_response(blob: bytes) -> bytes:
        """
        Binary response body of lambda functions should be encoded in base64.
        https://docs.aws.amazon.com/apigateway/latest/developerguide/lambda-proxy-binary-media.html
        """
        return base64.b64encode(blob)

    @staticmethod
    def lambda_handler(event: dict, storage: Storage) -> dict:
        bucket = "fridge-report"
        key = storage.write(bucket, "webp", ImageHandler.get_binary_body_from_event(event))
        url = storage.generate_file_url(bucket, key)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "photoURL": url,
            })
        }


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    storage = Storage()
    return ImageHandler.lambda_handler(event, storage)
