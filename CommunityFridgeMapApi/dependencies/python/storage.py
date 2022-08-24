import os
import uuid
from urllib.parse import urlparse, urlunparse
import boto3
import botocore
from botocore.config import Config

def get_s3_client(env=os.getenv("Environment")):
    endpoint_url="http://localstack:4566/" if env == "local" else None
    config = Config(
        signature_version=botocore.UNSIGNED,
    )

    return boto3.client(
        "s3",
        config=config,
        endpoint_url=endpoint_url,
    )

def translate_s3_url_for_client(url: str, env=os.getenv("Environment")) -> str:
    """
    This function translates a S3 url to a client-accessible urls.

    From a lambda function's perspective, local AWS gateway is located at "localstack:4566" (within cfm-network).
    However, this hostname is not available for the host machine.
    In order to fetch S3 files from a local browser, we need to use "localhost:4566".
    """
    if env == "local":
        parsed_url = urlparse(url)
        return urlunparse(parsed_url._replace(netloc="localhost:4566"))
    return url


class Storage:
    def __init__(self):
        self._client = get_s3_client()

    def idempotent_create_bucket(self, bucket: str):
        self._client.create_bucket(Bucket=bucket)

    def write(self, bucket: str, extension: str, blob: bytes):
        key = f"{str(uuid.uuid4())}.{extension}"
        self.idempotent_create_bucket(bucket)
        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=blob,
        )
        return key

    def generate_file_url(self, bucket: str, key: str):
        url = self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
            },
            ExpiresIn=0,
        )
        return translate_s3_url_for_client(url)
