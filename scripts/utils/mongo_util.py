import os
from typing import Dict, List, Optional

from pymongo import MongoClient
from pymongo.cursor import Cursor

from scripts.logging import logger


class MongoConnect:
    def __init__(self, uri):
        try:
            self.uri = uri
            self.client = MongoClient(self.uri, connect=False)
        except Exception as e:
            logger.exception(str(e))
            raise

    def __call__(self, *args, **kwargs):
        return self.client

    def __repr__(self):
        return f"Mongo Client(uri:{self.uri}, server_info={self.client.server_info()})"


class MongoCollectionBaseClass:
    def __init__(self, mongo_client, database, collection):
        self.client = mongo_client
        self.database = database
        self.collection = collection

    def insert_one(self, data: Dict):
        """
        The function is used to inserting a document to a collection in a Mongo Database.
        :param data: Data to be inserted
        :return: Insert ID
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_one(data)
            logger.qtrace(data)
            return response.inserted_id
        except Exception as e:
            logger.exception(str(e))
            raise

    def insert_many(self, data: List):
        """
        The function is used to inserting documents to a collection in a Mongo Database.
        :param data: List of Data to be inserted
        :return: Insert IDs
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_many(data)
            logger.qtrace(data)
            return response.inserted_ids
        except Exception as e:
            logger.exception(str(e))
            raise

    def find(
        self,
        query: Dict,
        filter_dict: Optional[Dict] = None,
        sort=None,
        collation: Optional[bool] = False,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> Cursor:
        """
        The function is used to query documents from a given collection in a Mongo Database
        :param query: Query Dictionary
        :param filter_dict: Filter Dictionary
        :param sort: List of tuple with key and direction. [(key, -1), ...]
        :param collation: can add rules for lettercase and accent marks.
        :param skip: Skip Number
        :param limit: Limit Number
        :return: List of Documents
        """
        if sort is None:
            sort = []
        if filter_dict is None:
            filter_dict = {"_id": 0}
        database_name = self.database
        collection_name = self.collection
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            if len(sort) > 0:
                cursor = (
                    collection.find(
                        query,
                        filter_dict,
                    )
                    .sort(sort)
                    .skip(skip)
                )
            else:
                cursor = collection.find(
                    query,
                    filter_dict,
                ).skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            if collation:
                cursor = cursor.collation({"locale": "en"})
            logger.qtrace(f"{query}, {filter_dict}")
            return cursor
        except Exception as e:
            logger.exception(str(e))
            raise

    def count_documents(self, query: Dict, limit: Optional[int] = 1) -> Cursor:
        """
        The function is used to count documents from a given collection in a Mongo Database
        :param query: Query Dictionary
        :param limit: Limit Number
        :return: List of Documents
        """
        database_name = self.database
        collection_name = self.collection
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            return collection.count_documents(query, limit=limit)
        except Exception as e:
            logger.exception(str(e))
            raise

    def find_one(self, query: Dict, filter_dict: Optional[Dict] = None):
        try:
            database_name = self.database
            collection_name = self.collection
            if filter_dict is None:
                filter_dict = {"_id": 0}
            db = self.client[database_name]
            collection = db[collection_name]
            logger.qtrace(f"{self.collection}, {query}, {filter_dict}")
            return collection.find_one(query, filter_dict)
        except Exception as e:
            logger.exception(str(e))
            raise

    def update_one(self, query: Dict, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_one(query, {"$set": data}, upsert=upsert)
            logger.qtrace(f"{self.collection}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    def update_to_set(self, query: Dict, param: str, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param param:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_one(query, {"$addToSet": {param: data}}, upsert=upsert)
            logger.qtrace(f"{self.collection}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    def update_many(self, query: Dict, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_many(query, {"$set": data}, upsert=upsert)
            logger.qtrace(f"{query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(str(e))
            raise

    def delete_many(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.delete_many(query)
            logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(str(e))
            raise

    def delete_one(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.delete_one(query)
            logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(str(e))
            raise

    def distinct(self, query_key: str, filter_json: Optional[Dict] = None):
        """
        :param query_key:
        :param filter_json:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            logger.qtrace(f"{query_key}, {filter_json}")
            return collection.distinct(query_key, filter_json)
        except Exception as e:
            logger.exception(str(e))
            raise

    def aggregate(self, pipelines: List, collation=None):
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            logger.qtrace(f"{self.collection}, {pipelines}")
            if collation:
                return collection.aggregate(pipelines, collation=collation)
            return collection.aggregate(pipelines)
        except Exception as e:
            logger.exception(str(e))
            raise
