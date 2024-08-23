import discord
import logging

from discord import Member
from discord import Message
from ruamel.yaml import YAML

from nick_bot.services.MessageHandler import MessageHandler

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

yaml = YAML()
config = yaml.load(open("../config/config.yaml"))

message_service = MessageHandler(client)

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
    await message_service.handle_message(client.user.id, message)

client.run(config['token'])
