import re

from discord import Message, Member, Client
from nick_bot.services.RenameService import RenameService
from nick_bot.services.TimeoutService import TimeoutService


class MessageHandler:

    """
    Service to manage the messages
    """

    # REGEX : @nick_bot renomme @someone en new_name
    __RENAME_REGEX = re.compile('<@\d+>\s+(renomme|rename)\s+<@\d+>\s+(en|to)\s+(.*)')

    #REGEX : @nick_bot timeout @someone
    __TIMEOUT_REGEX = re.compile('<@\d+>\s+(timeout)\s+<@\d+>')

    #REGEX : @nick_bot help
    __HELP_REGEX = re.compile('<@\d+>\s+(help)')

    def __init__(self, client: Client):
        """
        Constructor
        :param rename_service:
        """
        self._discord_client = client
        self._rename_service = RenameService(client)
        self._timeout_service = TimeoutService(client)

    async def handle_message(self, client_id: int, message: Message) -> str:
        """
        Read a message and return a response
        :param client_id:
        :param message:
        :return:
        """

        content = message.content
        match_rename = re.match(self.__RENAME_REGEX, content)
        match_timeout = re.match(self.__TIMEOUT_REGEX, content)
        match_help = re.match(self.__HELP_REGEX, content)

        if message.mentions:
            if match_rename:
                mentionned_member = self.get_metionned_member(message.mentions)
                new_name = match_rename.group(3)
                return_message = await self._rename_service.renaming(new_name, mentionned_member)
            elif match_timeout:
                mentionned_member = self.get_metionned_member(message.mentions)
                return_message = self._timeout_service.timeout_user(mentionned_member)
            elif match_help:
                return_message = self.get_default_answer()

            if return_message :
                await message.channel.send(return_message)

    @staticmethod
    def get_default_answer():
        return '''
Voici les commandes que tu peux tapper:
Pour recevoir de l'aide :
`help`
Pour renommer quelqu'un:
`renomme @name en nouveau_nom`
                    '''

    def get_metionned_member(self, mentions: list[Member]) -> Member | None:
        mentioned_ids = list(map(lambda mention: mention.id, mentions))
        mentioned_ids.remove(self._discord_client.user.id)
        members = self._discord_client.get_all_members()
        for member in members:
            for mention_id in mentioned_ids:
                if member.id == mention_id:
                    return member
        return None
