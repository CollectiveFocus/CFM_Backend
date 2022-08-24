import os
import uuid
import boto3

def get_s3_client(env=os.getenv("Environment")):
    endpoint_url="http://localstack:4566/" if env == "local" else None

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
    )

class Storage:
    def __init__(self):
        self._client = get_s3_client()

    def idempotent_create_bucket(self, bucket: str):
        self._client.create_bucket(
            Bucket=bucket,
            ACL="public-read"
        )

    def read(self, bucket: str, key: str):
        return self._client.get_object(
            Bucket=bucket,
            Key=key,
        )["Body"].read()

    def write(self, bucket: str, blob: bytes):
        key = str(uuid.uuid4())
        self.idempotent_create_bucket(bucket)
        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=blob,
        )
        return key
