from discord import Client


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

    async def renaming(self, new_name: str, mentioned_ids: list) -> str:
        """
        Rename a user
        :param new_name:
        :param mentioned_ids:
        :return:
        """
        message = 'Impossible de renommer l\'utilisateur'
        members = self._discord_client.get_all_members()
        for member in members:
            old_name = ''
            for id in mentioned_ids:
                if member.id == id:
                    old_name = member.name
                    try:
                        await member.edit(nick=new_name)
                        message = f'Renommage de {old_name} en {new_name}'
                    except Exception:
                        #affiche l'erreur dans la console
                        print(Exception)
                        message = f'Je n\'ai pas les droits de renommage {old_name}'
        return message
