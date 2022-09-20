import logging
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ses', "us-east-1")

CHARSET = "UTF-8"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def sendEmail(sender, recipient, subject, body) -> int:
    #   Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [
                    recipient
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Data': body,
                    },
                    'Text': {
                        'Data': body,
                    },
                },
                'Subject': {
                    'Data': subject,
                },
            }
            # we can use a configuationset for logging purposest
            #       maybe we'd want to define the names in a list of constants/enums?
            # ConfigurationSetName=configuration_set,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return 404
    else:
        logger.info("Email sent! Message ID:" + response['MessageId'])
        logger.info(response["ResponseMetadata"]["HTTPStatusCode"])
        return response["ResponseMetadata"]["HTTPStatusCode"]
