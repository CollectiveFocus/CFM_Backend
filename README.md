# CFM_Backend

## Setup

1. SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
2. Python 3 - [Install Python 3](https://www.python.org/downloads/)
3. Docker - [Install Docker](https://docs.docker.com/get-docker/)

## Build and Test Locally

Confirm that the following requests work for you

1. `cd CommunityFridgeMapApi/`
2. `sam local invoke HelloWorldFunction --event events/event.json`
    * response: ```{"statusCode": 200, "body": "{\"message\": \"hello world\"}"}```
3. `sam local start-api`
4. `curl http://localhost:3000/hello`
    * response: ```{"message": "hello world"}```


