from db import DB_Response
import boto3
from botocore.exceptions import ClientError

def send_notification(type= None, address=None):
    #address is an email address for emails, phone number for sms
    validTypes = ['email', 'sms']


    if type not in validTypes:
        typeErrorMsg =f'{type} is not a valid notification type'
        return DB_Response(
                message=typeErrorMsg, status_code=450, success=False
            )
    

    
    if type == 'email' and address is not None:
        #send email
        pass
    if type == 'sms' and address is not None:
        #send sms
        pass
    

