import json
import base64

try:
    from s3_service import S3Service
except:
    from dependencies.python.s3_service import S3Service

def has_webp_magic_number(blob: bytes) -> bool:
    """
    Return True if the binary has valid webp magic numbers.

    Reference: https://datatracker.ietf.org/doc/html/draft-zern-webp
    """
    if len(blob) < 15:
        return False
    return (
        blob[0] == 0x52 and
        blob[1] == 0x49 and
        blob[2] == 0x46 and
        blob[3] == 0x46 and
        blob[8] == 0x57 and
        blob[9] == 0x45 and
        blob[10] == 0x42 and
        blob[11] == 0x50 and
        blob[12] == 0x56 and
        blob[13] == 0x50 and
        blob[14] == 0x38
    )

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
    def lambda_handler(event: dict, s3: S3Service) -> dict:
        bucket = "community-fridge-map-images"
        blob = ImageHandler.get_binary_body_from_event(event)
        if not has_webp_magic_number(blob):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "message": "Request could not be understood due to incorrect syntax. Image type must be webp."
                }),
            }
        try:
            key = s3.write(bucket, "webp", blob)
            url = s3.generate_file_url(bucket, key)
        except:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "message": "Unexpected error prevented server from fulfilling request."
                }),
            }
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
    s3 = S3Service()
    return ImageHandler.lambda_handler(event, s3)
