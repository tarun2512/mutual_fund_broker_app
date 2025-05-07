from typing import Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from scripts.logging import logger


class MongoConnect:
    def __init__(self, uri: str):
        try:
            self.uri = uri
            self.client = AsyncIOMotorClient(self.uri, connect=False)
        except Exception as e:
            logger.exception(f"Failed to initialize MongoClient: {str(e)}")
            raise

    def __call__(self, *args, **kwargs):
        return self.client

    def __repr__(self):
        return f"MongoConnect(uri={self.uri})"


class AsyncMongoCollectionBaseClass:
    def __init__(
        self, mongo_client: AsyncIOMotorClient, database: str, collection: str
    ):
        self.collection: AsyncIOMotorCollection = mongo_client[database][collection]

    async def insert_one(self, data: Dict) -> str:
        try:
            response = await self.collection.insert_one(data)
            logger.qtrace(data)
            return str(response.inserted_id)
        except Exception as e:
            logger.exception(str(e))
            raise

    async def insert_many(self, data: List[Dict]) -> List[str]:
        try:
            response = await self.collection.insert_many(data)
            logger.qtrace(data)
            return [str(id_) for id_ in response.inserted_ids]
        except Exception as e:
            logger.exception(str(e))
            raise

    async def find(
        self,
        query: Dict,
        filter_dict: Optional[Dict] = None,
        sort: Optional[List] = None,
        collation: Optional[Dict] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        try:
            filter_dict = filter_dict or {"_id": 0}
            cursor = self.collection.find(query, filter_dict)

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            if collation:
                cursor = cursor.collation(collation)

            logger.qtrace(f"{query}, {filter_dict}")
            return [doc async for doc in cursor]
        except Exception as e:
            logger.exception(str(e))
            raise

    async def count_documents(self, query: Dict, limit: Optional[int] = 0) -> int:
        try:
            return await self.collection.count_documents(query, limit=limit)
        except Exception as e:
            logger.exception(str(e))
            raise

    async def find_one(
        self, query: Dict, filter_dict: Optional[Dict] = None
    ) -> Optional[Dict]:
        try:
            filter_dict = filter_dict or {"_id": 0}
            logger.qtrace(f"{self.collection.name}, {query}, {filter_dict}")
            return await self.collection.find_one(query, filter_dict)
        except Exception as e:
            logger.exception(str(e))
            raise

    async def update_one(self, query: Dict, data: Dict, upsert: bool = False) -> int:
        try:
            response = await self.collection.update_one(
                query, {"$set": data}, upsert=upsert
            )
            logger.qtrace(f"{self.collection.name}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    async def update_to_set(
        self, query: Dict, param: str, data: Dict, upsert: bool = False
    ) -> int:
        try:
            response = await self.collection.update_one(
                query, {"$addToSet": {param: data}}, upsert=upsert
            )
            logger.qtrace(f"{self.collection.name}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    async def update_many(self, query: Dict, data: Dict, upsert: bool = False) -> int:
        try:
            response = await self.collection.update_many(
                query, {"$set": data}, upsert=upsert
            )
            logger.qtrace(f"{query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    async def delete_one(self, query: Dict) -> int:
        try:
            response = await self.collection.delete_one(query)
            logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(str(e))
            raise

    async def delete_many(self, query: Dict) -> int:
        try:
            response = await self.collection.delete_many(query)
            logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(str(e))
            raise

    async def distinct(
        self, query_key: str, filter_json: Optional[Dict] = None
    ) -> List:
        try:
            logger.qtrace(f"{query_key}, {filter_json}")
            return await self.collection.distinct(query_key, filter_json or {})
        except Exception as e:
            logger.exception(str(e))
            raise

    async def aggregate(
        self, pipelines: List[Dict], collation: Optional[Dict] = None
    ) -> List[Dict]:
        try:
            logger.qtrace(f"{self.collection.name}, {pipelines}")
            if collation:
                cursor = self.collection.aggregate(pipelines, collation=collation)
            else:
                cursor = self.collection.aggregate(pipelines)
            return [doc async for doc in cursor]
        except Exception as e:
            logger.exception(str(e))
            raise
