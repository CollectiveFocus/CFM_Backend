import json
import uuid
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
    def lambda_handler(event: dict) -> dict:
        bucket = "fridge_images"
        uri = Storage().write(bucket, str(uuid.uuid4()), ImageHandler.get_binary_body_from_event(event))
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "uri": uri,
            })
        }

def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    return ImageHandler.lambda_handler(event)
