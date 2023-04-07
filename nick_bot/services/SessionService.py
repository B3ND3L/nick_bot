from discord import Member

from nick_bot.datas.OverwatchApi import OverwatchApi
from nick_bot.services.BattletagService import BattletagService


class SessionService:

    def __init__(self, config: dict, battletag_service: BattletagService):
        self._battletag_service = battletag_service
        self._overwatch_api = OverwatchApi(config)

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

        print(f'était en game {was_ingame} || est en game {now_ingame}')

        if not was_ingame and now_ingame:
            self.session_start(member_name)
        elif was_ingame and not now_ingame:
            self.session_stop(member_name)

    def session_start(self, discord_name):
        print(f'{discord_name} is now in game !')
        self.get_stat(discord_name)

    def session_stop(self, discord_name):
        print(f'{discord_name} is leaving the game !')
        self.get_stat(discord_name)

    def get_stat(self, discord_name: str):
        battletags = self._battletag_service.get_battletags(discord_name)
        for battletag in battletags:
            player_id = self.format_battletag(battletag)
            stats = self._overwatch_api.get_stat(player_id)
            print(stats)

    def format_battletag(self, battletag:str) -> str:
        return battletag.replace('#', '-')