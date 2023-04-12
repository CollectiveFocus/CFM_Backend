import json
import base64
import os

try:
    from s3_service import S3Service
except:
    from dependencies.python.s3_service import S3Service


def api_response(body, status_code) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": (body),
    } 

def get_s3_bucket_name():
        STAGE = os.getenv("Stage", None)
        bucket = "community-fridge-map-images"
        if STAGE is not None:
            bucket = f"{bucket}-{STAGE}"
        return bucket

class ImageHandler:

    def get_image_content_type(image_data: str):
        """
        Checks if the given image data represents a valid image and returns its content type.

        :param image_data: The binary data of the image.
        :return: The content type of the image if it is a valid image format, None otherwise.
        """
        signatures = {
            b'\xff\xd8': 'image/jpeg',
            b'\x89PNG\r\n\x1a\n': 'image/png',
            b'GIF87a': 'image/gif',
            b'GIF89a': 'image/gif',
            b'II*\x00': 'image/tiff',
            b'MM\x00*': 'image/tiff',
            # Add more signatures and content types as needed
        }

        webp_markers = [b'VP8 ', b'VP8L', b'VP8X']

        for signature, content_type in signatures.items():
            if image_data.startswith(signature):
                return content_type

        # Check for WebP format separately, as it requires additional checks
        for marker in webp_markers:
            if marker in image_data[:16]:
                return 'image/webp'

        return None

    @staticmethod
    def get_binary_body_from_event(event: dict) -> bytes:
        """Extract binary data from request body"""
        if event["isBase64Encoded"]:
            return base64.b64decode(event["body"])
        else:
            return None

    @staticmethod
    def encode_binary_file_for_response(blob: bytes) -> bytes:
        """
        Binary response body of lambda functions should be encoded in base64.
        https://docs.aws.amazon.com/apigateway/latest/developerguide/lambda-proxy-binary-media.html
        """
        return base64.b64encode(blob)
    
        
    @staticmethod
    def lambda_handler(event: dict, s3: S3Service) -> dict:
        if event.get("body", None) is None:
            error_message = {"message": "Received an empty body"}
            return api_response(body=json.dumps(error_message), status_code=400)
        if not event.get('isBase64Encoded', False):
            error_message = {"message": "Must be Base64 Encoded"}
            return api_response(body=json.dumps(error_message), status_code=400)

        bucket = get_s3_bucket_name()
        image_data = ImageHandler.get_binary_body_from_event(event)
        content_type = ImageHandler.get_image_content_type(image_data)
        if content_type is None:
            error_message = json.dumps({"message": "Invalid Image Format"})
            return api_response(body=error_message, status_code=400)
        try:
            key = s3.write(bucket, content_type, image_data)
            url = s3.generate_file_url(bucket, key)
        except:
            error_message: str = json.dumps({"message": "Unexpected error prevented server from fulfilling request."})
            return api_response(body={"message": error_message}, status_code=500)
        body = json.dumps({"photoUrl": url})
        return api_response(body=body, status_code=200)


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    s3 = S3Service()
    return ImageHandler.lambda_handler(event, s3)
