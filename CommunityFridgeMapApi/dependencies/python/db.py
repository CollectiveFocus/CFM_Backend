import os
import boto3
import time
from botocore.exceptions import ClientError
import logging
from typing import Tuple
import re
import json
from dataclasses import dataclass
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_ddb_connection(
    env: str = os.getenv("Environment", "")
) -> "botocore.client.DynamoDB":
    ddbclient = ""
    if env == "local":
        ddbclient = boto3.client("dynamodb", endpoint_url="http://dynamodb:8000/")
    else:
        ddbclient = boto3.client("dynamodb")
    return ddbclient


def layer_test() -> str:
    return "hello world"


@dataclass
class Field_Validator:
    is_valid: str
    message: str


class DB_Response:
    def __init__(
        self, success: bool, status_code: int, message: str, json_data: str = None
    ):
        self.message = message
        self.status_code = status_code
        self.success = success
        self.json_data = json_data

    def is_successful(self) -> bool:
        return self.success

    def get_dict_form(self) -> dict:
        return {
            "messsage": self.message,
            "success": self.success,
            "status_code": self.status_code,
            "json_data": self.json_data,
        }

    def api_format(self) -> dict:
        if self.json_data:
            body = self.json_data
        else:
            body = json.dumps({"message": self.message})
        return {
            "statusCode": self.status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": (body),
        }


