import re

from discord import Message

from nick_bot.services.BattletagService import BattletagService
from nick_bot.services.RenameService import RenameService


class MessageService:
    # REGEX : @nick_bot renomme @someone en new_name
    __RENAME_REGEX = re.compile('<@\d+>\s+(renomme|rename)\s+<@\d+>\s+(en|to)\s+(.*)')
    # REGEX : @nick_bot ajoute mon <battletag>
    __ADD_BATTLETAG_REGEX = re.compile('<@\d+>\s+(add|ajoute)\s+(my|mon)\s+battletag\s+(.*)')
    # REGEX : @nick_bot retire mon <battletag>
    __REMOVE_BATTLETAG_REGEX = re.compile('<@\d+>\s+(remove|retire)\s+(my|mon)\s+battletag\s+(.*)')
    # REGEX : @nick_bot help
    __HELP = re.compile('<@\d+>\s+(help|aide)')

    def __init__(self, battletag_service: BattletagService, rename_service: RenameService):
        self._battletag_service = battletag_service
        self._rename_service = rename_service

    async def read_message(self, client_id: int, message: Message) -> str:

        content = message.content
        match_rename = re.match(self.__RENAME_REGEX, content)
        match_add_battletag = re.match(self.__ADD_BATTLETAG_REGEX, content)
        match_remove_battletag = re.match(self.__REMOVE_BATTLETAG_REGEX, content)
        match_help = re.match(self.__HELP, content)

        return_message = 'Je ne sais pas quoi répondre.'

        if message.mentions:
            mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
            if client_id in mentioned_ids:
                mentioned_ids.remove(client_id)
                if match_rename:
                    new_name = match_rename.group(3)
                    return_message = await self._rename_service.renaming(new_name, mentioned_ids)
                elif match_add_battletag:
                    battletag = await match_add_battletag.group(3)
                    return_message = self._battletag_service.add_battletag(battletag, message.author.name)
                elif match_remove_battletag:
                    battletag = await match_remove_battletag.group(3)
                    return_message = self._battletag_service.remove_battletag(battletag, message.author.name)
                elif match_help:
                    return_message = '''
Voici les commandes que tu peux tapper:
Pour recevoir de l'aide :
`help`
Pour renommer quelqu'un:
`renomme @name en nouveau_nom`
Pour ajouter un battletag:
`ajoute battletag MONBATTLETAG#1234`
Pour retirer un battletag:
`retire battletag MONBATTLETAG#1234`
                    '''
                return return_message
