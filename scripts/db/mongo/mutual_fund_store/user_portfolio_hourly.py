from typing import Any, Optional

from pydantic import BaseModel

from scripts.constants.db_constants import DatabaseNames, CollectionNames
from scripts.utils.mongo_util import AsyncMongoCollectionBaseClass


class UserCollectionKeys:
    KEY_USER_ID = "user_id"
    KEY_USERNAME = "username"
    KEY_USER_ROLE = "userrole"
    KEY_EMAIL = "email"


class UserPortfolioHourlySchema(BaseModel):
    user_id: Optional[str] = ""
    timestamp: Optional[int] = 0
    total_value: Optional[Any] = None
    investments: Optional[Any] = None


class UserPortfolioHourly(AsyncMongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(
            mongo_client,
            database=DatabaseNames.mutual_fund_db,
            collection=CollectionNames.collection_user_portfolio_hourly,
        )
        self.key_user_id = UserCollectionKeys.KEY_USER_ID

    async def update_user_portfolio_hourly(self, query, data):
        """
        The following function will update target details in rule_targets collections
        :param self:
        :param query:
        :param data:
        :return:
        """
        return await self.update_one(query=query, data=data, upsert=True)

    async def find_user_portfolio_hourly(self, user_id=None, scheme_code=None):
        query = {}
        if user_id:
            query[self.key_user_id] = user_id
        if scheme_code:
            query["scheme_code"] = scheme_code
        user = await self.find(query=query)
        if user:
            return list(user)
        return []
