from typing import Optional

from pydantic import BaseModel

from scripts.constants.db_constants import DatabaseNames, CollectionNames
from scripts.utils.mongo_util import MongoCollectionBaseClass


class UserCollectionKeys:
    KEY_USER_ID = "user_id"
    KEY_USERNAME = "username"
    KEY_USER_ROLE = "userrole"
    KEY_EMAIL = "email"


class UserPortfolioSchema(BaseModel):
    user_id: Optional[str] = ""
    scheme_code: Optional[int] = 0
    scheme_name: Optional[str] = ""
    units_held: Optional[float] = 0
    investment_on: Optional[int] = 0
    average_nav_price: Optional[float] = 0
    mutual_fund_family: Optional[str] = ""


class UserPortfolio(MongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(mongo_client, database=DatabaseNames.mutual_fund_db, collection=CollectionNames.collection_user_portfolio)
        self.key_user_id = UserCollectionKeys.KEY_USER_ID

    def update_user_portfolio(self, query, data):
        """
        The following function will update target details in rule_targets collections
        :param self:
        :param query:
        :param data:
        :return:
        """
        return self.update_one(query=query, data=data, upsert=True)

    def find_user_portfolio(self, user_id=None, scheme_code=None):
        query = {}
        if user_id:
            query[self.key_user_id] = user_id
        if scheme_code:
            query["scheme_code"] = scheme_code
        user = self.find(query=query)
        if user:
            return user
        return []
