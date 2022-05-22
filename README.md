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

## Local Database Connection

**Guide that was used:** https://betterprogramming.pub/how-to-deploy-a-local-serverless-application-with-aws-sam-b7b314c3048c

Follow these steps to get Dynamodb running locally

1. `cd CommunityFridgeMapApi/`
2. **Create a Docker bridge network**
    1. `docker network create cfm-network`
    2. `docker run --network cfm-network --name dynamodb -d -p 8000:8000 amazon/dynamodb-local`
3. **Create Dynamodb tables locally** 
    1. **fridge:** `aws dynamodb create-table --table-name fridge --attribute-definitions AttributeName=state,AttributeType=S AttributeName=name,AttributeType=S --key-schema AttributeName=state,KeyType=HASH AttributeName=name,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000`
    2. **fridge_check_in:** `aws dynamodb create-table --table-name fridge_check_in --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=timestamp,AttributeType=N --key-schema AttributeName=pk,KeyType=HASH AttributeName=timestamp,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000`
    3. **fridge_history:** `aws dynamodb create-table --table-name fridge_history --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=timestamp,AttributeType=N --key-schema AttributeName=pk,KeyType=HASH AttributeName=timestamp,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000`
    4. **tag**: `aws dynamodb create-table --table-name tag --attribute-definitions AttributeName=name,AttributeType=S --key-schema AttributeName=name,KeyType=HASH  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000`
4. **Build the functions inside a Docker container**
    1. `sam build --use-container`
5. **Load data into your local Dynamodb tables**
    1. `sam local invoke LoadFridgeDataFunction --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
6. **Get data from your local Dynamodb tables**
    1. **Generate sample payload:** `sam local generate-event apigateway aws-proxy --method GET --path document --body "" > local-event.json`
    2. `sam local invoke GetAllFunction --event local-event.json --parameter-overrides ParameterKey=Environment,ParameterValue=local --docker-network cfm-network`
    3. `aws dynamodb scan --table-name fridge --endpoint-url http://localhost:8000`

## Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
CFM_BACKEND$ cd CommunityFridgeMapApi
CommunityFridgeMapApi$ pip install -r tests/requirements.txt --user
# unit test
CommunityFridgeMapApi$ python -m pytest tests/unit -v
```

## Useful AWS SAM commands
1. `sam validate -t template.yml`