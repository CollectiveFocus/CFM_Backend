import pytest
from tests.storage_stub import StorageStub

@pytest.fixture
def storage_stub():
    return StorageStub()
