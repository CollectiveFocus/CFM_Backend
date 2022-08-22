# CFM_Backend

## Setup

1. SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
    * **You do not need to create an aws account to use SAM CLI, creating an aws account is OPTIONAL**
2. Python 3 - [Install Python 3](https://www.python.org/downloads/)
3. Docker - [Install Docker](https://docs.docker.com/get-docker/)

## Build and Test Locally

Confirm that the following requests work for you

1. `cd CommunityFridgeMapApi/`
2. `sam build --use-container`
3. `sam local invoke HelloWorldFunction --event events/event.json`
    * response: ```{"statusCode": 200, "body": "{\"message\": \"hello world\"}"}```
4. `sam local start-api`
5. `curl http://localhost:3000/hello`
    * response: ```{"message": "hello world"}```

## Setup Local Database Connection

**Guide that was used:** https://betterprogramming.pub/how-to-deploy-a-local-serverless-application-with-aws-sam-b7b314c3048c

Follow these steps to get Dynamodb running locally

1. **Start a local DynamoDB service**
    ```sh
    docker compose up
    # OR if you want to run it in the background:
    docker compose up -d
    ```
1. **Create tables**
    ```sh
    ./scripts/create_local_dynamodb_tables.sh
    ```
1. **Load data into your local Dynamodb tables**
    1. Fridge Data: `sam local invoke LoadFridgeDataFunction --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
1. **Get data from your local Dynamodb tables**
    1. **Generate sample payload:** `sam local generate-event apigateway aws-proxy --method GET --path document --body "" > local-event.json`
    2. `sam local invoke GetAllFunction --event local-event.json --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
    3. `aws dynamodb scan --table-name fridge --endpoint-url http://localhost:8000`

## API

Choose your favorite API platform for using APIs.
Recommend: https://www.postman.com/


### Fridge

### One Time Use
1. GET Fridge: `sam local invoke FridgesFunction --event events/local-event-get-fridge.json --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`

### Local Server
1. Start Server: `sam local start-api --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
2. Go to http://localhost:3000/v1/fridges/{fridge_id}
    * Example: http://localhost:3000/v1/fridges/thefriendlyfridge

### Fridge Report

#### One Time Use
1. POST FridgeReport: `sam local invoke FridgeReportFunction --event events/local-fridge-report-event.json --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
    * [OPTIONAL] Generate custom event Example: `sam local generate-event apigateway aws-proxy --method POST --path document --body "{\"status\": \"working\", \"fridge_percentage\": 0}" > events/local-fridge-report-event-2.json`
        * Add `"fridge_id": "{FRIDGE_ID}"` to pathParameter in generated file
2. Query Data: `aws dynamodb scan --table-name fridge_report --endpoint-url http://localhost:8000`

#### Local Server
1. Start Server: `sam local start-api --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
2. Make a POST Request to: `http://127.0.0.1:3000/v1/fridges/{fridge_id}/reports`
    * Example: `curl --location --request POST 'http://127.0.0.1:3000/v1/fridges/thefriendlyfridge/reports' --header 'Content-Type: application/json' --data-raw '{"status": "working", "fridge_percentage": 100}'`

## Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
CFM_BACKEND$ cd CommunityFridgeMapApi
CommunityFridgeMapApi$ pip install -r tests/requirements.txt --user
# unit test
CommunityFridgeMapApi$ python -m pytest tests/unit -v
```

To test with coverage
```bash
CommunityFridgeMapApi$ coverage run -m pytest tests/unit -v
CommunityFridgeMapApi$ coverage report
CommunityFridgeMapApi$ coverage html
```

MacOS:
```bash
CommunityFridgeMapApi$ open -a "Google Chrome" htmlcov/index.html
```

Windows:
```bash
CommunityFridgeMapApi$ start "Google Chrome" htmlcov/index.html
```

## Useful AWS SAM commands
1. `sam validate -t template.yaml`
2. `sam build --use-container`
    * Use this command before running the backend if you updated the code

## Useful Dynamodb Commands
1. `aws dynamodb scan --table-name fridge --endpoint-url http://localhost:8000`
2. `aws dynamodb scan --table-name fridge_report --endpoint-url http://localhost:8000`

## Useful formatting Command
```bash
CFM_BACKEND$ bash .git/hooks/pre-commit
```

## Resources

Project Documentation

  - [Architecture Brainstorming](https://docs.google.com/document/d/1FYClUD16KUY42_p93rZFHN-iyp94RU0Rtw517vj2jXs/edit)
  - [Architecture](https://docs.google.com/document/d/1yZVGAxVn4CEZyyce_Zuha3oYOOU8ey7ArBvLbm7l4bw/edit)
  - [Database Tables] (https://docs.google.com/document/d/16hjNHxm_ebZv8u_VolT1bdlJEDccqb7V67-Y6ljjUdY/edit?usp=sharing)
  - [Development Workflow](https://docs.google.com/document/d/1m9Xqo4QUVEBjMD7sMjxSHa3CxxjvrHppwc0nrdWCAAc/edit)
