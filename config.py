import os
import discord

TOKEN = os.getenv('TOKEN')
BID_CHANNEL_ID = int(os.getenv('BID_CHANNEL_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))
ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID'))
ADMIN_ID_1 = int(os.getenv('ADMIN_ID_1'))
ADMIN_ID_2 = int(os.getenv('ADMIN_ID_2'))
ADMIN_ID_3 = int(os.getenv('ADMIN_ID_3'))
REGISTER_CHANNEL_ID = int(os.getenv('REGISTER_CHANNEL_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
UPDATE_CHANNEL_ID = int(os.getenv('UPDATE_CHANNEL_ID'))
LEADERBOARD_CHANNEL_ID = int(os.getenv('LEADERBOARD_CHANNEL_ID'))
MATCH_RESULTS_CHANNEL_ID = int(os.getenv('MATCH_RESULTS_CHANNEL_ID'))
                                  
BOT_ID = int(os.getenv('BOT_ID'))
BET_CHANNEL_NAME = 'Bet Channels'
VERIFY_CHANNEL_NAME = 'Verify'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
