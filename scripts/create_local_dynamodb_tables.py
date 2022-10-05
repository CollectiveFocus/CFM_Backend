#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

ENDPOINT_URL = "http://localhost:8000"

scripts_dir = os.path.dirname(__file__)
schema_dir = os.path.join(scripts_dir, "../schema")

for file in os.listdir(schema_dir):
    file_path = os.path.abspath(os.path.join(schema_dir, file))
    if file.endswith(".json"):
        p = subprocess.run(
            [
                "aws",
                "dynamodb",
                "create-table",
                "--cli-input-json",
                Path(file_path).as_uri(),
                "--endpoint-url",
                ENDPOINT_URL,
            ],
            env=dict(os.environ, AWS_PAGER=""),
        )
        if p.returncode:
            print(f"Could not create DynamoDB table from {file}")
            exit(p.returncode)

