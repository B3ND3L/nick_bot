from pymongo import MongoClient
from pymongo.cursor import Cursor


class OverwatchDB:
    _db_client = None
    __DATABASE_NAME = 'Overwatch'
    __BATTLETAG_COLLECTION_NAME = 'Battletags'

    def __init__(self, config: dict):
        user = config['user']
        password = config['password']
        host = config['host']
        port = config['port']

        connexion_uri = f'mongodb://{user}:{password}@{host}:{port}/{self.__DATABASE_NAME}'
        self._db_client = MongoClient(connexion_uri)

    """
    
    MANAGE BATTLETAG DOCUMENTS

    """

    def find_battletag_by_discord_name(self, discord_name: str) -> Cursor:
        filters = {'discord_name': discord_name}
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(self.__BATTLETAG_COLLECTION_NAME)
        return collection.find(filters, {}, limit=1)

    def insert_battletag(self, document: dict):
        self.insert_document(self.__BATTLETAG_COLLECTION_NAME, document)

    def update_battletags(self, discord_name: str, battletags: list):
        self.update_document(self.__BATTLETAG_COLLECTION_NAME, {'discord_name': discord_name},
                             {'battletags': battletags})

    def delete_battletag(self, discord_name):
        self.delete_document(self.__BATTLETAG_COLLECTION_NAME, {'discord_name': discord_name})

    """
    
    GENERIC MONGO OPERATIONS
    
    """

    def insert_document(self, collection_name: str, document: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.insert_one(document)

    def update_document(self, collection_name: str, filters: dict, changes: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.update_one(filters,
                              {"$set": changes})

    def delete_document(self, collection_name: str, filters: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.delete_one(filters)
