from pymongo import MongoClient


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

    def add_battletag(self, discord_name: str, battletag: str):
        mongo_result = self.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            # { discord_name : str, battletags : list}
            battletags = mongo_player['battletags']
            if not battletag in battletags:
                battletags.append(battletag)
                self.update_document(self.__BATTLETAG_COLLECTION_NAME, {"discord_name": discord_name}, {'battletags': battletags})
                return 1
            else:
                return 0
        mongo_player = {
            'discord_name': discord_name,
            'battletags': [battletag]
        }
        self.insert_document(self.__BATTLETAG_COLLECTION_NAME, mongo_player)
        return 1

    def remove_battletag(self, discord_name: str, battletag: str):
        mongo_result = self.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            battletags = mongo_player['battletags']
            # { discord_name : str, battletags : list}
            if battletag in battletags:
                battletags.remove(battletag)
                filters = {"discord_name": discord_name}
                if len(battletags) > 0:
                    self.update_document(self.__BATTLETAG_COLLECTION_NAME, filters, {'battletags': battletags})
                else:
                    self.delete_document(self.__BATTLETAG_COLLECTION_NAME, filters)
                return 1
        return 0

    def find_battletag_by_discord_name(self, discord_name: str):
        filters = {"discord_name": discord_name}
        collection = self._db_client.get_database(self.__DATABASE_NAME).get_collection(self.__BATTLETAG_COLLECTION_NAME)
        return collection.find(filters, {}, limit=1)

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
