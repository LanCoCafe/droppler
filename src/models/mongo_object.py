from abc import ABC, abstractmethod
from typing import Generic, Dict, Type, TypeVar, Iterator, Optional

from linebot.v3.messaging import MessagingApi
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

T = TypeVar("T", bound="MongoObject")


class MongoObject(ABC, Generic[T]):
    collection_name: str

    def __init__(self, api: MessagingApi, database: Database):
        self.api: MessagingApi = api
        self.database: Database = database

    @abstractmethod
    def unique_identifier(self) -> Dict:
        """
        Returns a dictionary representing the unique identifier for the document.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Returns a dictionary representation of the document to be upserted.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def upsert(self) -> UpdateResult:
        """
        Updates or inserts a document in the collection.

        :return: The UpdateResult of the update operation.
        """
        data = self.to_dict()

        return self.database.get_collection(self.__class__.collection_name).update_one(
            self.unique_identifier(),
            {"$set": data},
            upsert=True
        )

    def delete(self) -> DeleteResult:
        """
        Deletes this document from the collection.

        :return: The DeleteResult of the delete operation.
        """
        return self.database.get_collection(self.__class__.collection_name).delete_one(
            self.unique_identifier()
        )

    @classmethod
    def find_one(cls: Type[T], api: MessagingApi, database: Database, **kwargs) -> Optional[T]:
        """
        Find a document in the collection that matches the specified query.
        """
        document = database.get_collection(cls.collection_name).find_one(kwargs)

        if not document:
            return None

        # noinspection PyUnresolvedReferences
        del document["_id"]

        return cls(api=api, database=database, **document)

    @classmethod
    def find(cls: Type[T], api: MessagingApi, database: Database, **kwargs) -> Iterator[T]:
        """
        Find all documents in the collection that match the specified query.
        """
        cursor = database.get_collection(cls.collection_name).find(kwargs)

        for document in cursor:
            del document["_id"]

            yield cls(api=api, database=database, **document)
