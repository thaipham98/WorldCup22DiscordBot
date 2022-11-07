import discord
from replit import db
import os
import random
from migration import Migration

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
token = os.getenv('TOKEN')

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))


@client.event
async def on_message(message):
    print('Message is', message)
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    id = 727084338675449906
    print('username is', client.get_user(id))
    print(f'Message {user_message} by {username} on {channel}')

    if message.author == client.user:
        return

    if channel == "random":
        if user_message.lower() == "hello" or user_message.lower() == "hi":
            await message.channel.send(f'Hello {username}')
            return
        elif user_message.lower() == "bye":
            await message.channel.send(f'Bye {username}')
        elif user_message.lower() == "tell me a joke":
            jokes = [" Can someone please shed more\
            light on how my lamp got stolen?",
                     "Why is she called llene? She\
                     stands on equal legs.",
                     "What do you call a gazelle in a \
                     lions territory? Denzel."]
            await message.channel.send(random.choice(jokes))
          
#print("db_URL:", os.getenv("REPLIT_DB_URL"))
#client.run('MTAzNDAxMTM2Mjk5MDUxMDEyMQ.Gqm_Lx.LrvyQ-lAvGMx-_ZuFfjtC_K25pRSPT1jDFrzZI')



db.clear()
db["match"] = {}
#match_table = db["match"]
migration = Migration()
migration.insert_matches_data()
#print(db.items())
keys = db.keys()
#dict = db.items()
print(keys)
print(db['match'])
#print(dict['match'])
#print(db.keys)