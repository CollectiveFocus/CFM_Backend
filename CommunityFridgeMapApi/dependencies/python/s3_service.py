import os
import uuid
from urllib.parse import urlparse, urlunparse
import logging
import boto3
import botocore
from botocore.exceptions import ClientError
from botocore.config import Config

def get_s3_client(env):
    endpoint_url="http://localstack:4566/" if env == "local" else None
    config = Config(
        signature_version=botocore.UNSIGNED, # Do not include signatures in s3 presigned-urls.
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


class S3ServiceException(Exception):
    pass


class S3Service:
    """
    Adapter class for persisting binary files in S3 buckets.
    """
    def __init__(self, env=os.getenv("Environment")):
        self._env = env
        self._client = get_s3_client(env)

    def idempotent_create_bucket(self, bucket: str):
        """
        Creates a bucket if there is no existing bucket with the same name.
        No-op when not local.
            Parameters:
                bucket: name of the bucket
        """
        if self._env != "local":
            return
        try:
            self._client.create_bucket(Bucket=bucket)
        except ClientError as e:
            logging.error(e)
            raise S3ServiceException(f"Failed to create a bucket {bucket}")

    def write(self, bucket: str, content_type: str, blob: bytes):
        """
        writes a binary file to the storage.
            Parameters:
                bucket: bucket to put file into
                extension: file extension
                blob: binary data to be written
            Returns:
                The key of the newly created file
        """
        extension = content_type.split("/")[1]
        key = f"{str(uuid.uuid4())}.{extension}"
        self.idempotent_create_bucket(bucket)

        try:
            self._client.put_object(
                Bucket=bucket,
                Key=key,
                Body=blob,
                ContentType=content_type
            )
        except ClientError as e:
            logging.error(e)
            raise S3ServiceException(f"Failed to save file {key} in bucket {bucket}")

        return key

    def generate_file_url(self, bucket: str, key: str):
        """
        generates an url for the client to access a persisted file.
            Parameters:
                bucket: name of the bucket that contains the file
                key: key of the file within the bucket
            Returns:
                A public url for the specified file
        """
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                },
                ExpiresIn=0,
            )
        except ClientError as e:
            logging.error(e)
            raise S3ServiceException(f"Failed to generate url for file {key} in bucket {bucket}")

        return translate_s3_url_for_client(url)
