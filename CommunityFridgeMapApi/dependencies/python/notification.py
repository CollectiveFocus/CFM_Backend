from db import DB_Response
import re
import boto3
from botocore.exceptions import ClientError

#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses/client/send_email.html

# def sendNotification(message, userId, lastNotified, email, phoneNumber):


def send_sms(phone_number:str=None, message:str=None, region:str='us-east-1'):

    sns = boto3.client(
        "sns",
        region_name=region
    )
    if(not is_valid_phone_number(phone_number)):
        return

    try: #Tries to send an sms, returns an error if unsuccessful
        [MessageId, SequenceNumber]  = sns.publish( #SNS.publish returns a unique message ID identifier and 
            PhoneNumber=phone_number,
            Message = message
        )

        if MessageId: response = {'Sent': True, 
                                  'Error': None, 
                                  'MessageId': MessageId, 
                                  'SequenceNumber': SequenceNumber}
    except Exception as e:
        response = {'Sent': False, 
                    'Error': e, 
                    'MessageId': None, 
                    'SequenceNumber': None}

    return response


def send_email(
    sender_email:str=None, to_addresses:list=None, cc_addresses:list=None, bcc_addresses:list=None,
    subject:str=None, message:str=None, html_data:str=None, reply_to_addresses:list=None):

    client = boto3.client('ses')

    Source = sender_email

    Destination = {
            'ToAddresses': to_addresses,
            'CcAddresses': cc_addresses,
            'BccAddresses': bcc_addresses
            }

    Message= {
            'Subject:': {
                'Data': subject,
                'Charset': 'UTF-8',
                },
            'Body': {
                'Text': {
                    'Data': message,
                    'Charset': 'UTF-8'
                    },
                'Html':{
                    'Data': html_data,
                    'Charset': 'UTF-8',

                    }
                }
            }
    ReplyToAddresses = reply_to_addresses
    ReturnPath = ''  #This is the email address that is addressed when emails fail
    SourceArn = '' #Something about authorization, See docs  
    ReturnPathArn = '' #Same thing, something about authorization

    try:    #Tries to send an email, returns an error if unsuccessful

        MessageId = client.send_email(
                    Source, Destination, Message, ReplyToAddresses, ReturnPath, SourceArn, ReturnPathArn)
        
        response = {'Sent': True, 
                    'Error': None, 
                    'MessageId': MessageId, 
                    'SequenceNumber': None}
    
    except Exception as e:
        response = {'Sent': False, 
                    'Error': e, 
                    'MessageId': None, 
                    'SequenceNumber': None}
        
    return response


def is_valid_phone_number(phone_number):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return bool(pattern.match(phone_number))
