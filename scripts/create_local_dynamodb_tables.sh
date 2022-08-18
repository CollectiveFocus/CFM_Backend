SCRIPTS_DIR="$(dirname "$0")"
SCHEMA_DIR="$(realpath $SCRIPTS_DIR/../schema)"
ENDPOINT_URL="http://localhost:8000"

for SCHEMA_FILE in $SCHEMA_DIR/*.json; do
  AWS_PAGER="" aws dynamodb create-table --cli-input-json "file://$SCHEMA_FILE" --endpoint-url $ENDPOINT_URL
  if [ $? -ne 0 ]; then
    echo "Failed to create table from $SCHEMA_FILE"
    exit 1
  fi
done

echo "Successfully created tables at $ENDPOINT_URL"
