# CFM_Backend

## Setup

1. Install AWS SAM CLI
    * https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html


## Build and Test Locally

Confirm that the following requests work for you

1. `cd CommunityFridgeMapApi/`
2. `CommunityFridgeMapApi$ sam build --use-container`
3. `sam local invoke HelloWorldFunction --event events/event.json`
    * response: ```{"statusCode": 200, "body": "{\"message\": \"hello world\"}"}```
4. `sam local start-api`
5. `curl http://localhost:3000/hello`
    * response: ```{"message": "hello world"}```


