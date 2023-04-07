import re

from discord import Message

from nick_bot.services.BattletagService import BattletagService
from nick_bot.services.RenameService import RenameService


class MessageService:
    # REGEX : @nick_bot renomme @someone en new_name
    __RENAME_REGEX = re.compile('<@\d+>\s+renomme\s+<@\d+>\s+en\s+(.*)')
    # REGEX : @nick_bot ajoute mon <battletag>
    __ADD_BATTLETAG_REGEX = re.compile('<@\d+>\s+ajoute\s+mon\s+battletag\s+(.*)')
    # REGEX : @nick_bot retire mon <battletag>
    __REMOVE_BATTLETAG_REGEX = re.compile('<@\d+>\s+retire\s+mon\s+battletag\s+(.*)')

    def __init__(self, battletag_service: BattletagService, rename_service: RenameService):
        self._battletag_service = battletag_service
        self._rename_service = rename_service

    def read_message(self, client_id: int, message: Message) -> str:

        content = message.content
        match_rename = re.match(self.__RENAME_REGEX, content)
        match_add_battletag = re.match(self.__ADD_BATTLETAG_REGEX, content)
        match_remove_battletag = re.match(self.__REMOVE_BATTLETAG_REGEX, content)

        return_message = 'Je ne sais pas quoi répondre.'

        if message.mentions:
            mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
            if client_id in mentioned_ids:
                mentioned_ids.remove(client_id)
                if match_rename:
                    new_name = match_rename.group(1)
                    return_message = self._rename_service.renaming(new_name, mentioned_ids)
                elif match_add_battletag:
                    battletag = match_add_battletag.group(1)
                    return_message = self._battletag_service.add_battletag(battletag, message.author.name)
                elif match_remove_battletag:
                    battletag = match_remove_battletag.group(1)
                    return_message = self._battletag_service.remove_battletag(battletag, message.author.name)

        return return_message
