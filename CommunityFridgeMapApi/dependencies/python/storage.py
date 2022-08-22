from enum import Enum
import os
from tempfile import gettempdir
from pathlib import Path

def get_or_create_file_system_bucket(bucket: str):
    base = gettempdir()
    bucket_path = os.path.join(base, bucket)
    if not os.path.isdir(bucket_path):
        os.mkdir(bucket_path)
    return bucket_path

def write_to_file_system(bucket: str, object: str, blob: bytes):
    bucket_path = get_or_create_file_system_bucket(bucket)
    file_path = os.path.join(bucket_path, object)
    with open(file_path, "wb") as file:
        file.write(blob)
    return Path(file_path).as_uri()

def write_to_s3(bucket: str, object: str, blob: bytes):
    raise NotImplementedError()

class StorageType(Enum):
    FileSystem="file_system"
    S3="s3"

default_storage_type = StorageType.FileSystem if os.getenv("Environment") == "local" else StorageType.S3

class Storage:
    def __init__(self, type=default_storage_type):
        self._type = type

    def write(self, bucket: str, object: str, blob):
        if self._type == StorageType.FileSystem:
            uri = write_to_file_system(bucket, object, blob)
        elif self._type == StorageType.S3:
            uri = write_to_s3(bucket, object, blob)
        return uri
