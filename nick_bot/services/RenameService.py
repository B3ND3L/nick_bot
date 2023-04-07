from discord import Client


class RenameService:

    def __init__(self, discord_client: Client) -> str:
        self._discord_client = discord_client

    def renaming(self, new_name: str, mentioned_ids: list) -> str:
        members = self._discord_client.get_all_members()
        for member in members:
            for id in mentioned_ids:
                if member.id == id:
                    old_name = member.name
                    print(f'FOUND IT ! {old_name}')
                    try:
                        member.edit(nick=new_name)
                    except Exception:
                        return f'Je n\'ai pas les droits de renommage {old_name}'

            return f'Renommage de {old_name} en {new_name}'