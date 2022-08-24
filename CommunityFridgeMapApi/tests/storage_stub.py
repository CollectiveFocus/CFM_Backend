class StorageStub:
    def __init__(self):
        self._buckets = {}
        self._current_index = 0

    def idempotent_create_bucket(self, bucket: str):
        if bucket not in self._buckets:
            self._buckets[bucket] = {}

    def read(self, bucket: str, key: str):
        return self._buckets[bucket][key]

    def write(self, bucket: str, blob: bytes):
        key = str(self._current_index)
        self._current_index += 1
        self.idempotent_create_bucket(bucket)
        self._buckets[bucket][key] = blob
        return key
