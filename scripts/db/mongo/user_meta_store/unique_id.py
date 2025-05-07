from typing import Optional
from pydantic import BaseModel
from scripts.constants.db_constants import CollectionNames, DatabaseNames
from scripts.utils.mongo_util import AsyncMongoCollectionBaseClass


class UniqueIdSchema(BaseModel):
    """
    This is the Schema for the Mongo DB Collection.
    All datastore and general responses will be following the schema.
    """

    key: Optional[str] = ""
    id: Optional[str] = ""


class UniqueId(AsyncMongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(
            mongo_client,
            database=DatabaseNames.user_meta_store_db,
            collection=CollectionNames.collection_unique_id,
        )

    @property
    def key_key(self):
        return "key"

    async def find_one_record(self, **kwargs):
        """
        The following function will give one record for a given set of
        search parameters as keyword arguments
        :param kwargs:
        :return:
        """
        record = await self.find_one(query=kwargs)
        return UniqueIdSchema(**record) if record else UniqueIdSchema()

    async def insert_record(self, record: UniqueIdSchema):
        """
        The following function will give one record for a given set of
        search parameters as keyword arguments
        :param record:
        :return:
        """
        await self.insert_one(record.model_dump())
        return record.id

    async def update_record(self, record: UniqueIdSchema):
        """
        The following function will give one record for a given set of
        search parameters as keyword arguments
        :param record:
        :return:
        """
        await self.update_one(
            query={self.key_key: record.key}, data=record.model_dump()
        )
        return record.id
