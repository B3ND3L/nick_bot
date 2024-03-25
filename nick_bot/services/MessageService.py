import re

from discord import Message
from nick_bot.services.RenameService import RenameService


class MessageService:

    """
    Service to manage the messages
    """

    # REGEX : @nick_bot renomme @someone en new_name
    __RENAME_REGEX = re.compile('<@\d+>\s+(renomme|rename)\s+<@\d+>\s+(en|to)\s+(.*)')
    # REGEX : @nick_bot help
    __HELP = re.compile('<@\d+>\s+(help|aide)')

    def __init__(self,rename_service: RenameService):
        """
        Constructor
        :param rename_service:
        """
        self._rename_service = rename_service

    async def read_message(self, client_id: int, message: Message) -> str:
        """
        Read a message and return a response
        :param client_id:
        :param message:
        :return:
        """

        content = message.content
        match_rename = re.match(self.__RENAME_REGEX, content)
        match_help = re.match(self.__HELP, content)

        return_message = 'Je ne sais pas quoi répondre.'

        if message.mentions:
            mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
            if client_id in mentioned_ids:
                mentioned_ids.remove(client_id)
                if match_rename:
                    new_name = match_rename.group(3)
                    return_message = await self._rename_service.renaming(new_name, mentioned_ids)
                elif match_help:
                    return_message = '''
Voici les commandes que tu peux tapper:
Pour recevoir de l'aide :
`help`
Pour renommer quelqu'un:
`renomme @name en nouveau_nom`
                    '''
                return return_message
