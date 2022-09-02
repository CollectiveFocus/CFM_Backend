class S3ServiceStub:
    """Stub implementation of the Storage class for testing"""
    def __init__(self):
        self._buckets = {}
        self._current_index = 0

    def idempotent_create_bucket(self, bucket: str):
        if bucket not in self._buckets:
            self._buckets[bucket] = {}

    def read(self, bucket: str, key: str):
        return self._buckets[bucket][key]

    def write(self, bucket: str, extension: str, blob: bytes):
        key = f"{self._current_index}.{extension}"
        self._current_index += 1
        self.idempotent_create_bucket(bucket)
        self._buckets[bucket][key] = blob
        return key

    def generate_file_url(self, bucket: str, key: str):
        return f"http://localhost:4566/{bucket}/{key}"
