import datetime

from discord import Member

from nick_bot.datas.OverwatchApi import OverwatchApi
from nick_bot.datas.OverwatchDB import OverwatchDB
from nick_bot.services.BattletagService import BattletagService

from nick_bot.services.SingletonFactory import SingletonFactory


class SessionService:

    def __init__(self, config: dict, battletag_service: BattletagService):
        self._battletag_service = battletag_service
        self._overwatch_api = OverwatchApi(config['api'])
        self._overwatch_database: OverwatchDB = SingletonFactory.get_overwatch_db_instance(config['database'])

    def on_presence(self, before: Member, after: Member):
        member_name = after.name
        intersting_activities = ['Overwatch 2']

        was_ingame = False
        now_ingame = False

        for activity in before.activities:
            if activity.name in intersting_activities:
                was_ingame = True

        for activity in after.activities:
            if activity.name in intersting_activities:
                now_ingame = True

        if not was_ingame and now_ingame:
            print(f'{member_name} started to play')
            self.session_start(member_name)
        elif was_ingame and not now_ingame:
            print(f'{member_name} stopped to play')
            self.session_stop(member_name)

    def session_start(self, discord_name):
        battletags = self._battletag_service.get_battletags(discord_name)
        all_stats = self.get_stats(battletags)
        self.insert_all_temp_stats(all_stats)

    def session_stop(self, discord_name):
        battletags = self._battletag_service.get_battletags(discord_name)
        after_session_stats = self.get_stats(battletags)
        before_session_stats = self.get_saved_stats(battletags)

        session_stats = self.compute_session_stat(before_session_stats, after_session_stats)
        if session_stats:
            self.insert_all_session_stats(session_stats)
            self._overwatch_database.delete_temp_stats_by_battletags(battletags)

    def get_stats(self, battletags: list):
        all_stats = list()
        for battletag in battletags:
            player_id = self.format_battletag(battletag)
            stats = self._overwatch_api.get_stat(player_id)
            stats['player'] = battletag
            stats['date'] = datetime.datetime.now()
            all_stats.append(stats)
        return all_stats

    def insert_all_session_stats(self, all_stats):
        self._overwatch_database.insert_all_session_stats(all_stats)

    def insert_all_temp_stats(self, all_stats):
        self._overwatch_database.insert_all_stats(all_stats)

    def get_saved_stats(self, battletags):
        stats_cursor = self._overwatch_database.get_stats_multiple_battletag(battletags)
        returned_stats = list()
        for stat in stats_cursor:
            returned_stats.append(stat)
        return returned_stats

    def compute_session_stat(self, before_session_stats, after_session_stats) -> list:
        before_session_stats = self.format_stats(before_session_stats)
        after_session_stats = self.format_stats(after_session_stats)

        delta_session_stats = list()

        for player, before_stat in before_session_stats.items():

            delta_stat = dict()

            after_stat = after_session_stats[player]
            nb_game_tank = after_stat['roles']['tank']['games_played'] - before_stat['roles']['tank']['games_played']
            nb_game_dps = after_stat['roles']['damage']['games_played'] - before_stat['roles']['damage']['games_played']
            nb_game_supp = after_stat['roles']['support']['games_played'] - before_stat['roles']['support'][
                'games_played']

            if nb_game_tank == 0 and nb_game_supp == 0 and nb_game_dps == 0:
                print(f'{player} didn\'t play this session')
            else:
                delta_stat['player'] = player
                if nb_game_tank > 0:
                    delta_stat['tank'] = self.make_diff(before_stat['roles']['tank'],
                                                        after_stat['roles']['tank'])
                if nb_game_supp > 0:
                    delta_stat['support'] = self.make_diff(before_stat['roles']['support'],
                                                           after_stat['roles']['support'])
                if nb_game_dps > 0:
                    delta_stat['damage'] = self.make_diff(before_stat['roles']['damage'],
                                                          after_stat['roles']['damage'])
            delta_session_stats.append(delta_stat)
        return delta_session_stats

    @staticmethod
    def make_diff(stat_before: dict, stat_after: dict) -> dict:

        delta_stat = dict()

        delta_stat['games_played'] = stat_after['games_played'] - stat_before['games_played']
        delta_stat['time_played'] = stat_after['time_played'] - stat_before['time_played']
        delta_stat['winrate'] = stat_after['winrate'] - stat_before['winrate']
        delta_stat['kda'] = stat_after['kda'] - stat_before['kda']
        delta_stat['total'] = dict()
        delta_stat['total']['eliminations'] = stat_after['total']['eliminations'] - stat_before['total']['eliminations']
        delta_stat['total']['assists'] = stat_after['total']['assists'] - stat_before['total']['assists']
        delta_stat['total']['deaths'] = stat_after['total']['deaths'] - stat_before['total']['deaths']
        delta_stat['total']['damage'] = stat_after['total']['damage'] - stat_before['total']['damage']
        delta_stat['total']['healing'] = stat_after['total']['healing'] - stat_before['total']['healing']
        # TODO Compute Average stats in this session

        return delta_stat

    @staticmethod
    def format_stats(stats: list) -> dict:
        returned_dict = {}
        for stat in stats:
            returned_dict[stat['player']] = stat
        return returned_dict

    @staticmethod
    def format_battletag(battletag: str) -> str:
        return battletag.replace('#', '-')
