from datetime import timedelta

from discord import Client, Member


class TimeoutService:

    __TIMEOUT_DURATION: int = 15

    def __init__(self, discord_client: Client):
        self._discord_client = discord_client


    def timeout_user(self, member: Member):
        member.timeout(timedelta(seconds=self.__TIMEOUT_DURATION))
        return f'{member.name} ne peut plus envoyer de message pendant {self.__TIMEOUT_DURATION} secondes.'