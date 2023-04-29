import discord
from discord import Member
from discord import Message
from ruamel.yaml import YAML

from nick_bot.services.BattletagService import BattletagService
from nick_bot.services.MessageService import MessageService
from nick_bot.services.RenameService import RenameService
from nick_bot.services.SessionService import SessionService

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

yaml = YAML()
config = yaml.load(open("../config/config.yaml"))

battletag_service = BattletagService(config)
rename_service = RenameService(client)
message_service = MessageService(battletag_service, rename_service)
session_service = SessionService(config, battletag_service)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    response = await message_service.read_message(client.user.id, message)
    if response:
        await message.channel.send(response)


@client.event
async def on_presence_update(before: Member, after: Member):
    session_service.on_presence(before, after)


client.run(config['token'])
