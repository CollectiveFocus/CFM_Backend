import logging
import json
from re import sub
import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RECIPIENT = "info@collectivefocus.site"
SENDER = "info@collectivefocus.site"


def api_response(status_code, body) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": body,
    }


class SendEmail:

    CHARSET = "UTF-8"

    def __init__(self, client=boto3.client("ses", "us-east-1")):
        self.client = client

    def sendEmail(self, sender, recipient, subject, body) -> int:
        try:
            # Provide the contents of the email.
            response = self.client.send_email(
                Source=sender,
                Destination={
                    "ToAddresses": [recipient],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Data": body,
                        },
                        "Text": {
                            "Charset": SendEmail.CHARSET,
                            "Data": body,
                        },
                    },
                    "Subject": {
                        "Charset": SendEmail.CHARSET,
                        "Data": subject,
                    },
                }
                # we can use a configuationset for logging purposest
                #       maybe we'd want to define the names in a list of constants/enums?
                # ConfigurationSetName=configuration_set,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            return api_response(404, "Unable to send Email. Please try again")
        else:
            messageId = response.get("MessageId", "Not Found")
            logger.info(f"Email sent! Message ID: {messageId}")
            return api_response(
                200, json.dumps({"message": "Succesffully Sent Email!"})
            )


class ContactHandler:
    def extract_body_fields(body):
        body = json.loads(body)
        sender = body.get("name", None)
        senderEmailAddress = body.get("email", None)
        subject = body.get("subject", "No Subject")
        subject = f"FridgeFinder Contact: {subject}."
        message = body.get("message", None)
        if subject and sender:
            subject = f"{subject} From: {sender}"
        return message, subject, sender, senderEmailAddress

    @staticmethod
    def lambda_handler(event: dict, client=boto3.client("ses", "us-east-1")) -> dict:
        body = event.get("body", {})
        if not body:
            return api_response(
                400,
                json.dumps(
                    {"message": "Unable to send Email. Missing Required Fields"}
                ),
            )
        (
            message,
            subject,
            senderName,
            senderEmailAddress,
        ) = ContactHandler.extract_body_fields(body)
        if not senderName or not senderEmailAddress or not message:
            return api_response(
                "400",
                json.dumps(
                    {"message": "Unable to send Email. Missing Required Fields"}
                ),
            )
        response = SendEmail(client).sendEmail(
            SENDER,
            RECIPIENT,
            subject,
            ContactHandler.format_email(senderEmailAddress, message, senderName),
        )
        return response

    @staticmethod
    def format_email(email, body, name):
        return f"From: {name} {email}\r\nMessage: {body}"


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict:
    return ContactHandler.lambda_handler(event)
