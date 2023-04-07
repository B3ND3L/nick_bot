import requests


class OverwatchApi:
    __PLAYER_STATS_PATH = '/players/{player}/stats/summary'

    def __init__(self, config):
        self._request_client = requests
        self.api_url = config['url']

    def get_stat(self, player: str) -> dict:
        url = self.api_url + self.__PLAYER_STATS_PATH.format(player=player)
        return self._request_client.get(url).json()
