from nick_bot.datas.OverwatchDB import OverwatchDB


class BattletagService:

    def __init__(self, config):
        self._overwatch_database = OverwatchDB(config)

    def get_battletags(self, discord_name: str) -> list:
        documents = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        battletags = list()
        for document in documents:
            for battletag in document['battletags']:
                battletags.append(battletag)
        return battletags

    def add_battletag(self, battletag: str, username: str) -> str:
        status = self._overwatch_database.add_battletag(username, battletag)
        if status == 1:
            return f'Le battletag a été ajouté'
        else:
            return f'Tu as déjà ajouté ce battletag'

    def remove_battletag(self, battletag: str, username: str) -> str:
        status = self._overwatch_database.remove_battletag(username, battletag)
        if status == 1:
            return f'Le battletag a été retiré'
        else:
            return f'Tu n\'as aucun battletag'

    def add_battletag(self, discord_name: str, battletag: str) -> int:
        mongo_result = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            battletags = mongo_player['battletags']
            if not battletag in battletags:
                battletags.append(battletag)
                self._overwatch_database.update_battletags(discord_name, battletags)
                return 1
            else:
                return 0
        mongo_player = {
            'discord_name': discord_name,
            'battletags': [battletag]
        }
        self._overwatch_database.insert_battletag(mongo_player)
        return 1

    def remove_battletag(self, discord_name: str, battletag: str) -> int:
        mongo_result = self._overwatch_database.find_battletag_by_discord_name(discord_name)
        for mongo_player in mongo_result:
            battletags = mongo_player['battletags']
            if battletag in battletags:
                battletags.remove(battletag)
                if len(battletags) > 0:
                    self._overwatch_database.update_battletags(discord_name, battletags)
                else:
                    self._overwatch_database.delete_battletag(discord_name)
                return 1
        return 0
