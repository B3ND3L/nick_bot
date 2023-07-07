import requests


class OverwatchApi:

    """
    Overwatch API Connector
    """

    __PLAYER_SUMMARY_STATS_PATH = '/players/{player}/stats/summary'
    __ROLES_PATH = '/roles'
    __HEROES_PATH = '/heroes?role={role}'

    def __init__(self, config):
        """
        Constructor
        :param config:
        """
        self._request_client = requests
        self.api_url = config['url']

    def get_summary_stats(self, player: str) -> dict:
        """
        Get the summary stats of a player
        :param player:
        :return:
        """
        url = self.api_url + self.__PLAYER_SUMMARY_STATS_PATH.format(player=player)
        return self._request_client.get(url).json()

    def get_roles(self) -> dict:
        """
        Get the roles
        :return:
        """
        url = self.api_url + self.__ROLES_PATH
        return self._request_client.get(url).json()

    def get_heroes_by_role(self, role: str):
        """
        Get the heroes by role
        :param role:
        :return:
        """
        url = self.api_url + self.__HEROES_PATH.format(role=role)
        return self._request_client.get(url).json()
