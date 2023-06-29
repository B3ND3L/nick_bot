from pymongo import MongoClient
from pymongo.cursor import Cursor


class OverwatchDB:
    _db_client = None
    __DATABASE_NAME = 'Overwatch'
    __BATTLETAG_COLLECTION_NAME = 'Battletags'
    __TEMP_STAT_COLLECTION_NAME = 'Temp_stats'
    __SESSIONS_COLLECTION_NAME = 'Sessions'
    __HEROES_COLLECTION_NAME = 'Heroes'

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
        return self.find_one_document(self.__BATTLETAG_COLLECTION_NAME, filters)

    def insert_battletag(self, document: dict):
        self.insert_document(self.__BATTLETAG_COLLECTION_NAME, document)

    def update_battletags(self, discord_name: str, battletags: list):
        self.update_document(self.__BATTLETAG_COLLECTION_NAME, {'discord_name': discord_name},
                             {'battletags': battletags})

    def delete_battletag(self, discord_name):
        self.delete_document(self.__BATTLETAG_COLLECTION_NAME, {'discord_name': discord_name})

    """
    
    MANAGE STATS DOCUMENTS
    
    """

    def insert_all_stats(self, stats: list):
        self.insert_documents(self.__TEMP_STAT_COLLECTION_NAME, stats)

    def insert_all_session_stats(self, stats: list):
        self.insert_documents(self.__SESSIONS_COLLECTION_NAME, stats)

    def get_stats_multiple_battletag(self, battletags: list):
        filters = {'player': {'$in':  battletags}}
        return self.find_documents(self.__TEMP_STAT_COLLECTION_NAME, filters)

    def delete_temp_stats_by_battletags(self, battletags: list):
        filters = {'player': {'$in': battletags}}
        self.delete_document(self.__TEMP_STAT_COLLECTION_NAME, filters)

    """
    
    MANAGE HEROES DOCUMENTS
    
    """

    def insert_heroes(self, heroes: list):
        self.insert_documents(self.__HEROES_COLLECTION_NAME, heroes)

    def delete_all_heroes(self):
        self.delete_documents(self.__HEROES_COLLECTION_NAME)

    """
    
    GENERIC MONGO OPERATIONS
    
    """

    def insert_document(self, collection_name: str, document: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.insert_one(document)

    def insert_documents(self, collection_name: str, documents: list):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.insert_many(documents)

    def update_document(self, collection_name: str, filters: dict, changes: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.update_one(filters,
                              {"$set": changes})

    def delete_document(self, collection_name: str, filters: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.delete_one(filters)

    def delete_documents(self, collection_name: str, filters: dict={}):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        collection.delete_many(filters)

    def find_one_document(self, collection_name: str, filters: dict):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        return collection.find(filters, {}, limit=1)

    def find_documents(self, collection_name: str, filters: dict, project: dict={}):
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(collection_name)
        return collection.find(filters, project)
