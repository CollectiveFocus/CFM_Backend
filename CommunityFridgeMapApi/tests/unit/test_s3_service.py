import pytest
from dependencies.python.s3_service import translate_s3_url_for_client


@pytest.mark.parametrize(
    "url,env,expected",
    [
        (
            "https://fridge-report.s3.amazonaws.com/wonderful.webp",
            "aws",
            "https://fridge-report.s3.amazonaws.com/wonderful.webp",
        ),
        (
            "http://localstack:4566/brooklyn.webp",
            "local",
            "http://localhost:4566/brooklyn.webp",
        ),
    ]
)
def test_translate_s3_url_for_client(url, env, expected):
    actual = translate_s3_url_for_client(url, env=env)
    assert actual == expected
