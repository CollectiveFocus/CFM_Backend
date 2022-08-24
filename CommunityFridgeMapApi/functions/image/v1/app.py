import json
import base64

try:
    from storage import Storage
except:
    from dependencies.python.storage import Storage

class ImageHandler:
    @staticmethod
    def get_binary_body_from_event(event: dict) -> bytes:
        assert event["isBase64Encoded"]
        return base64.b64decode(event["body"])

    @staticmethod
    def encode_binary_file_for_response(blob: bytes) -> bytes:
        return base64.b64encode(blob)

    @staticmethod
    def lambda_handler(event: dict, storage: Storage) -> dict:
        bucket = "fridge-report"
        key = storage.write(bucket, ImageHandler.get_binary_body_from_event(event))
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "bucket": bucket,
                "key": key,
            })
        }


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    storage = Storage()
    return ImageHandler.lambda_handler(event, storage)
