import re
from typing import Optional

from pydantic import BaseModel

from scripts.constants.db_constants import DatabaseNames, CollectionNames
from scripts.utils.mongo_util import AsyncMongoCollectionBaseClass


class UserCollectionKeys:
    KEY_USER_ID = "user_id"
    KEY_USERNAME = "username"
    KEY_USER_ROLE = "userrole"
    KEY_EMAIL = "email"


class UserSchema(BaseModel):
    Scheme_Code: Optional[float] = 0
    ISIN_Div_Payout_ISIN_Growth: Optional[str] = ""
    ISIN_Div_Reinvestment: Optional[str] = ""
    Scheme_Name: Optional[str] = ""
    Net_Asset_Value: Optional[float] = 0
    Date: Optional[str] = ""
    Scheme_Type: Optional[str] = ""
    Scheme_Category: Optional[str] = ""
    Mutual_Fund_Family: Optional[str] = ""


class MutualFundData(AsyncMongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(
            mongo_client,
            database=DatabaseNames.mutual_fund_db,
            collection=CollectionNames.collection_mutual_fund_data,
        )
        self.key_user_id = UserCollectionKeys.KEY_USER_ID
        self.key_username = UserCollectionKeys.KEY_USERNAME
        self.key_email = UserCollectionKeys.KEY_EMAIL

    async def fetch_records(self, scheme_name=None, mutual_fund_family=None):
        """
        The following function will update target details in rule_targets collections
        :param self:
        :param scheme_name:
        :param mutual_fund_family:
        :return:
        """
        query = {}
        if scheme_name:
            query["Scheme_Name"] = scheme_name
        if mutual_fund_family:
            query["Mutual_Fund_Family"] = mutual_fund_family
        return await self.find(query=query)

    async def insert_one_user(self, data):
        """
        The following function will insert one user in the
        user collections
        :param self:
        :param data:
        :return:
        """
        return await self.insert_one(data)

    async def find_user(
        self, user_id=None, username=None, email=None, filter_dict=None
    ):
        query = {}
        if user_id:
            query[self.key_user_id] = user_id
        if username:
            query[self.key_username] = username
        if email:
            query[self.key_email] = re.compile(email, re.IGNORECASE)
            query[self.key_email] = email
        user = await self.find_one(query=query, filter_dict=filter_dict)
        if user:
            return UserSchema(**user)
        return UserSchema()

    async def get_all_users(
        self, filter_dict=None, sort=None, skip=0, limit=None, **query
    ):
        users = await self.find(
            filter_dict=filter_dict, sort=sort, skip=skip, limit=limit, query=query
        )
        return list(users) or []

    async def delete_one_user(self, user_id):
        return await self.delete_one(query={self.key_user_id: user_id})

    async def update_one_user(self, query, data):
        """
        The following function will insert one user in the
        user collections
        :param self:
        :param query:
        :param data:
        :return:
        """
        return await self.update_one(query=query, data=data, upsert=True)
