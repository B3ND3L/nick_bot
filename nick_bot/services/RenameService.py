from discord import Client


class RenameService:

    def __init__(self, discord_client: Client) -> str:
        self._discord_client = discord_client

    async def renaming(self, new_name: str, mentioned_ids: list) -> str:
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
                        message = f'Je n\'ai pas les droits de renommage {old_name}'
        return message
