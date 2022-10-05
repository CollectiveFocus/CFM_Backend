import os
import boto3
import time

def get_ddb_connection(env:str=os.getenv('Environment', '')) -> 'botocore.client.DynamoDB':
    ddbclient=''
    if env == 'local':
        ddbclient = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000/')
    else:
        ddbclient = boto3.client('dynamodb')
    return ddbclient

def layer_test() -> str:
    return "hello world"

class Fridge:    
    REQUIRED_FIELDS = ['display_name', 'fridge_state', 'address', 'lat', 'long']
    TABLE_NAME = "fridge"
    STATES ={'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'}
    FOOD_ACCEPTS = []#TODO: Fill this in
    FOOD_RESTRICTIONS = []#TODO: fill this in
    FRIDGE_TYPES = {
        'display_name': 'S',
        'username': 'S',
        'fridge_state': 'S',
        'address': 'S',
        'instagram': 'S',
        'info': 'S',
        'url': 'S',
        'neighborhood': 'S',
        'organizer_email': 'S',
        'tags': 'L',
        'food_accepts': 'L',
        'food_restrictions': 'L',
        'lat': 'S',
        'long': 'S',
        'last_editted': 'N',
        'profile_image': 'S',
        'check_in_time': 'S',
        'check_in_notes': 'S',
        'check_in_status': 'S',
        'check_in_image': 'S'
    }

    def __init__(self, db_client, fridge: dict={}):
        self.display_name:str = fridge.get('display_name', None) #display_name must be alphanumeric (spaces are fine)
        self.username:str = fridge.get('username', None)
        self.fridge_state:str = fridge.get('fridge_state', None)
        self.address:str = fridge.get('address', None)
        self.instagram:str = fridge.get('instagram', None)
        self.info:str = fridge.get('info', None)
        self.url:str = fridge.get('url', None)
        self.neighborhood:str = fridge.get('neighborhood', None)
        self.organizer_email:str = fridge.get('organizer_email', None)
        self.tags:list = fridge.get('tags', None)
        self.food_accepts:list = fridge.get('food_accepts', None)
        self.food_restrictions:list = fridge.get('food_restrictions', None)
        self.lat:str = fridge.get('lat', None)
        self.long:str = fridge.get('long', None)
        self.profile_image:str = fridge.get('profile_image', None)
        self.last_editted:int = fridge.get('last_editted', None)
        self.check_in_time:int = fridge.get('check_in_time', None)
        self.check_in_notes:str = fridge.get('check_in_notes', None)
        self.check_in_status:str = fridge.get('check_in_status', None)
        self.check_in_image:str = fridge.get('check_in_image', None)
        self.db_client = db_client
        if self.fridge_state is not None:
            self.fridge_state = self.fridge_state.upper()

    def has_required_fields(self) -> bool:
        for field in self.REQUIRED_FIELDS:
            if getattr(self, field) is None:
                raise RequiredFieldMissingException(object_name='fridge', field=field)
        return True

    def is_valid_fridge_state(self) -> bool:
        if self.fridge_state not in self.STATES:
            raise InvalidStateException(fridge_state=self.fridge_state)
        return True

    def get_fridge(db_client):
        pass

    def get_fridges(db_client):
        pass

    def add_fridges(db_client):
        pass
    
    def set_username(self):
        #Fridge username is the display_name with no spaces and all lower cased
        username = self.display_name.lower().replace(" ", "")
        if not username.isalnum():
            raise InvalidDisplayNameException(username)
        self.username = username


    def build_fridge_item(self):
        #generates a dictionary in the format dynamodb expects
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
        fridge_item = {}
        for key in self.FRIDGE_TYPES:
            val = getattr(self, key)
            if val is not None:
                fridge_item[key] = {self.FRIDGE_TYPES[key]: val}
        return fridge_item


    def add_fridge(self):
        self.has_required_fields()
        self.is_valid_fridge_state()
        self.set_username()
        item = self.build_fridge_item()
        conditional_expression = 'attribute_not_exists(fridge_state) AND attribute_not_exists(username)'
        response  = self.db_client.put_item(
            TableName=self.TABLE_NAME,
            Item=item,
            ConditionExpression=conditional_expression
        )
        return response

    def get_fridge_locations(db_client):
        pass

    def get_all_fridges(db_client):
        return db_client.scan(TableName=Fridge.TABLE_NAME)


class FrigeCheckIn:

    def __init__(self):
        pass

class FridgeHistory:
    
    def __init__(self):
        pass

class Tag:

    def __init__(self):
        pass

class RequiredFieldMissingException(Exception):
    def __init__(self, object_name, field):
        self.field = field
        self.object_name = object_name

    def __str__(self):
        return "<Missing Required Field: %s. For Object: %s>" % (self.field, self.object_name)

class InvalidStateException(Exception):
    def __init__(self, fridge_state):
        self.state = fridge_state
    
    def __str__(self):
        return "<Invalid State Given: %s>" % (self.fridge_state)

class InvalidDisplayNameException(Exception):
    def __init__(self, username):
        self.username = username
    
    def __str__(self):
        return "<Display Name Must Be Alphanumeric: %s>" % (self.username)