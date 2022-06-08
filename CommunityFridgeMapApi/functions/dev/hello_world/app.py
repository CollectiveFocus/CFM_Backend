import json
try:
    from db import layer_test
except:
    from dependencies.python.db import layer_test
    #If it gets here it's because we are performing a unit test. It's a common error when using lambda layers
    #Here is an example of someone having a similar issue:
    #https://stackoverflow.com/questions/69592094/pytest-failing-in-aws-sam-project-due-to-modulenotfounderror

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    return {                                                                                                                                                                                                                                                                                                                                                                                                                                      
        "statusCode": 200,
        "body": json.dumps({
            "message": layer_test(),
        }),
    }
