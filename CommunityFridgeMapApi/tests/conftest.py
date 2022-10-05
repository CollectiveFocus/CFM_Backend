import pytest
from tests.s3_service_stub import S3ServiceStub

@pytest.fixture
def s3_service_stub():
    return S3ServiceStub()
