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

# REGEX : @nick_bot rename @someone en new_name
RENAME_REGEX = re.compile('<@\d+> rename <@\d+> en (.*)')
# REGEX : @nick_bot ajoute mon battletag
ADD_BATTLETAG_REGEX = re.compile('<@\d+> add battletag (.*)')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

        match_rename = re.match(RENAME_REGEX, message.content)
        new_name = match_rename.group(1)

        match_add_battletag = re.search(ADD_BATTLETAG_REGEX, message.content)
        battletag = match_add_battletag.group(1)

    if message.mentions:
        mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
        if client.user.id in mentioned_ids:
            mentioned_ids.remove(client.user.id)
            return_message = ''
            if new_name:
                return_message = await renaming(new_name, mentioned_ids)
            elif battletag:
                return_message = await add_battletag(battletag, message.author, mentioned_ids)
            await message.channel.send(return_message)


@client.event
async def on_presence_update(member, before, after):
    print(member)
    for activity in after.activities:
        print(activity.name)


async def add_battletag(battletag: str, user, mentioned_ids):
    print(battletag)


async def renaming(new_name: str, mentioned_ids: list) -> str:
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
    else:
        return 'Bad command :('


client.run(config['token'])
