# This example requires the 'message_content' intent.
import sys

import discord
import re
from discord import Message
from ruamel.yaml import YAML

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

conf_file = open("/config/config.yaml")

yaml = YAML()
config = yaml.load(conf_file)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.mentions:
        mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
        if client.user.id in mentioned_ids:
            mentioned_ids.remove(client.user.id)
            return_message = await do_action(message, mentioned_ids)
            await message.channel.send(return_message)


async def do_action(message: Message, mentioned_ids: list) -> str:

    match = re.search('<@\d+> rename <@\d+> en (.*)', message.content)

    new_name = match.group(1)

    if new_name:
        members = client.get_all_members()
        for member in members:
            for id in mentioned_ids:
                if member.id == id:
                    old_name = member.name
                    print(f'FOUND IT ! {old_name}')
                    try:
                        await member.edit(nick=new_name)
                    except Exception:
                        return f'Je n\'ai pas les droits de rename {old_name}'

        return f'Renommage de {old_name} en {new_name}'
    else :
        return 'Bad command :('


client.run(config['token'])