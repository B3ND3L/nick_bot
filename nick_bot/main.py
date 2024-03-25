import discord
import logging

from discord import Member
from discord import Message
from ruamel.yaml import YAML

from nick_bot.services.MessageService import MessageService
from nick_bot.services.RenameService import RenameService

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

yaml = YAML()
config = yaml.load(open("../config/config.yaml"))

rename_service = RenameService(client)
message_service = MessageService(rename_service)

logger = logging.getLogger('discord')

@client.event
async def on_ready():
    """
    When the bot is ready
    :return:
    """
    logger.info(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message: Message):
    """
    When a message is received
    :param message:
    :return:
    """
    if message.author == client.user:
        return
    response = await message_service.read_message(client.user.id, message)
    if response:
        await message.channel.send(response)

client.run(config['token'])
