import discord
from discord import app_commands
from replit import db
import os
import random
from migration import Migration

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#client = commands.Bot(intents=discord.Intents.all())
#client = discord.Client(intents=intents)
token = os.getenv('TOKEN')
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

# @client.event
# async def on_ready():
#     print("Logged in as a bot {0.user}".format(client))
#     await client.tree.sync()

def from_admin(interaction):
  return interaction.channel.name == 'admin' and interaction.channel_id == int(os.getenv('ADMIN_CHANNEL_ID')) and interaction.user.id == int(os.getenv('ADMIN_ID'))

@tree.command(name="create", description="Create a new player")
async def create_player(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="create!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command!', ephemeral=True)
      #channel = client.get_channel(channel_id)
      #await channel.send('This is an admin command. You are not allowed to perform this command!')
      #await interaction.response.send_message()

@tree.command(name="delete", description="Delete an existing player")
async def delete_player(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="delete!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command!', ephemeral=True)

@tree.command(name="update", description="Update scores")
async def update_scores(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="update!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command!', ephemeral=True)

@tree.command(name="remind", description="Remind players")
async def remind_players(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if from_admin(interaction):
      # channel = interaction.channel
      # channel_id = interaction.channel_id
      # user.id = interaction.user
      await interaction.response.send_message(content="remind!")
    else:
      await interaction.response.send_message(content='This is an admin command. You are not allowed to perform this command!', ephemeral=True)

@tree.command(name="bet", description="Choose a betting option")
async def bet(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Betting')
    await interaction.response.send_message(content='betting', ephemeral=True)

@tree.command(name="me", description="Show your record")
async def view_me(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Me')
    await interaction.response.send_message(content='me', ephemeral=True)

@tree.command(name="record", description="Show all record")
async def view_all_record(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('All record')
    await interaction.response.send_message(content='view all records', ephemeral=True)

@tree.command(name="help", description="Show rules and commands")
async def help(interaction: discord.Interaction):
    # channel_id = interaction.channel_id
    # channel = client.get_channel(channel_id)
    # await channel.send('Help')
    await interaction.response.send_message(content='help', ephemeral=True)

    
  



# @client.event
# async def on_message(message):
#     print('Message is', message)
#     username = str(message.author).split("#")[0]
#     channel = str(message.channel.name)
#     user_message = str(message.content)


#     channel_id = message.channel.id
#     channel_name = message.channel.name
#     author_id = message.author.id
#     print(channel_id)
#     print(type(channel_id))
#     print(channel_name)
#     print(type(channel_name))
#     print(author_id)
#     print(type(author_id))
#     id = 727084338675449906
#     print('username is', client.get_user(id))
#     print(f'Message {user_message} by {username} on {channel}')

#     if message.author == client.user:
#         return

#     if channel == "random":
#         if user_message.lower() == "hello" or user_message.lower() == "hi":
#             await message.channel.send(f'Hello {username}')
#             return
#         elif user_message.lower() == "bye":
#             await message.channel.send(f'Bye {username}')
#         elif user_message.lower() == "tell me a joke":
#             jokes = [" Can someone please shed more\
#             light on how my lamp got stolen?",
#                      "Why is she called llene? She\
#                      stands on equal legs.",
#                      "What do you call a gazelle in a \
#                      lions territory? Denzel."]
#             await message.channel.send(random.choice(jokes))
          
#print("db_URL:", os.getenv("REPLIT_DB_URL"))
client.run(token)



#db.clear()
#db["match"] = {}
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