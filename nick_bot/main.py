# This example requires the 'message_content' intent.
import sys

import discord
import re
from discord import Message
from discord import Member
from ruamel.yaml import YAML

from nick_bot.db.OverwatchDB import OverwatchDB

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

conf_file = open("../config/config.yaml")

yaml = YAML()
config = yaml.load(conf_file)

overwatchDatabase = OverwatchDB(config['database'])

# REGEX : @nick_bot renomme @someone en new_name
RENAME_REGEX = re.compile('<@\d+>\s+renomme\s+<@\d+>\s+en\s+(.*)')
# REGEX : @nick_bot ajoute mon <battletag>
ADD_BATTLETAG_REGEX = re.compile('<@\d+>\s+ajoute\s+mon\s+battletag\s+(.*)')
# REGEX : @nick_bot retire mon <battletag>
REMOVE_BATTLETAG_REGEX = re.compile('<@\d+>\s+retire\s+mon\s+battletag\s+(.*)')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    match_rename = re.match(RENAME_REGEX, message.content)
    match_add_battletag = re.match(ADD_BATTLETAG_REGEX, message.content)
    match_remove_battletag = re.match(REMOVE_BATTLETAG_REGEX, message.content)

    if message.mentions:
        mentioned_ids = list(map(lambda mention: mention.id, message.mentions))
        if client.user.id in mentioned_ids:
            mentioned_ids.remove(client.user.id)
            return_message = 'Je ne sais pas quoi répondre.'
            if match_rename:
                new_name = match_rename.group(1)
                return_message = await renaming(new_name, mentioned_ids)
            elif match_add_battletag:
                battletag = match_add_battletag.group(1)
                return_message = await add_battletag(battletag, message.author.name)
            elif match_remove_battletag:
                battletag = match_remove_battletag.group(1)
                return_message = await remove_battletag(battletag, message.author.name)
            await message.channel.send(return_message)


@client.event
async def on_presence_update(before: Member, after: Member):
    member_name = after.name
    intersting_activities = ['overwatch']

    was_ingame = False
    now_ingame = False

    for activity in before.activities:
        if activity.name in intersting_activities:
            was_ingame = True

    for activity in before.activities:
        if activity.name in intersting_activities:
            now_ingame = True

    if not was_ingame and now_ingame:
        print(f'{member_name} is now in game !')
    elif was_ingame and not now_ingame:
        print(f'{member_name} is leaving the game !')


async def add_battletag(battletag: str, username: str):
    status = overwatchDatabase.add_battletag(username, battletag)
    if status == 1:
        return f'Le battletag a été ajouté'
    else:
        return f'Tu as déjà ajouté ce battletag'


async def remove_battletag(battletag: str, username: str):
    status = overwatchDatabase.remove_battletag(username, battletag)
    if status == 1:
        return f'Le battletag a été retiré'
    else:
        return f'Tu n\'as aucun battletag'


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
                    return f'Je n\'ai pas les droits de renommage {old_name}'

        return f'Renommage de {old_name} en {new_name}'
    else:
        return 'Bad command :('


client.run(config['token'])
