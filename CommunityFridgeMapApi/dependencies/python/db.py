from email import message
import os
import boto3
import time
from botocore.exceptions import ClientError
import logging
from typing import Tuple

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

    def __init__(self, db_client: "botocore.client.DynamoDB"):
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


class Fridge(DB_Item):
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 32
    REQUIRED_FIELDS = ["display_name", "address", "lat", "long"]
    TABLE_NAME = "fridge"
    FOOD_ACCEPTS = []  # TODO: Fill this in
    FOOD_RESTRICTIONS = []  # TODO: fill this in
    ITEM_TYPES = {
        "display_name": "S",
        "username": "S",
        "address": "S",
        "instagram": "S",
        "info": "S",
        "url": "S",
        "neighborhood": "S",
        "organizer_email": "S",
        "tags": "L",
        "food_accepts": "L",
        "food_restrictions": "L",
        "lat": "S",
        "long": "S",
        "last_edited": "N",
        "profile_image": "S",
        "report_timestamp": "S",
        "report_notes": "S",
        "report_status": "S",
        "report_image": "S",
    }

    def __init__(self, db_client: "botocore.client.DynamoDB", fridge: dict = None):
        super().__init__(db_client=db_client)
        if fridge is not None:
            self.display_name: str = fridge.get(
                "display_name", None
            )  # display_name must be alphanumeric (spaces are fine)
            self.username: str = fridge.get("username", None)
            self.address: str = fridge.get("address", None)
            self.instagram: str = fridge.get("instagram", None)
            self.info: str = fridge.get("info", None)
            self.url: str = fridge.get("url", None)
            self.neighborhood: str = fridge.get("neighborhood", None)
            self.organizer_email: str = fridge.get("organizer_email", None)
            self.tags: list = fridge.get("tags", None)
            self.food_accepts: list = fridge.get("food_accepts", None)
            self.food_restrictions: list = fridge.get("food_restrictions", None)
            self.lat: str = fridge.get("lat", None)
            self.long: str = fridge.get("long", None)
            self.profile_image: str = fridge.get("profile_image", None)
            self.last_edited: str = fridge.get("last_edited", None)
            self.report_timestamp: int = fridge.get("report_timestamp", None)
            self.report_notes: str = fridge.get("report_notes", None)
            self.report_status: str = fridge.get("report_status", None)
            self.report_image: str = fridge.get("report_image", None)

    def get_item(self):
        pass

    def get_items(self):
        pass

    def add_items(self):
        pass

    def set_username(self):
        # Fridge username is the display_name with no spaces and all lower cased
        username = self.display_name.lower().replace(" ", "")
        self.username = username

    def is_valid_display_name(self) -> bool:
        # A valid display_name is alphanumric and can contain spaces
        username = self.display_name.lower().replace(" ", "")
        return username.isalnum()

    @staticmethod
    def is_valid_username(fridge_username) -> tuple[bool, str]:
        if fridge_username is None:
            return False, "Missing Required Field: username"
        if not fridge_username.isalnum():
            return False, "Username Must Be Alphanumeric"
        username_length = len(fridge_username)
        is_valid_username_length = (
            username_length >= Fridge.MIN_USERNAME_LENGTH
            and username_length <= Fridge.MAX_USERNAME_LENGTH
        )
        if not is_valid_username_length:
            return (
                False,
                f"Username Must Have A Character Length >= {Fridge.MIN_USERNAME_LENGTH} and <= {Fridge.MAX_USERNAME_LENGTH}",
            )
        return True, "success"

    def set_last_edited(self):
        self.last_edited = str(int(time.time()))

    def add_item(self) -> DB_Response:
        has_required_fields, field = self.has_required_fields()
        if not has_required_fields:
            return DB_Response(
                message="Missing Required Field: %s" % field,
                status_code=400,
                success=False,
            )
        if not self.is_valid_display_name():
            return DB_Response(
                message="Display Name Can Only Contain Letters, Numbers, and Spaces",
                status_code=400,
                success=False,
            )
        self.set_username()
        self.set_last_edited()
        item = self.format_dynamodb_item()
        conditional_expression = "attribute_not_exists(username)"
        try:
            self.db_client.put_item(
                TableName=self.TABLE_NAME,
                Item=item,
                ConditionExpression=conditional_expression,
            )
        except self.db_client.exceptions.ConditionalCheckFailedException as e:
            return DB_Response(
                message="Fridge already exists, pick a different name",
                status_code=409,
                success=False,
            )
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
            message="Fridge was succesfully added", status_code=200, success=True
        )

    def get_fridge_locations(self):
        pass


class FridgeReport(DB_Item):

    REQUIRED_FIELDS = ["fridge_username", "status", "fridge_percentage"]
    ITEM_TYPES = {
        "notes": "S",
        "fridge_username": "S",
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
            self.fridge_username: str = fridge_report.get("fridge_username", None)
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
        is_valid_username, is_valid_username_message = Fridge.is_valid_username(
            self.fridge_username
        )
        if not is_valid_username:
            return DB_Response(
                message=is_valid_username_message, status_code=400, success=False
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
