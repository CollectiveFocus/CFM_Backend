from db import DB_Response
import re
import boto3
from botocore.exceptions import ClientError


def send_sms(phone_number=None, message=None):
    
    sns = boto3.client(
        "sns",
        region_name="us-east-1"
    )
    if(not is_valid_phone_number(phone_number)):
        return

    response = sns.publish(
        PhoneNumber=phone_number,
        Message = message
    )
    return response

def is_valid_phone_number(phone_number):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return bool(pattern.match(phone_number))
