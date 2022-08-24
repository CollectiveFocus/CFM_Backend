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
    def upload_handler(event: dict) -> dict:
        bucket = "fridge-report"
        key = Storage().write(bucket, ImageHandler.get_binary_body_from_event(event))
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

    @staticmethod
    def download_handler(event) -> dict:
        path_parameters = event["pathParameters"] or {}
        bucket = path_parameters["bucket"]
        key = path_parameters["key"]
        body = ImageHandler.encode_binary_file_for_response(
            Storage().read(bucket, key)
        )
        return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {
                "Content-Type": "image/webp",
                "Access-Control-Allow-Origin": "*",
            },
            "body": body
        }

def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    httpMethod = event.get("httpMethod")
    if httpMethod == "GET":
        return ImageHandler.download_handler(event)
    if httpMethod == "POST":
        return ImageHandler.upload_handler(event)
