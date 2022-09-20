import logging
import json

from send_email import sendEmail

logger = logging.getLogger()
logger.setLevel(logging.INFO)

recipient = "info@collectivefocus.site"


class ContactUs:
    @staticmethod
    def lambda_handler(event: dict) -> dict:
        body = event.get("body", {})
        if not body:
            return {"statusCode": 400}
        body = json.loads(body)
        sender = body.get("name", None)
        senderAddress = body.get("email", None)
        subject = body.get("subject", "no subject")
        message = body.get("message", None)

        if not sender or not senderAddress or not message:
            raise ValueError('missing required field to send email')

        subject = subject + " from: " + sender

        responseCode = sendEmail(senderAddress, recipient, subject, message)

        return {"statusCode": responseCode}


def lambda_handler(
    event: dict, context: "awslambdaric.lambda_context.LambdaContext"
) -> dict: return ContactUs.lambda_handler(event)
