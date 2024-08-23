from discord import Client, Member


class RenameService:

    """
    Service to manage the renaming
    """

    def __init__(self, discord_client: Client) -> str:
        """
        Constructor
        :param discord_client:
        """
        self._discord_client = discord_client

    async def renaming(self, new_name: str, mentionned_member: Member) -> str:
        """
        Rename a user
        :param new_name:
        :param mentionned_member:
        :return:
        """
        message = 'Impossible de renommer l\'utilisateur'
        try:
            old_name = mentionned_member.name
            await mentionned_member.edit(nick=new_name)
            message = f'Renommage de {old_name} en {new_name}'
        except Exception:
            #affiche l'erreur dans la console
            print(Exception)
            message = f'Je n\'ai pas les droits de renommage {old_name}'
        return message
