import os
import discord

TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID'))
ADMIN_ID_1 = int(os.getenv('ADMIN_ID_1'))
ADMIN_ID_2 = int(os.getenv('ADMIN_ID_2'))
REGISTER_CHANNEL_ID = int(os.getenv('REGISTER_CHANNEL_ID'))
BOT_ID = int(os.getenv('BOT_ID'))
BET_CHANNEL_NAME = 'Bet Channels'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True