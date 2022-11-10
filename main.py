import discord
from discord import app_commands
from replit import db
import os
import random
from migration import Migration
from user_table import UserTable
from user import User
from events_api import Event_API
import datetime
from bet_model import BetModel

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#client = commands.Bot(intents=discord.Intents.all())
#client = discord.Client(intents=intents)
token = os.getenv('TOKEN')
bot_id = int(os.getenv('BOT_ID'))
guild_id = int(os.getenv('GUILD_ID'))
events_api = Event_API()
bet_model = BetModel()
#tree = app_commands.CommandTree(client)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents =intents)
        self.synced = False #we use this so the bot doesn't sync commands more than once

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #check if slash commands have been synced 
            await tree.sync() #guild specific: leave blank if global (global registration can take 1-24 hours)
            self.synced = True
        print(f"We have logged in as {self.user}.")

client = aclient()
tree = app_commands.CommandTree(client)
#db["user"].clear()
user_table = UserTable()


text_channel_name = 'Text Channels'

# @client.event
# async def on_ready():
#     print("Logged in as a bot {0.user}".format(client))
#     await client.tree.sync()

async def create_private_channel(interaction, user_id, channel_name):
      user = client.get_user(int(user_id))
      bot = client.get_user(bot_id)
      guild = interaction.guild
      category = discord.utils.get(guild.categories, name=text_channel_name)
      overwrites = {
          guild.default_role: discord.PermissionOverwrite(read_messages=False),
          user: discord.PermissionOverwrite(view_channel=True),
          bot: discord.PermissionOverwrite(view_channel=True)
      }

      guild = interaction.guild
      category = discord.utils.get(guild.categories, name=text_channel_name)

      channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
      #print(type(user))
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="Channel {0} is created for {1}".format(channel_name, user.name))
      return user, channel

def from_admin(interaction):
  return interaction.channel.name == 'admin' and interaction.channel_id == int(os.getenv('ADMIN_CHANNEL_ID')) and interaction.user.id == int(os.getenv('ADMIN_ID'))

@tree.command(name="create", description="Create a new player")
async def create_player(interaction: discord.Interaction, user_id : str, channel_name : str):
    #user_id = int(user_id)
    guild = client.get_guild(guild_id)
    if guild.get_member(int(user_id)) is None: 
      await interaction.response.send_message(content='User with id = {0} does not exist in the server'.format(user_id))
      return
  
    if from_admin(interaction):
      user_entity = user_table.view_user(user_id)
      if user_entity is not None:
        await interaction.response.send_message(content='User with id = {0} already existed'.format(user_id))
      else:
        user, user_channel = await create_private_channel(interaction, user_id, channel_name)
        user_entity = User(user.id, user.name, user_channel.id, user_channel.name, 0, 0, 0, 0, {})
        user_table.add_user(user_entity)
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.', ephemeral=True)
      #channel = client.get_channel(channel_id)
      #await channel.send('This is an admin command. You are not allowed to perform this command!')
      #await interaction.response.send_message()

async def kick_user(interaction, user_id):
  user_entity = user_table.view_user(user_id)
  if user_entity is None:
    print("There is no user with id = {0} a".format(user_id))
    return 0
    
  channel_id = user_entity.channel_id
  user_table.delete_user(user_id)
  
  user = client.get_user(int(user_id))
  await interaction.guild.kick(user)
  print("channel_id=", channel_id)
  return channel_id

async def delete_user_channel(user_channel_id):
  channel = client.get_channel(user_channel_id)
  await channel.delete()

@tree.command(name="delete", description="Delete an existing player")
async def delete_player(interaction: discord.Interaction, user_id : str):
    #user_id = int(user_id)
    guild = client.get_guild(guild_id)
    if guild.get_member(int(user_id)) is None: 
      await interaction.response.send_message(content='User with id = {0} does not exist in the server'.format(user_id))
      return
    #channel_id = interaction.channel_id
    print("from delete_player", db['user'])
    if from_admin(interaction):
      user_channel_id = await kick_user(interaction, user_id)
      if user_channel_id:
        await delete_user_channel(user_channel_id)
        await interaction.response.send_message(content="User with id = {0} is deleted".format(user_id))
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      else:
        await interaction.response.send_message(content="There is no user with id = {0}".format(user_id))
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.', ephemeral=True)

@tree.command(name="update", description="Update scores")
async def update_scores(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="update!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help', ephemeral=True)

@tree.command(name="remind", description="Remind players")
async def remind_players(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="remind!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help', ephemeral=True)

@tree.command(name="bet", description="Choose a betting option")
async def bet(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Betting')
    current_time = datetime.datetime.now()
    today = str(current_time.year) + str(current_time.month) + str(current_time.day)
    daily_matches = events_api.get_upcoming_daily_events("20221118")
    daily_bet = bet_model.from_daily_matches_to_daily_bet(daily_matches)

    if len(daily_bet) == 0:
      await interaction.response.send_message(content='There are no matches today.', ephemeral=True)
      return
    print(daily_bet)
    await interaction.response.send_message(content='betting', ephemeral=True)

@tree.command(name="me", description="Show your record")
async def view_me(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Me')
    user_id = interaction.user.id
    user = user_table.view_user(str(user_id))
    record = user.to_record()
    print(record)
    
    await interaction.response.send_message(content='me', ephemeral=True)

@tree.command(name="record", description="Show all records")
async def view_all_record(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('All record')
    users = user_table.view_all()
    records = [user.to_record() for user in users]
    print(records)
    #TODO ranking
    await interaction.response.send_message(content='view all records', ephemeral=True)

@tree.command(name="help", description="Show rules and commands")
async def help(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Help')
    guideline = "/bet: view upcoming matches and choose betting option \n/me: view your current record \n/record: view all records \n/help: view available commands"
    await interaction.response.send_message(content=guideline, ephemeral=True)

#print(db["user"])
#print(db['match'])
#print(user_table.table)
client.run(token)



#db.clear()
#db["match"] = {}
#db["user"] = {}

#match_table = db["match"]
#migration = Migration()
#migration.insert_matches_data()
#print(db.items())
#keys = db.keys()
#dict = db.items()
#print(keys)
#print(db['match'])
#print(dict['match'])
#print(db.keys)