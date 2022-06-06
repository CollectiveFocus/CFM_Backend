from email import message
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

class DB_Response:

    def __init__(self, success: bool, status_code: int, message: str, db_items: list = None):
        self.message = message
        self.status_code = status_code
        self.success = success
        self.db_items = db_items

    def is_successful(self) -> bool:
        return self.success
    
    def get_dict_form(self) -> dict:
        return {'messsage': self.message, 'success': self.success, 'status_code': self.status_code, 'db_item': self.db_items}

class DB_Item:

    REQUIRED_FIELDS = []
    ITEM_TYPES = {}
    TABLE_NAME = ""
    def __init__(self, db_client: 'botocore.client.DynamoDB'):
        self.db_client = db_client
        pass

    def add_item(self):
        pass

    def update_item(self):
        pass

    def get_item(self):
        pass

    def delete_item(self):
        pass

    def get_all_items(self):
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan
        return self.db_client.scan(TableName=self.TABLE_NAME)

    def has_required_fields(self) -> tuple:
        for field in self.REQUIRED_FIELDS:
            if getattr(self, field) is None:
                return (False, field)
        return (True, None)
    
    def format_dynamodb_item(self):
        #generates a dictionary in the format dynamodb expects
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
        fridge_item = {}
        for key in self.ITEM_TYPES:
            val = getattr(self, key)
            if val is not None:
                fridge_item[key] = {self.ITEM_TYPES[key]: val}
        return fridge_item

class Fridge(DB_Item):    
    REQUIRED_FIELDS = ['display_name', 'fridge_state', 'address', 'lat', 'long']
    TABLE_NAME = "fridge"
    STATES ={'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'}
    FOOD_ACCEPTS = []#TODO: Fill this in
    FOOD_RESTRICTIONS = []#TODO: fill this in
    ITEM_TYPES = {
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

    def __init__(self, db_client: 'botocore.client.DynamoDB', fridge: dict=None):
        super().__init__(db_client=db_client)
        self.db_client = db_client
        if fridge is not None:
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
            if self.fridge_state is not None:
                self.fridge_state = self.fridge_state.upper()

    def is_valid_fridge_state(self) -> bool:
        return self.fridge_state in self.STATES

    def get_item(self):
        pass

    def get_items(self):
        pass

    def add_items(self):
        pass
    
    def set_username(self):
        #Fridge username is the display_name with no spaces and all lower cased
        username = self.display_name.lower().replace(" ", "")
        self.username = username

    def is_valid_display_name(self) -> bool:
        #A valid display_name is alphanumric and can contain spaces
        username = self.display_name.lower().replace(" ", "")
        return username.isalnum()

    def add_item(self) -> DB_Response:
        has_required_fields, field = self.has_required_fields()
        if not has_required_fields:
            return DB_Response(message = "Missing Required Field: %s" % field, status_code=400, success=False)
        if not self.is_valid_fridge_state():
            return DB_Response(message="Invalid State Given: %s" % self.fridge_state, status_code=400, success=False)
        if not self.is_valid_display_name():
            return DB_Response(message="Display Name Can Only Contain Letters, Numbers, and Spaces", status_code=400, success=False)
        self.set_username()
        item = self.format_dynamodb_item()
        conditional_expression = 'attribute_not_exists(fridge_state) AND attribute_not_exists(username)'
        try:
            self.db_client.put_item(
                TableName=self.TABLE_NAME,
                Item=item,
                ConditionExpression=conditional_expression
            )
        except self.db_client.exceptions.ConditionalCheckFailedException:
            return DB_Response(message="Fridge already exists, pick a different name", status_code=409, success=False)
        return DB_Response(message="Fridge was succesfully added", status_code=200, success=True)

    def get_fridge_locations(self):
        pass


class FrigeCheckIn(DB_Item):

    def __init__(self, db_client: 'botocore.client.DynamoDB'):
        super().__init__(db_client=db_client)

class FridgeHistory(DB_Item):
    
    def __init__(self, db_client: 'botocore.client.DynamoDB'):
        super().__init__(db_client=db_client)

class Tag(DB_Item):

    def __init__(self, db_client: 'botocore.client.DynamoDB'):
        super().__init__(db_client=db_client)

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