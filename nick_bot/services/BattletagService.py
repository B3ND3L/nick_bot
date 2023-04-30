from nick_bot.services.SingletonFactory import SingletonFactory


class BattletagService:

    __ADD_BATTLETAG_PATTERN = 'Le battletag {battletag} à bien été ajouté pour {discord_name}'
    __BATTLETAG_ALREADY_EXISTS_PATTERN = 'Le battletag {battletag} exist déjà pour {discord_name}'
    __REMOVE_BATTLETAG_PATTERN = 'Le battletag {battletag} à bien été retiré pour {discord_name}'
    __BATTLETAG_NOT_FOUND = 'Le battletag {battletag} n\'existe pas pour {discord_name}'

    def __init__(self, config):
        self._overwatch_database = SingletonFactory.get_overwatch_db_instance(config['database'])

    def get_battletags(self, discord_name: str) -> list:
        documents = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        battletags = list()
        for document in documents:
            for battletag in document['battletags']:
                battletags.append(battletag)
        return battletags

    def add_battletag(self, battletag: str, discord_name: str) -> str:
        mongo_result = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            battletags = mongo_player['battletags']
            if not battletag in battletags:
                battletags.append(battletag)
                self._overwatch_database.update_battletags(discord_name, battletags)
                return self.__ADD_BATTLETAG_PATTERN.format(battletag=battletag, discord_name=discord_name)
            else:
               return self.__BATTLETAG_ALREADY_EXISTS_PATTERN.format(battletag=battletag, discord_name=discord_name)
        mongo_player = {
            'discord_name': discord_name,
            'battletags': [battletag]
        }
        self._overwatch_database.insert_battletag(mongo_player)
        return self.__ADD_BATTLETAG_PATTERN.format(battletag=battletag, discord_name=discord_name)

    def remove_battletag(self, battletag: str, discord_name: str) -> str:
        mongo_result = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            battletags = mongo_player['battletags']
            if battletag in battletags:
                battletags.remove(battletag)
                if len(battletags) > 0:
                    self._overwatch_database.update_battletags(discord_name, battletags)
                else:
                    self._overwatch_database.delete_battletag(discord_name)
                return self.__REMOVE_BATTLETAG_PATTERN.format(battletag=battletag, discord_name=discord_name)
        return self.__BATTLETAG_NOT_FOUND.format(battletag=battletag, discord_name=discord_name)
