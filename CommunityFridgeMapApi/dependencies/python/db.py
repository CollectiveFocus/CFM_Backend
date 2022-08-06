import os
import boto3
import time
from botocore.exceptions import ClientError
import logging
from typing import Tuple
import re
import json

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


class Field_Validator:
    def __init__(self, success, message):
        self.success = success
        self.message = message

    def get_message(self):
        """
        Gets message field
        """
        return self.message

    def is_valid(self):
        """
        Gets success field
        """
        return self.success


class DB_Response:
    def __init__(
        self, success: bool, status_code: int, message: str, db_items: list = None
    ):
        self.message = message
        self.status_code = status_code
        self.success = success
        self.db_items = db_items

    def is_successful(self) -> bool:
        return self.success

    def get_dict_form(self) -> dict:
        return {
            "messsage": self.message,
            "success": self.success,
            "status_code": self.status_code,
            "db_item": self.db_items,
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
        if not field_validation.is_valid():
            return DB_Response(
                message=field_validation.get_message(), status_code=400, success=False
            )
        item = self.format_dynamodb_item_v2()
        try:
            self.db_client.put_item(
                TableName=self.TABLE_NAME,
                Item=item,
                ConditionExpression=conditional_expression,
            )
        except self.db_client.exceptions.ConditionalCheckFailedException as e:
            return DB_Response(
                message=f"{self.TABLE_NAME} already exists, pick a different Name",
                status_code=409,
                success=False,
            )
        except self.db_client.exceptions.ResourceNotFoundException as e:
            message = (
                "Cannot do operations on a non-existent table:  %s" % self.TABLE_NAME
            )
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
            status_code=200,
            success=True,
        )

    def update_item(self):
        pass

    def get_item(self):
        pass

    def delete_item(self):
        pass

    def get_all_items(self):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan
        return self.db_client.scan(TableName=self.TABLE_NAME)

    def has_required_fields(self) -> tuple:
        for field in self.REQUIRED_FIELDS:
            if getattr(self, field) is None:
                return (False, field)
        return (True, None)

    def format_dynamodb_item(self):
        # generates a dictionary in the format dynamodb expects
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
        fridge_item = {}
        for key in self.ITEM_TYPES:
            val = getattr(self, key)
            if val is not None:
                fridge_item[key] = {self.ITEM_TYPES[key]: val}
        return fridge_item

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

    # TODO: deprecate format_dynamodb_item in favor of format_dynamodb_item_v2
    def format_dynamodb_item_v2(self):
        """
        Creates a dictionary in the syntax that dynamodb expects
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
        """
        fridge_item = {}
        for key in self.FIELD_VALIDATION:
            if "/" in key:
                continue
            val = getattr(self, key)
            if val is not None:
                if type(val) == dict:
                    val = json.dumps(val)
                fridge_item[key] = {self.FIELD_VALIDATION[key]["type"]: val}
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
            if type(value) == str:
                object_dict[key] = DB_Item.remove_whitespace(value)
            if type(value) == dict:
                object_dict[key] = DB_Item.process_fields(value)
            if type(value) == list:
                for index, val in enumerate(value):
                    if type(val) == str:
                        value[index] = DB_Item.remove_whitespace(val)
        return object_dict

    @staticmethod
    def remove_whitespace(value: str):
        """
        Removes extra white spaces, trailing spaces, and leading spaces
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
            if required:
                if class_field_value is None:
                    return Field_Validator(
                        success=False, message=f"Missing Required Field: {key}"
                    )
            if min_length and is_not_none:
                if len(str(class_field_value)) < min_length:
                    return Field_Validator(
                        success=False,
                        message=f"{key} character length must be >= {min_length}",
                    )
            if max_length and is_not_none:
                if len(str(class_field_value)) > max_length:
                    return Field_Validator(
                        success=False,
                        message=f"{key} character length must be <= {max_length}",
                    )
        return Field_Validator(
            success=True, message="All Fields Were Successfully Validated"
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
        "tags": {"required": False, "type": "L"},
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
        "food_accepts": {"required": False, "type": "L"},
        "food_restrictions": {"required": False, "type": "L"},
        "photoURL": {
            "required": False,
            "max_length": 2048,
            "type": "S",
        },
        "last_edited": {"required": False, "type": "N", "max_length": 20},
        "verified": {"required": False, "type": "B"},
        "latest_report": {"required": False, "type": "S"},
        "latest_report/timestamp": {"required": False},
        "latest_report/condition": {"required": False},
        "latest_report/foodPercentage": {"required": False},
        "latest_report/foodPhotoURL": {"required": False},
        "latest_report/notes": {"required": False},
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
            self.latest_report: dict = fridge.get("latest_report", None)
            self.verified: bool = fridge.get("verified", None)

    def get_item(self):
        pass

    def get_items(self):
        pass

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
        if not field_validator.is_valid():
            return field_validator
        if not self.is_valid_name():
            return Field_Validator(
                message="Name Can Only Contain Letters, Numbers, and Spaces",
                success=False,
            )
        return field_validator

    @staticmethod
    def is_valid_id(fridge_id: str) -> tuple[bool, str]:
        """
        Checks if the fridge is id valid. A valid fridge id is alphanumeric and
        must have character length >= 3 and <= 32
        """
        if fridge_id is None:
            return False, "Missing Required Field: id"
        if not fridge_id.isalnum():
            return False, "id Must Be Alphanumeric"
        id_length = len(fridge_id)
        is_valid_id_length = (
            id_length >= Fridge.MIN_ID_LENGTH and id_length <= Fridge.MAX_ID_LENGTH
        )
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


class FridgeReport(DB_Item):

    REQUIRED_FIELDS = ["fridge_id", "status", "fridge_percentage"]
    ITEM_TYPES = {
        "notes": "S",
        "fridge_id": "S",
        "image_url": "S",
        "timestamp": "N",
        "status": "S",
        "fridge_percentage": "S",
    }
    TABLE_NAME = "fridge_report"
    VALID_STATUS = {"working", "needs cleaning", "needs servicing", "not at location"}
    VALID_FRIDGE_PERCENTAGE = {"0", "33", "67", "100"}
    MAX_NOTES_LENGTH = 256

    def __init__(
        self, db_client: "botocore.client.DynamoDB", fridge_report: dict = None
    ):
        super().__init__(db_client=db_client)
        if fridge_report is not None:
            self.set_notes(fridge_report.get("notes", None))
            self.status: str = fridge_report.get("status", None)
            self.image_url: str = fridge_report.get("image_url", None)
            self.fridge_id: str = fridge_report.get("fridge_id", None)
            self.fridge_percentage: int = fridge_report.get("fridge_percentage", None)

    def set_timestamp(self):
        self.timestamp = str(int(time.time()))

    def set_notes(self, notes: str):
        """
        Notes is optional. If Notes is an empty string then set to None
        """
        if notes is None:
            self.notes = None
            return
        if len(notes) == 0:
            self.notes = None
        else:
            self.notes = notes

    @staticmethod
    def is_valid_notes(notes: str) -> bool:
        return notes is None or len(notes) <= FridgeReport.MAX_NOTES_LENGTH

    @staticmethod
    def is_valid_status(status: str) -> bool:
        return status in FridgeReport.VALID_STATUS

    @staticmethod
    def is_valid_fridge_percentage(fridge_percentage: str) -> bool:
        return fridge_percentage in FridgeReport.VALID_FRIDGE_PERCENTAGE

    def add_item(self) -> DB_Response:
        has_required_fields, missing_field = self.has_required_fields()
        if not has_required_fields:
            return DB_Response(
                message=f"Missing Required Field: {missing_field}",
                status_code=400,
                success=False,
            )
        is_valid_id, is_valid_id_message = Fridge.is_valid_id(self.fridge_id)
        if not is_valid_id:
            return DB_Response(
                message=is_valid_id_message, status_code=400, success=False
            )
        if not FridgeReport.is_valid_status(self.status):
            return DB_Response(
                message=f"Invalid Status, must to be one of: {str(self.VALID_STATUS)}",
                status_code=400,
                success=False,
            )
        if not FridgeReport.is_valid_fridge_percentage(self.fridge_percentage):
            return DB_Response(
                message=f"Invalid Fridge percentage, must to be one of: {str(self.VALID_FRIDGE_PERCENTAGE)}",
                status_code=400,
                success=False,
            )
        if not FridgeReport.is_valid_notes(self.notes):
            return DB_Response(
                message=f"Notes character length must be <= {self.MAX_NOTES_LENGTH}",
                status_code=400,
                success=False,
            )
        self.set_timestamp()
        item = self.format_dynamodb_item()
        try:
            self.db_client.put_item(TableName=self.TABLE_NAME, Item=item)
        except self.db_client.exceptions.ResourceNotFoundException as e:
            message = (
                "Cannot do operations on a non-existent table:  %s" % Fridge.TABLE_NAME
            )
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
            message="Fridge Report was succesfully added", status_code=200, success=True
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
                message="Missing Required Field: %s" % field,
                status_code=400,
                success=False,
            )
        is_valid_field = self.is_valid_tag_name(self.tag_name)
        if not is_valid_field:
            return DB_Response(
                message="Tag Name Can Only Contain Letters, Numbers, Hyphens and Underscore: %s"
                % self.tag_name,
                status_code=400,
                success=False,
            )
        item = {"tag_name": {"S": self.tag_name}}

        try:
            self.db_client.put_item(TableName=self.TABLE_NAME, Item=item)
        except self.db_client.exceptions.ResourceNotFoundException as e:
            message = (
                "Cannot do operations on a non-existent table:  %s" % Tag.TABLE_NAME
            )
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