class DB_Item:

    REQUIRED_FIELDS = []
    ITEM_TYPES = {}
    TABLE_NAME = ""
    FIELD_VALIDATION = {}

    def __init__(self, db_client: "botocore.client.DynamoDB"):
        self.db_client = db_client
        pass

    def add_item(self, conditional_expression=None) -> DB_Response:
        """
        adds item to database
            Parameters:
                conditional_expression (str): conditional expression for boto3 function put_item

            Returns:
                db_response (DB_Response): returns a DB_Response
        """
        field_validation = self.validate_fields()
        if not field_validation.is_valid:
            return DB_Response(
                message=field_validation.message, status_code=400, success=False
            )
        item = self.format_dynamodb_item_v2()
        try:
            if conditional_expression:
                self.db_client.put_item(
                    TableName=self.TABLE_NAME,
                    Item=item,
                    ConditionExpression=conditional_expression,
                )
            else:
                self.db_client.put_item(TableName=self.TABLE_NAME, Item=item)
        except self.db_client.exceptions.ConditionalCheckFailedException as e:
            return DB_Response(
                message=f"{self.TABLE_NAME} already exists, pick a different Name",
                status_code=409,
                success=False,
            )
        except self.db_client.exceptions.ResourceNotFoundException as e:
            message = f"Cannot do operations on a non-existent table: {self.TABLE_NAME}"
            logging.error(message)
            return DB_Response(message=message, status_code=500, success=False)
        except ClientError as e:
            logging.error(e)
            return DB_Response(
                message="Unexpected AWS service exception",
                status_code=500,
                success=False,
            )
        return DB_Response(
            message=f"{self.TABLE_NAME} was succesfully added",
            status_code=201,
            success=True,
        )

    def update_item(self):
        pass

    def get_item(self, primary_key):
        pass

    def delete_item(self):
        pass

    def get_all_items(self):
        """
        Gets all the Fridge Items
        NOTE: This function is probably fine for the fridges in NYC. But as more fridges
        are added to the database, this will be a bottleneck. Ideally we would be querying
        based on proximity. Here is an option for if we ever need to transition:
        https://hometechtime.com/how-to-build-a-dynamodb-geo-database-to-store-and-query-geospatial-data/
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan
        return self.db_client.scan(TableName=self.TABLE_NAME)

    def has_required_fields(self) -> tuple:
        for field in self.REQUIRED_FIELDS:
            if getattr(self, field) is None:
                return (False, field)
        return (True, None)

    def get_class_field_value(self, key: str):
        """
        Gets the class field value based on a key.
        The parameter key can be the class field name or in the case of a dictionary can contain "/"
        "/" is used when a class field is a dictionary and the client wants to get the value of a child field
        Example: location: {geoLng: 23.4323}
                 key = "location/geoLng"
        In order to get the value of geoLng the client would use the key "location/geoLng"
            Parameters:
                key (str): the name of the class field the client wants to obtain the value of

            Returns:
                object_dict (dict): the class field value
        """
        class_field_value = None
        if "/" in key:
            key_split = key.split("/")
            parent_key = key_split[0]
            class_field_value = getattr(self, parent_key)
            for i in range(1, len(key_split)):
                if class_field_value is None:
                    break
                child_key = key_split[i]
                class_field_value = class_field_value.get(child_key, None)
        else:
            class_field_value = getattr(self, key)
        return class_field_value

    def format_dynamodb_item_v2(self):
        """
        Creates a dictionary in the syntax that dynamodb expects
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
        """
        fridge_item = {}
        fridge_json = {}
        for key in self.FIELD_VALIDATION:
            if "/" in key:
                continue
            val = getattr(self, key)
            if val is not None:
                fridge_json[key] = val
                if isinstance(val, int) and not isinstance(val, bool):
                    val = str(val)
                if isinstance(val, dict):
                    val = json.dumps(val)
                elif isinstance(val, list):
                    fridge_json[key] = val.copy()
                    list_type = self.FIELD_VALIDATION[key]["list_type"]
                    val = val.copy()
                    for index, v in enumerate(val):
                        val[index] = {list_type: v}
                fridge_item[key] = {self.FIELD_VALIDATION[key]["type"]: val}
        fridge_item["json_data"] = {"S": json.dumps(fridge_json)}
        return fridge_item

    @staticmethod
    def process_fields(object_dict: dict) -> dict:
        """
        Removes extra white spaces, trailing spaces, leading spaces from object_dict values
        If the length of the field is ZERO after removing the white spaces, sets the value to None
            Parameters:
                object_dict (dict): a dictinary

            Returns:
                object_dict (dict):
        """
        for key, value in object_dict.items():
            if isinstance(value, str):
                object_dict[key] = DB_Item.remove_extra_whitespace(value)
            if isinstance(value, dict):
                object_dict[key] = DB_Item.process_fields(value)
            if isinstance(value, list):
                for index, val in enumerate(value):
                    if isinstance(val, str):
                        value[index] = DB_Item.remove_extra_whitespace(val)
        return object_dict

    @staticmethod
    def remove_extra_whitespace(value: str):
        """
        Removes extra white spaces, trailing spaces, and leading spaces
        Example: Input: " hi    there " Output: "hi there"
            Parameters:
                value (str): a string
            Returns:
                value (str): the value parameter without extra white spaces,
                             trailing spaces, and leading spaces
        """
        value = re.sub(" +", " ", value).strip()
        if len(value) == 0:
            value = None
        return value

    def validate_fields(self) -> Field_Validator:
        """
        Validates that all the fields are valid.
        All fields are valid if they pass all the constraints set in FIELD_VALIDATION
        """
        for key, field_validation in self.FIELD_VALIDATION.items():
            class_field_value = self.get_class_field_value(key)
            is_not_none = class_field_value is not None
            required = field_validation.get("required", None)
            min_length = field_validation.get("min_length", None)
            max_length = field_validation.get("max_length", None)
            choices = field_validation.get("choices", None)
            if required:
                if class_field_value is None:
                    return Field_Validator(
                        is_valid=False, message=f"Missing Required Field: {key}"
                    )
            if min_length and is_not_none:
                if len(str(class_field_value)) < min_length:
                    return Field_Validator(
                        is_valid=False,
                        message=f"{key} character length must be >= {min_length}",
                    )
            if max_length and is_not_none:
                if len(str(class_field_value)) > max_length:
                    return Field_Validator(
                        is_valid=False,
                        message=f"{key} character length must be <= {max_length}",
                    )
            if choices and is_not_none:
                if class_field_value not in choices:
                    return Field_Validator(
                        is_valid=False,
                        message=f"{key} must to be one of: {str(choices)}",
                    )
        return Field_Validator(
            is_valid=True, message="All Fields Were Successfully Validated"
        )


class Fridge(DB_Item):
    MIN_ID_LENGTH = 3
    MAX_ID_LENGTH = 32
    FIELD_VALIDATION = {
        "id": {
            "required": True,
            "min_length": MIN_ID_LENGTH,
            "max_length": MAX_ID_LENGTH,
            "type": "S",
        },
        "name": {
            "required": True,
            "min_length": MIN_ID_LENGTH,
            "max_length": 50,
            "type": "S",
        },
        "tags": {"required": False, "type": "L", "list_type": "S"},
        "location": {"required": True, "type": "S"},
        "location/street": {"required": False, "max_length": 256},
        "location/city": {"required": False, "max_length": 256},
        "location/state": {"required": False, "max_length": 256},
        "location/zip": {"required": False, "max_length": 10},
        "location/geoLat": {"required": True, "max_length": 20},
        "location/geoLng": {"required": True, "max_length": 20},
        "maintainer": {"required": False, "type": "S"},
        "maintainer/name": {"required": False, "max_length": 256},
        "maintainer/organization": {"required": False, "max_length": 256},
        "maintainer/phone": {"required": False, "min_length": 10, "max_length": 12},
        "maintainer/email": {"required": False, "max_length": 320},
        "maintainer/website": {"required": False, "max_length": 2048},
        "maintainer/instagram": {"required": False, "max_length": 64},
        "notes": {"required": False, "max_length": 280, "type": "S"},
        "food_accepts": {"required": False, "type": "L", "list_type": "S"},
        "food_restrictions": {"required": False, "type": "L", "list_type": "S"},
        "photoURL": {
            "required": False,
            "max_length": 2048,
            "type": "S",
        },
        "last_edited": {"required": False, "type": "N", "max_length": 20},
        "verified": {"required": False, "type": "B"},
        "latestFridgeReport": {"required": False, "type": "S"},
        "latestFridgeReport/epochTimestamp": {"required": False},
        "latestFridgeReport/timestamp": {"required": False},
        "latestFridgeReport/condition": {"required": False},
        "latestFridgeReport/foodPercentage": {"required": False},
        "latestFridgeReport/photoURL": {"required": False},
        "latestFridgeReport/notes": {"required": False},
    }
    TABLE_NAME = "fridge"
    FOOD_ACCEPTS = []  # TODO: Fill this in
    FOOD_RESTRICTIONS = []  # TODO: fill this in

    def __init__(self, db_client: "botocore.client.DynamoDB", fridge: dict = None):
        super().__init__(db_client=db_client)
        if fridge is not None:
            fridge = DB_Item.process_fields(fridge)
            self.id: str = fridge.get("id", None)
            self.name: str = fridge.get(
                "name", None
            )  # name must be alphanumeric and can contain spaces
            self.tags: list = fridge.get("tags", None)
            self.location: dict = fridge.get("location", None)
            self.maintainer: dict = fridge.get("maintainer", None)
            self.notes: str = fridge.get("notes", None)
            self.food_accepts: list = fridge.get("food_accepts", None)
            self.food_restrictions: list = fridge.get("food_restrictions", None)
            self.photoURL: str = fridge.get("photoURL", None)
            self.last_edited: str = fridge.get("last_edited", None)
            self.latestFridgeReport: dict = fridge.get("latestFridgeReport", None)
            self.verified: bool = fridge.get("verified", None)

    def get_item(self, fridgeId):
        is_valid, message = Fridge.is_valid_id(fridgeId=fridgeId)
        if not is_valid:
            return DB_Response(success=False, status_code=400, message=message)
        key = {"id": {"S": fridgeId}}
        result = self.db_client.get_item(TableName=self.TABLE_NAME, Key=key)
        if "Item" not in result:
            return DB_Response(
                success=False, status_code=404, message="Fridge was not found"
            )
        else:
            json_data = result["Item"]["json_data"]["S"]
            return DB_Response(
                success=True,
                status_code=200,
                message="Successfully Found Fridge",
                json_data=json_data,
            )

    def get_items(self, tag=None):
        # scan/query doc: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#querying-and-scanning
        response = None
        if tag:
            response = self.db_client.scan(
                TableName=self.TABLE_NAME,
                FilterExpression="contains (tags, :tag)",
                ExpressionAttributeValues={":tag": {"S": tag}},
                ProjectionExpression="json_data",
            )
        else:
            response = self.db_client.scan(
                TableName=self.TABLE_NAME, ProjectionExpression="json_data"
            )
        json_data_list = [item["json_data"]["S"] for item in response["Items"]]
        # Converts list of json to json.
        json_response = f"[{','.join(json_data_list)}]"
        return DB_Response(
            success=True,
            status_code=200,
            message="Query Successfully Completed",
            json_data=json_response,
        )

    def add_items(self):
        pass

    def set_id(self):
        """
        Sets the Fridge id. Fridge id is the Fridge name with no spaces and all lower cased
        """
        id = self.name.lower().replace(" ", "")
        self.id = id

    def is_valid_name(self) -> bool:
        """
        Checks if a Fridge name is valid. A valid name is alphanumric and can contain spaces
            Returns:
                bool (bool):
        """
        id = self.name.lower().replace(" ", "")
        return id.isalnum()

    def validate_fields(self) -> Field_Validator:
        """
        Validates that all the fields are valid.
        All fields are valid if they pass all the constraints set in FIELD_VALIDATION
        """
        field_validator = super().validate_fields()
        if not field_validator.is_valid:
            return field_validator
        if not self.is_valid_name():
            return Field_Validator(
                message="Name Can Only Contain Letters, Numbers, and Spaces",
                is_valid=False,
            )
        return field_validator

    @staticmethod
    def is_valid_id(fridgeId: str) -> tuple[bool, str]:
        """
        Checks if the fridge is id valid. A valid fridge id is alphanumeric and
        must have character length >= 3 and <= 32
        """
        if fridgeId is None:
            return False, "Missing Required Field: id"
        if not fridgeId.isalnum():
            return False, "id Must Be Alphanumeric"
        id_length = len(fridgeId)
        is_valid_id_length = Fridge.MIN_ID_LENGTH <= id_length <= Fridge.MAX_ID_LENGTH
        if not is_valid_id_length:
            return (
                False,
                f"id Must Have A Character Length >= {Fridge.MIN_ID_LENGTH} and <= {Fridge.MAX_ID_LENGTH}",
            )
        return True, "success"

    def set_last_edited(self):
        """
        Sets last_edited to the current epoch time. Timezone defaults to UTC
        """
        self.last_edited = str(int(time.time()))

    def add_item(self, conditional_expression=None) -> DB_Response:
        """
        Adds a fridge item to the database
        """
        self.set_id()
        self.set_last_edited()
        conditional_expression = "attribute_not_exists(id)"
        return super().add_item(conditional_expression=conditional_expression)

    def get_fridge_locations(self):
        pass

    def update_fridge_report(self, fridgeId: str, fridge_report: dict) -> DB_Response:
        """
        Updates latestFridgeReport field with new Fridge Report.
        This function is called when a new FridgeReport is added to the database
        """
        db_reponse = self.get_item(fridgeId=fridgeId)
        if not db_reponse.is_successful():
            # Fridge was not found
            return db_reponse
        fridge_dict = json.loads(db_reponse.json_data)
        fridge_dict["latestFridgeReport"] = fridge_report
        fridge_json_data = json.dumps(fridge_dict)
        latestFridgeReport = json.dumps(fridge_report)
        """
        JD and #LFR are mapped to the values set in ExpressionAttributeNames
        :fj and :fr are mapped to the values set in ExpressionAttributeValues
        UpdateExpression becomes: "json_data":  {"S": fridge_json_data}, "latestFridgeReport": {"S": latestFridgeReport}
        """
        self.db_client.update_item(
            TableName=self.TABLE_NAME,
            Key={"id": {"S": fridgeId}},
            ExpressionAttributeNames={"#LFR": "latestFridgeReport", "#JD": "json_data"},
            ExpressionAttributeValues={
                ":fr": {"S": latestFridgeReport},
                ":fj": {"S": fridge_json_data},
            },
            UpdateExpression="SET #JD = :fj, #LFR = :fr",
        )
        return DB_Response(
            success=True, status_code=201, message="fridge_report was succesfully added"
        )


class FridgeReport(DB_Item):
    TABLE_NAME = "fridge_report"
    VALID_CONDITIONS = {
        "working",
        "needs cleaning",
        "needs servicing",
        "not at location",
    }
    VALID_FOOD_PERCENTAGE = {0, 33, 67, 100}
    FIELD_VALIDATION = {
        "notes": {"required": False, "max_length": 256, "type": "S"},
        "fridgeId": {
            "required": True,
            "min_length": Fridge.MIN_ID_LENGTH,
            "max_length": Fridge.MAX_ID_LENGTH,
            "type": "S",
        },
        "photoURL": {
            "required": False,
            "max_length": 2048,
            "type": "S",
        },
        "epochTimestamp": {"required": False, "type": "N"},
        "timestamp": {"required": False, "type": "S"},
        "condition": {"required": True, "type": "S", "choices": VALID_CONDITIONS},
        "foodPercentage": {
            "required": True,
            "type": "N",
            "choices": VALID_FOOD_PERCENTAGE,
        },
    }

    def __init__(
        self, db_client: "botocore.client.DynamoDB", fridge_report: dict = None
    ):
        super().__init__(db_client=db_client)
        if fridge_report is not None:
            fridge_report = self.process_fields(fridge_report)
            self.notes: str = fridge_report.get("notes", None)
            self.condition: str = fridge_report.get("condition", None)
            self.photoURL: str = fridge_report.get("photoURL", None)
            self.fridgeId: str = fridge_report.get("fridgeId", None)
            self.foodPercentage: int = fridge_report.get("foodPercentage", None)
            # timestamp and epochTimestamp have the same time but in different formats
            self.timestamp: str = fridge_report.get(
                "timestamp", None
            )  # ISO formatted timestamp for api clients
            self.epochTimestamp: str = fridge_report.get(
                "epochTimestamp", None
            )  # Epoch timestamp for querying

    def set_timestamp(self):
        """
        Sets epochTimestamp and timestamp fields
        timestamp is ISO formatted date/time and is what the API user will use
        epochTimestamp will be what is used to query the database
        """
        self.epochTimestamp = str(int(time.time()))
        utc_time = datetime.datetime.utcnow()
        self.timestamp = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def object_to_dict(self):
        """
        Converts object into a dictionary
        """
        object_dict = {}
        for key in self.FIELD_VALIDATION:
            val = getattr(self, key)
            if val is not None:
                object_dict[key] = val
        return object_dict

    def add_item(self) -> DB_Response:
        self.set_timestamp()
        fridge_report_dict = self.object_to_dict()
        db_response = super().add_item()
        if not db_response.is_successful():
            return db_response
        return Fridge(db_client=self.db_client).update_fridge_report(
            fridgeId=self.fridgeId, fridge_report=fridge_report_dict
        )


class FridgeHistory(DB_Item):
    def __init__(self, db_client: "botocore.client.DynamoDB"):
        super().__init__(db_client=db_client)


class Tag(DB_Item):
    REQUIRED_FIELDS = ["tag_name"]
    TABLE_NAME = "tag"
    # Tag Class constants
    MIN_TAG_LENGTH = 3
    MAX_TAG_LENGTH = 32

    def __init__(self, db_client: "botocore.client.DynamoDB", tag_name: str = None):
        super().__init__(db_client=db_client)
        self.tag_name = self.format_tag(tag_name)

    def format_tag(self, tag_name: str) -> str:
        # tag_name is alphanumeric, all lowercased, may include hyphen and underscore but no spaces.
        if tag_name:
            tag_name = tag_name.lower().replace(" ", "")
        return tag_name

    @staticmethod
    def is_valid_tag_name(tag_name: str) -> Tuple[bool, str]:
        # valid tag name is alphanumeric, all lowercased, may include hyphen and underscore but no spaces.
        if tag_name is None:
            message = "Missing required fields: tag_name"
            return False, message
        length_tag_name = len(tag_name)
        is_tag_length_valid = (
            length_tag_name >= Tag.MIN_TAG_LENGTH
            and length_tag_name <= Tag.MAX_TAG_LENGTH
        )
        if tag_name and is_tag_length_valid:
            for x in tag_name:
                if not x.isalnum() and x not in ["_", "-"]:
                    message = "tag_name contains invalid characters"
                    return False, message
            message = ""
            return True, message
        else:
            message = f"Length of tag_name is {length_tag_name}. It should be >= {Tag.MIN_TAG_LENGTH} but <= {Tag.MAX_TAG_LENGTH}."
            return False, message

    def add_item(self) -> DB_Response:
        has_required_fields, field = self.has_required_fields()
        if not has_required_fields:
            return DB_Response(
                message=f"Missing Required Field: {field}",
                status_code=400,
                success=False,
            )
        is_valid_field = self.is_valid_tag_name(self.tag_name)
        if not is_valid_field:
            return DB_Response(
                message=f"Tag Name Can Only Contain Letters, Numbers, Hyphens and Underscore: {self.tag_name}",
                status_code=400,
                success=False,
            )
        item = {"tag_name": {"S": self.tag_name}}

        try:
            self.db_client.put_item(TableName=self.TABLE_NAME, Item=item)
        except self.db_client.exceptions.ResourceNotFoundException as e:
            message = f"Cannot do operations on a non-existent table: {Tag.TABLE_NAME}"
            logging.error(message)
            return DB_Response(message=message, status_code=500, success=False)
        except ClientError as e:
            logging.error(e)
            return DB_Response(
                message="Unexpected AWS service exception",
                status_code=500,
                success=False,
            )
        return DB_Response(
            message="Tag was succesfully added", status_code=200, success=True
        )
