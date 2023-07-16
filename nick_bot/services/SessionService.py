import asyncio
import datetime
import logging

from discord import Member

from nick_bot.datas.OverwatchApi import OverwatchApi
from nick_bot.datas.OverwatchDB import OverwatchDB
from nick_bot.services.BattletagService import BattletagService

from nick_bot.services.SingletonFactory import SingletonFactory


class SessionService:

    """
    Service to manage the sessions
    """

    __TIME_BETWEEN_REQUEST: int = 4000
    __ROLES: list = ('tank', 'damage', 'support')


    def __init__(self, config: dict, battletag_service: BattletagService):
        """
        Constructor
        :param config:
        :param battletag_service:
        """
        self._battletag_service = battletag_service
        self._overwatch_api = OverwatchApi(config['api'])
        self._overwatch_database: OverwatchDB = SingletonFactory.get_overwatch_db_instance(config['database'])
        self._logger = logging.getLogger('discord')

    async def on_presence(self, before: Member, after: Member):
        """
        Check if a player started or stopped to play
        :param before:
        :param after:
        :return:
        """
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
            self._logger.info(f'{member_name} started to play')
            self.session_start(member_name)
        elif was_ingame and not now_ingame:
            self._logger.info(f'{member_name} stopped to play')
            await self.session_stop(member_name)

    def session_start(self, discord_name):
        """
        Start a session for a player
        :param discord_name:
        :return:
        """
        battletags = self._battletag_service.get_battletags(discord_name)
        all_stats = self.get_stats(battletags)
        if all_stats:
            self.insert_all_temp_stats(all_stats)
        else:
            self._logger.warning(f'No stats for {battletags}')

    async def session_stop(self, discord_name):
        """
        Stop a session for a player
        :param discord_name:
        :return:
        """
        battletags = self._battletag_service.get_battletags(discord_name)
        session_stats = await self.compute_session_stat(battletags)
        if session_stats:
            self.insert_all_session_stats(session_stats)
        self._overwatch_database.delete_temp_stats_by_battletags(battletags)

    def get_stats(self, battletags: list):
        """
        Get stats for a list of battletags
        :param battletags:
        :return:
        """
        all_stats = list()
        for battletag in battletags:
            player_id = self.format_battletag(battletag)
            stats = self._overwatch_api.get_summary_stats(player_id)
            stats['player'] = battletag
            stats['date'] = datetime.datetime.now()
            all_stats.append(stats)
        return all_stats

    def get_player_stats(self, battletag: str) -> dict:
        """
        Get stats for a battletag
        :param battletag:
        :return:
        """
        player_id = self.format_battletag(battletag)
        return self._overwatch_api.get_summary_stats(player_id)

    def insert_all_session_stats(self, all_stats):
        """
        Insert all session stats in database
        :param all_stats:
        :return:
        """
        self._overwatch_database.insert_all_session_stats(all_stats)

    def insert_all_temp_stats(self, all_stats):
        """
        Insert all temp stats in database
        :param all_stats:
        :return:
        """
        self._overwatch_database.insert_all_stats(all_stats)

    def get_saved_stats(self, battletags):
        """
        Get saved stats for a list of battletags
        :param battletags:
        :return:
        """
        stats_cursor = self._overwatch_database.get_stats_multiple_battletag(battletags)
        returned_stats = list()
        for stat in stats_cursor:
            returned_stats.append(stat)
        return returned_stats

    def get_heroes_names(self):
        """
        Get all heroes names
        :return:
        """
        return self._overwatch_database.get_heroes_names()


    async def compute_session_stat(self, battletags) -> list:
        """
        Compute session stats for a list of battletags
        :param battletags:
        :return:
        """
        before_session_stats = self.format_stats(self.get_saved_stats(battletags))
        delta_session_stats = list()

        for player, before_stat in before_session_stats.items():
            session_time_start = before_stat['date']
            now = datetime.datetime.now()
            delta = now - session_time_start
            if delta.seconds > self.__TIME_BETWEEN_REQUEST:
                after_stat = self.get_player_stats(player)
            else:
                waiting_time = self.__TIME_BETWEEN_REQUEST - delta.seconds
                self._logger.info(f'Waiting {waiting_time} seconds before requesting stats for {player}')
                after_stat = await asyncio.sleep(waiting_time, self.get_player_stats(player))

            delta_stat = dict()

            nb_games_played = self.compute_nb_games_played(before_stat, after_stat)
            if nb_games_played == 0:
                self._logger.warning(f'No games played for {player}')
            else:
                for role in self.__ROLES:
                    delta_stat['player'] = player
                    delta_stat[role] = self.make_diff(before_stat['roles'][role], after_stat['roles'][role])
                    if not delta_stat[role]:
                        del(delta_stat[role])
                    delta_session_stats.append(delta_stat)
                for hero in  self.get_heroes_names():
                    delta_stat['player'] = player
                    delta_stat[hero] = self.make_diff(before_stat['heroes'][hero], after_stat['heroes'][hero])
                    if not delta_stat[hero]:
                        del(delta_stat[hero])
                    delta_session_stats.append(delta_stat)

        return delta_session_stats

    def make_diff(self, stat_before: dict, stat_after: dict) -> dict:
        """
        Make the difference between two session stats
        :param stat_before:
        :param stat_after:
        :return:
        """
        delta_stat = dict()

        if self.compute_nb_game_played(stat_before['games_played'], stat_after['games_played']) == 0:
            self._logger.warning(f'No games played for the role')
        else:
            delta_stat['games_played'] = stat_after['games_played'] - stat_before['games_played']
            delta_stat['time_played'] = stat_after['time_played'] - stat_before['time_played']
            delta_stat['winrate'] = self.compute_winrate_diff(stat_before['winrate'], stat_after['winrate'],
                                                              stat_before['games_played'], stat_after['games_played'])
            delta_stat['kda'] = stat_after['kda'] - stat_before['kda']
            delta_stat['total'] = dict()
            delta_stat['total']['eliminations'] = stat_after['total']['eliminations'] - stat_before['total']['eliminations']
            delta_stat['total']['assists'] = stat_after['total']['assists'] - stat_before['total']['assists']
            delta_stat['total']['deaths'] = stat_after['total']['deaths'] - stat_before['total']['deaths']
            delta_stat['total']['damage'] = stat_after['total']['damage'] - stat_before['total']['damage']
            delta_stat['total']['healing'] = stat_after['total']['healing'] - stat_before['total']['healing']
            # TODO Compute Average stats in this session

        return delta_stat

    def compute_winrate_diff(self, before_winrate, after_winrate, before_games_played, after_games_played) -> float:
        """
        Compute winrate diff between two sessions
        :param before_winrate:
        :param after_winrate:
        :param before_games_played:
        :param after_games_played:
        :return:
        """
        before_wins = self.compute_win_count_by_winrate_and_games(before_winrate, before_games_played)
        after_wins = self.compute_win_count_by_winrate_and_games(after_winrate, after_games_played)
        delta_wins = after_wins - before_wins
        delta_games_played = after_games_played - before_games_played
        return self.compute_winrate(delta_wins, delta_games_played)

    def compute_nb_games_played(self, before_stat, after_stat) -> int:
        """
        Compute number of games played between two sessions
        :param before_stat:
        :param after_stat:
        :return:
        """
        nb_game_tank = after_stat['roles']['tank']['games_played'] - before_stat['roles']['tank']['games_played']
        nb_game_supp = after_stat['roles']['support']['games_played'] - before_stat['roles']['support']['games_played']
        nb_game_dps = after_stat['roles']['damage']['games_played'] - before_stat['roles']['damage']['games_played']
        return nb_game_tank + nb_game_supp + nb_game_dps

    def compute_nb_game_played(self, before_game: int, after_game: int) -> int:
        """
        Compute number of games played between two sessions
        :param before_game:
        :param after_game:
        :return:
        """
        return after_game - before_game

    def compute_kda(self, eliminations, deaths, assists) -> float:
        """
        Compute KDA
        :param eliminations:
        :param deaths:
        :param assists:
        :return:
        """
        if deaths == 0:
            return eliminations + assists
        else:
            return (eliminations + assists) / deaths

    @staticmethod
    def format_stats(stats: list) -> dict:
        """
        Format stats in a dict
        :param stats:
        :return:
        """
        returned_dict = {}
        for stat in stats:
            returned_dict[stat['player']] = stat
        return returned_dict

    @staticmethod
    def format_battletag(battletag: str) -> str:
        """
        Format battletag to be used in API request
        :param battletag:
        :return:
        """
        return battletag.replace('#', '-')

    @staticmethod
    def compute_win_count_by_winrate_and_games(winrate, games_played) -> int:
        """
        Compute win count by winrate and games played
        :param winrate:
        :param games_played:
        :return:
        """
        return round(winrate * games_played / 100)

    @staticmethod
    def compute_winrate(wins, games_played) -> float:
        """
        Compute winrate
        :param wins:
        :param games_played:
        :return:
        """
        return round(wins / games_played * 100, 2)
