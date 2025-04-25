import re
from typing import Any, Dict, Optional

from pydantic import BaseModel

from scripts.constants.db_constants import DatabaseNames, CollectionNames
from scripts.utils.mongo_util import MongoCollectionBaseClass


class UserCollectionKeys:
    KEY_USER_ID = "user_id"
    KEY_USERNAME = "username"
    KEY_USER_ROLE = "userrole"
    KEY_EMAIL = "email"


class UserSchema(BaseModel):
    username: Optional[str] = ""
    password: Optional[str] = ""
    email: Optional[Any] = None
    phonenumber: Optional[Any] = None
    user_id: Optional[str] = ""
    created_by: Optional[str] = ""
    encryption_salt: Optional[Dict] = {}
    passwordReset: Optional[Dict] = {}
    failed_attempts: Optional[int] = 0
    is_user_locked: Optional[bool] = False
    last_failed_login: Optional[int] = 0
    last_logged_in: Optional[int] = 0
    created_on: Optional[int] = 0
    updated_on: Optional[int] = 0


class User(MongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(mongo_client, database=DatabaseNames.user_meta_store_db, collection=CollectionNames.collection_user)
        self.key_user_id = UserCollectionKeys.KEY_USER_ID
        self.key_username = UserCollectionKeys.KEY_USERNAME
        self.key_email = UserCollectionKeys.KEY_EMAIL

    def update_user(self, query, data):
        """
        The following function will update target details in rule_targets collections
        :param self:
        :param query:
        :param data:
        :return:
        """
        return self.update_one(query=query, data=data, upsert=True)

    def insert_one_user(self, data):
        """
        The following function will insert one user in the
        user collections
        :param self:
        :param data:
        :return:
        """
        return self.insert_one(data)

    def find_user(self, user_id=None, username=None, email=None, filter_dict=None):
        query = {}
        if user_id:
            query[self.key_user_id] = user_id
        if username:
            query[self.key_username] = username
        if email:
            query[self.key_email] = re.compile(email, re.IGNORECASE)
            query[self.key_email] = email
        user = self.find_one(query=query, filter_dict=filter_dict)
        if user:
            return UserSchema(**user)
        return UserSchema(**{})

    def get_all_users(self, filter_dict=None, sort=None, skip=0, limit=None, **query):
        users = self.find(filter_dict=filter_dict, sort=sort, skip=skip, limit=limit, query=query)
        if users:
            return list(users)
        return []

    def delete_one_user(self, user_id):
        return self.delete_one(query={self.key_user_id: user_id})

    def update_one_user(self, query, data):
        """
        The following function will insert one user in the
        user collections
        :param self:
        :param query:
        :param data:
        :return:
        """
        return self.update_one(query=query, data=data, upsert=True)
