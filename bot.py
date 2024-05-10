# bot.py
import os
import discord
from discord import app_commands
from database import backup_database
from cron_jobs import setup_cron_jobs
from commands import setup_commands
from events_api import Event_API

token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class CustomClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.events_api = Event_API()  # Initialize here and use as needed
        self.synced = False

    async def on_ready(self):
        print(f"We have logged in as {self.user}.")
        if not self.synced:
            await self.tree.sync()
            self.synced = True
            setup_commands(self.tree, self, self.events_api)  # Pass client and API to commands

        #setup_cron_jobs(self)
        #backup_database()

client = CustomClient()
client.run(token)
