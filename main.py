import discord
import asyncio
from discord import app_commands
from discord.ui import Select, View, Button
from replit import db
import os
import random
from migration import Migration
from user_table import UserTable
from match_table import MatchTable
from user import User
from events_api import Event_API
import datetime
from bet_model import BetModel
from bet_type import BetType
from updator import Updator
import copy
from result import get_result_shorthand
import pytz
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#db['user'].clear()
# db['match'].clear()
#client = commands.Bot(intents=discord.Intents.all())
#client = discord.Client(intents=intents)
token = os.getenv('TOKEN')
bot_id = int(os.getenv('BOT_ID'))
guild_id = int(os.getenv('GUILD_ID'))
events_api = Event_API()


def get_user_table():
  return UserTable()


def get_match_table():
  return MatchTable()


class aclient(discord.Client):

  def __init__(self):
    super().__init__(intents=intents)
    self.synced = False  #we use this so the bot doesn't sync commands more than once

  async def on_ready(self):
    await self.wait_until_ready()
    if not self.synced:  #check if slash commands have been synced
      await tree.sync(
      )  #guild specific: leave blank if global (global registration can take 1-24 hours)
      self.synced = True
    print(f"We have logged in as {self.user}.")


client = aclient()
tree = app_commands.CommandTree(client)
#db["user"].clear()

migration = Migration()


@tasks.loop(seconds=5.0)
async def test():
  print("test")
  channel = client.get_channel(1042862934482763917)  #channel id here
  if channel is not None:
    await channel.send("test tset test")


# @client.event
# async def on_ready():
#   # test.start()
#   remind_cron_job.start()

# @tasks.loop(seconds=60*60*3)
# def update_score_cron_job():
#   # call API
#   # update to DB
#   pass


@tasks.loop(hours=3)
async def remind_cron_job():
  channel = client.get_channel(int(
    os.getenv('ADMIN_CHANNEL_ID')))  #channel id here
  users = get_user_table().view_all()
  daily_bet = get_daily_bet()

  if len(daily_bet) == 0:
    await channel.send("No matches")
    return

  embed_contents = []
  for bet_detail in daily_bet:
    match_id = bet_detail.match_id
    match = get_match_table().view_match(str(match_id))
    match_info = match.to_payload()
    embed_contents.append(generate_bet_item(bet_detail, match_info))

  for user in users:
    channel = client.get_channel(user.channel_id)  #channel id here
    if channel is not None:
      await channel.send(
        "Nhắc nhẹ: Hnay có {0} trận nhé. Mấy ông thần vào /bet hộ cái".format(
          len(daily_bet)))
      for embed in embed_contents:
        await channel.send(embed=embed)
  channel.send("Automatically sent")


# user1 = User("12321", "a", "b",
#                          "c", 1, 2, 0, 10000, {})
# user2 = User("1321", "fadsf", "b",
#                          "c", 2, 2, 0, 10000, {})
# user3 = User("12321321", "fdafdfax", "b",
#                          "c", 4, 2, 0, 50000, {})
# user4 = User("123212341", "adfweqr", "b",
#                          "fadsva", 4, 3, 0, 50000, {})
# user5 = User("123213113", "adfbjkla", "b",
#                          "c", 4, 3, 0, 50000, {})
# user6 = User("1232131133213", "adfbjkla", "b",
#                          "c", 4, 3, 0, 60000, {})
# user7 = User("123213113434", "adfbjkla", "b",
#                          "c", 4, 3, 1, 60000, {})
# user_table.add_user(user1)
# user_table.add_user(user2)
# user_table.add_user(user3)
# user_table.add_user(user4)
# user_table.add_user(user5)
# user_table.add_user(user6)
# user_table.add_user(user7)
#print(db["user"])

bet_channel_name = 'Bet Channels'


async def create_private_channel(interaction, user_id, channel_name):
  user = client.get_user(int(user_id))
  bot = client.get_user(bot_id)
  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=bet_channel_name)
  overwrites = {
    guild.default_role: discord.PermissionOverwrite(read_messages=False),
    user: discord.PermissionOverwrite(view_channel=True),
    bot: discord.PermissionOverwrite(view_channel=True)
  }

  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=bet_channel_name)

  channel = await guild.create_text_channel(channel_name,
                                            overwrites=overwrites,
                                            category=category)

  return user, channel


def get_daily_bet():
  current_time = datetime.datetime.now()
  today = "{:02d}".format(current_time.year) + "{:02d}".format(
    current_time.month) + "{:02d}".format(current_time.day)
  # daily_matches = events_api.get_upcoming_daily_events(today)
  # TODO: replace this temp date with today date above
  #daily_matches = events_api.get_upcoming_daily_events(today)
  daily_matches = events_api.get_upcoming_daily_events('20221121')
  bet_model = BetModel()

  #print(daily_matches)
  daily_bet = bet_model.from_daily_matches_to_daily_bet(daily_matches)
  return daily_bet


def from_right_user(interaction):
  user_id = str(interaction.user.id)
  user = get_user_table().view_user(user_id)
  if user is None:
    return False
  return interaction.channel.id == user.channel_id


def from_admin(interaction):
  return interaction.channel.name == 'admin' and interaction.channel_id == int(
    os.getenv('ADMIN_CHANNEL_ID')) and (
      interaction.user.id == int(os.getenv('ADMIN_ID_1'))
      or interaction.user.id == int(os.getenv('ADMIN_ID_2')))


@tree.command(name="clear", description="Clear all chat history")
async def clear_chat(interaction: discord.Interaction):
  if interaction.user.id == int(
      os.getenv('ADMIN_ID_1')) or interaction.user.id == int(
        os.getenv('ADMIN_ID_2')):
    await interaction.response.send_message(
      content="All messages have been cleared")
    await interaction.channel.purge()
    return

  if from_register_channel(interaction):
    await interaction.response.send_message(
      content='You can only use /register in this channel')
    return

  if not from_right_user(interaction):
    await interaction.response.send_message(
      content='Please go to your channel {0} to use this command'.format(
        interaction.channel.name))
    return
  await interaction.response.send_message(
    content="All messages have been cleared")
  await interaction.channel.purge()


register_channel_id = 1043080542335291442


def from_register_channel(interaction):
  return interaction.channel.id == register_channel_id


@tree.command(name="register", description="Register")
async def create_player(interaction: discord.Interaction, channel_name: str):
  if not from_register_channel(interaction):
    await interaction.response.send_message(
      content="Please go to Welcome/register channel to register")
    return

  user_id = str(interaction.user.id)
  user_entity = get_user_table().view_user(user_id)
  if user_entity is not None:
    await interaction.response.send_message(
      content=
      'You already registered a channel with the name of {0} for this account'.
      format(user_entity.channel_name))
    return

  user, user_channel = await create_private_channel(interaction, user_id,
                                                    channel_name)
  embed_content = get_help_embed()
  await user_channel.send(content="Welcome {0}!".format(user.name),
                          embeds=[embed_content])
  user_entity = User(user.id, user.name, user_channel.id, user_channel.name, 0,
                     0, 0, 0, {})
  get_user_table().add_user(user_entity)
  updator = Updator()
  updator.update_user_bet_history(user.id)
  await interaction.response.send_message(
    content=
    "Channel {0} is created for {1}. Please go to your right channel in Bet Channels."
    .format(channel_name, user.name))


@tree.command(name="create", description="Create a new player")
async def create_player(interaction: discord.Interaction, user_id: str,
                        channel_name: str):
  #user_id = int(user_id)

  if from_admin(interaction):
    guild = client.get_guild(guild_id)
    if guild.get_member(int(user_id)) is None:
      await interaction.response.send_message(
        content='User with id = {0} does not exist in the server'.format(
          user_id))
      return

    user_entity = get_user_table().view_user(user_id)
    if user_entity is not None:
      await interaction.response.send_message(
        content='User with id = {0} already existed'.format(user_id))
    else:
      user, user_channel = await create_private_channel(
        interaction, user_id, channel_name)
      embed_content = get_help_embed()
      await user_channel.send(content="Welcome {0}!".format(user.name),
                              embeds=[embed_content])
      user_entity = User(user.id, user.name, user_channel.id,
                         user_channel.name, 0, 0, 0, 0, {})
      get_user_table().add_user(user_entity)
      updator = Updator()
      updator.update_user_bet_history(user.id)
      await interaction.response.send_message(
        content="Channel {0} is created for {1}".format(
          channel_name, user.name))
  else:
    await interaction.response.send_message(
      content=
      'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.'
    )


async def kick_user(interaction, user_id):
  user_entity = get_user_table().view_user(user_id)
  if user_entity is None:
    print("There is no user with id = {0} a".format(user_id))
    return 0

  channel_id = user_entity.channel_id
  get_user_table().delete_user(user_id)

  user = client.get_user(int(user_id))
  await interaction.guild.kick(user)
  print("channel_id=", channel_id)
  return channel_id


async def delete_user_channel(user_channel_id):
  channel = client.get_channel(user_channel_id)
  await channel.delete()


@tree.command(name="delete", description="Delete an existing player")
async def delete_player(interaction: discord.Interaction, user_id: str):
  #user_id = int(user_id)

  #channel_id = interaction.channel_id
  #print("from delete_player", db['user'])
  if from_admin(interaction):

    guild = client.get_guild(guild_id)
    if guild.get_member(int(user_id)) is None:
      await interaction.response.send_message(
        content='User with id = {0} does not exist in the server'.format(
          user_id))
      return
    user_channel_id = await kick_user(interaction, user_id)
    if user_channel_id:
      await delete_user_channel(user_channel_id)
      await interaction.response.send_message(
        content="User with id = {0} is deleted".format(user_id))

    else:
      await interaction.response.send_message(
        content="There is no user with id = {0}".format(user_id))
  else:
    await interaction.response.send_message(
      content=
      'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.'
    )


@tree.command(name="update", description="Update scores")
async def update_scores(interaction: discord.Interaction):
  if from_admin(interaction):
    await interaction.response.send_message(content="Updating ...")
    #print(db['user'])
    # print("before:",db['user']['727084338675449906'])
    #del db['user']['727084338675449906']['history']['123']
    # #print("after del:",db['user']['727084338675449906'])
    # me = user_table.view_user('727084338675449906')
    # deepme = copy.deepcopy(me)
    # print(deepme.history)
    # deepme.history[123] = {
    #         "bet_option": 0,
    #         "result": "",
    #         'time': 123
    # }
    # # print(deepme.history)
    # user_table.update_user(deepme)
    # # new_me = user_table.view_user('727084338675449906')
    # # print(new_me.history)
    # # #print(db['user'])
    # #print(me.history)
    # print("after:",db['user']['727084338675449906'])
    #del db['user']['727084338675449906']['history']
    #print(db['user']['727084338675449906'])
    #del db['user']['']

    #print(db['match'])
    # db['match']['4853741']['result'] = '1-2'
    # db['match']['4853741']['is_over'] = True

    # db['match']['4853743']['result'] = '1-1'
    # db['match']['4853743']['is_over'] = True

    # db['match']['5118542']['result'] = '3-1'
    # db['match']['5118542']['is_over'] = True

    # print(db['match']['4853741'])
    # print(db['match']['4853743'])
    # print(db['match']['5118542'])

    # db['user']['775984015525543967']['score'] = 0
    # db['user']['775984015525543967']['win'] = 0
    # db['user']['775984015525543967']['draw'] = 0
    # db['user']['775984015525543967']['loss'] = 0
    # db['user']['775984015525543967']['history']['4853741']['result'] = ''
    # db['user']['775984015525543967']['history']['4853743']['result'] = ''

    # db['user']['775984015525543967']['history']['5118542']['result'] = ''

    #print(db['user']['775984015525543967'])
    updator = Updator()
    updator.update_upcoming_matches()
    updator.update_all_user_bet_history()
    await interaction.followup.send(content="Done updating!")
  else:
    await interaction.response.send_message(
      content=
      'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help'
    )


@tree.command(name="remind", description="Remind players")
async def remind_players(interaction: discord.Interaction):
  #channel_id = interaction.channel_id
  if from_admin(interaction):
    users = get_user_table().view_all()
    daily_bet = get_daily_bet()

    if len(daily_bet) == 0:
      await interaction.response.send_message("There are not matches today")
      return

    embed_contents = []
    for bet_detail in daily_bet:
      match_id = bet_detail.match_id
      match = get_match_table().view_match(str(match_id))
      match_info = match.to_payload()
      embed_contents.append(generate_bet_item(bet_detail, match_info))

    await interaction.response.send_message(content="Reminded all users.")
    for user in users:
      #print(user.name)
      channel = client.get_channel(user.channel_id)  #channel id here
      if channel is not None:
        await channel.send(
          "Nhắc nhẹ: Hnay có {0} trận nhé. Mấy ông thần vào /bet hộ cái".
          format(len(daily_bet)))
        for embed in embed_contents:
          await channel.send(embed=embed)

  else:
    await interaction.response.send_message(
      content=
      'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help'
    )


def formatTime(epoch):
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  dt = datetime.datetime.fromtimestamp(epoch, tz)
  # print it
  return dt.strftime('%d/%m/%Y %H:%M')


def generate_bet_item(bet_detail, match_info):
  print(match_info)
  embed_content = discord.Embed(
    type='rich',
    title=f'{bet_detail.home} (home) - {bet_detail.away} (away)',
    description=f'{formatTime(match_info["time"])} VN time'
    if match_info else None,
    colour=discord.Colour.from_str('#7F1431'))
  embed_content.add_field(name='Chấp',
                          value=bet_detail.asian_handicap,
                          inline=True)
  embed_content.add_field(name='Tài xỉu',
                          value=bet_detail.over_under,
                          inline=True)
  return embed_content


def update_selection_for_user(user_id, match_id, selection):
  user = get_user_table().view_user(user_id)
  if user is None:
    return

  updated_user = copy.deepcopy(user)

  updated_user.history[match_id]['bet_option'] = selection

  get_user_table().update_user(updated_user)


def generate_bet_actions(bet_detail, user_bet_for_match, match_info):
  lock_time_before_match = 15 * 60
  bet_changable = int(datetime.datetime.now().timestamp()
                      ) <= bet_detail.time - lock_time_before_match

  default_bet = user_bet_for_match["bet_option"] if user_bet_for_match else None
  # FOR TEST: default_bet = BetType.OVER.value

  view = View()
  select = Select(options=[
    discord.SelectOption(label='Home',
                         value=BetType.HOME.value,
                         default=default_bet == BetType.HOME.value),
    discord.SelectOption(label='Away',
                         value=BetType.AWAY.value,
                         default=default_bet == BetType.AWAY.value),
    discord.SelectOption(label='Over',
                         value=BetType.OVER.value,
                         default=default_bet == BetType.OVER.value),
    discord.SelectOption(label='Under',
                         value=BetType.UNDER.value,
                         default=default_bet == BetType.UNDER.value)
  ],
                  disabled=not bet_changable or match_info['is_over'])

  async def on_select_callback(interaction):
    if not bet_changable:
      await interaction.response.edit_message(
        content='quá giờ r đừng có ăn gian', view=None)
      return
    selection = int(select.values[0])
    update_selection_for_user(str(interaction.user.id), bet_detail.match_id,
                              selection)
    print('match id ', bet_detail.match_id, ' selected bet ', select.values[0])
    await interaction.response.defer()

  select.callback = on_select_callback
  view.add_item(select)

  return view


async def send_bet_message(interaction, bet_detail, user_bet_for_match,
                           match_info):
  embed_content = generate_bet_item(bet_detail, match_info)
  view = generate_bet_actions(bet_detail, user_bet_for_match, match_info)
  await interaction.followup.send(content='Lên kèo',
                                  embeds=[embed_content],
                                  view=view)


@tree.command(name="bet", description="Choose a betting option")
async def bet(interaction: discord.Interaction):
  if from_register_channel(interaction):
    await interaction.response.send_message(
      content='You can only use /register in this channel')
    return

  if not from_right_user(interaction):
    await interaction.response.send_message(
      content='Please go to your channel {0} to use this command'.format(
        interaction.channel.name))
    return
  daily_bet = get_daily_bet()

  user_id = interaction.user.id
  user = get_user_table().view_user(str(user_id))
  user_record = user.to_payload()
  user_bet_history = user_record["history"]

  if len(daily_bet) == 0:
    await interaction.response.send_message(
      content='Hôm nay ko có trận đâu bạn ei.')
    return
  await interaction.response.send_message(content='Các trận hôm nay:')

  for bet_detail in daily_bet:
    match_id = bet_detail.match_id

    match = get_match_table().view_match(str(match_id))
    match_info = match.to_payload()

    user_bet_for_match = user_bet_history[str(match_id)] if str(
      match_id) in user_bet_history.keys() else None
    await send_bet_message(interaction, bet_detail, user_bet_for_match,
                           match_info)


def generate_user_summary(user_record, rank=None, isOwner=False):
  history = user_record.history
  history_str = ' '.join([get_result_shorthand(item) for item in history
                          ]) if len(history) > 0 else 'No match found'
  embed_content = discord.Embed(
    type='rich',
    title=user_record.channel_name +
    (f' #{rank}' if rank is not None else '') + (' *' if isOwner else ''),
    colour=discord.Colour.green()
    if isOwner else discord.Colour.from_str('#7F1431'))
  embed_content.add_field(
    name='Win-Draw-Loss',
    value=f'{user_record.win}-{user_record.draw}-{user_record.loss}',
    inline=True)
  embed_content.add_field(name='Score', value=user_record.score, inline=True)
  embed_content.add_field(name='History (max 10 recent)',
                          value=history_str,
                          inline=True)
  return embed_content


@tree.command(name="profile", description="Show your record")
async def view_me(interaction: discord.Interaction):
  if from_register_channel(interaction):
    await interaction.response.send_message(
      content='You can only use /register in this channel')
    return
  if not from_right_user(interaction):
    await interaction.response.send_message(
      content='Please go to your channel {0} to use this command'.format(
        interaction.channel.name))
    return
  user_id = interaction.user.id
  #print(db['user'])
  #print(user_table.table)
  user = get_user_table().view_user(str(user_id))
  user_record = user.to_record()
  print(user_record)
  embed_content = generate_user_summary(user_record, isOwner=True)

  await interaction.response.send_message(content='', embeds=[embed_content])


@tree.command(name="record", description="Show all records")
async def view_all_record(interaction: discord.Interaction):
  if from_register_channel(interaction):
    await interaction.response.send_message(
      content='You can only use /register in this channel')
    return
  if not from_right_user(interaction):
    await interaction.response.send_message(
      content='Please go to your channel {0} to use this command'.format(
        interaction.channel.name))
    return
  user_id = str(interaction.user.id)
  users = get_user_table().view_all()
  user_records = [user.to_record() for user in users]
  user_records = sorted(user_records,
                        key=lambda x: (x.score, x.win, x.draw, -x.loss),
                        reverse=True)
  embed_content = [
    generate_user_summary(record, idx + 1, record.user_id == user_id)
    for idx, record in enumerate(user_records)
  ]
  await interaction.response.send_message(content='Bảng xếp hạng bét thủ',
                                          embeds=embed_content)


def get_help_embed():
  embed_content = discord.Embed(type='rich',
                                title='🎯 Help Page!',
                                colour=discord.Colour.from_str('#7F1431'),
                                description="Some commands I'm capable to do:")
  embed_content.set_thumbnail(
    url=
    'https://lh3.googleusercontent.com/pw/AL9nZEXNJywRGO5N_wo6lmEf4L0S6uDroOgskWeCtBbcTm8kuunOI_Jm-RS1MwnaGLPO8ZNBc7QgbtXJcBLR5U6SG3cnmXauJ157I-1rb6lc6SN3_qeRWFAoLFLd8gbUmsxRa7gQKit_RXvca0gKhz2rsW_D=s887-no?authuser=0'
  )
  embed_content.set_image(
    url=
    'https://lh3.googleusercontent.com/lsAHvdaS7bpcxa1IVxEmtrJdcuj890Qddt_FuyECWJ_U7W4uNaCLopgu1hBon9oFCe_Sifm0ngxWt_C5QlE3pToKq4J0n41FGCagT7mHnMTo0t4oOWmjKaGPQm24jEogua-yiZ8IswluKmOsbb1fbsJD2cB9CYLw-4PwLDGWR7vth-Toqq1znlrFiFERWN-lsx5UZGnxnev83FcpBmyAFwx5rqzzN6zvSm6BI2QbMkHRkAGfu6iBD_7bQQ4XDI_akEHOAlyR0gf6uPtFy2Ey6XdfsXwemkrydtFTS5kcTDZrAlCIhivl1SsoHXZZCMSTOg8kKBx6XsUkHNgntWNYnnPA5Bs5ggEChNR9FwHtq1TkVV-GA-YcRNDe01B6Xeu3FwTLLEoGXE3JiTxT97d6lVNGLsNkDzrRtVmWJxikMR9j-rDgW3zktqlHOOdohejKdDPioVMPT7D3dvRRqWUXfnP4FjIGcLxHMh9LwrrKN1DXS8sVLHwjSObMe1Zdtr6WrLn0X43y2CB2MmrkKVLTnzuPCu4b93NtVFIR3AKur9t3PhNZl7O7WS0jOll3JzPpl8UstIpeo12RATNjUSLmAvtdTryg4H6Y9dayBoWZnLjFmxnn0viO7mY5IiIjMRKMNQCiZms9oY6Q7giDlPHYzR8Bg9IaJynOb1woSz-u1QCIPatBgPVlYYbulXUHsv3w7dcE-DpuqcbdF5uNvHFoET0z_J6j_vpievqO4BgukjFPKaKXuHKilOL0WF9XQdzgZ2dHsON5ARZXVwWHaj5GHYi6tm5xjwBAbCglnirz1bQBElNc96_ptkKI6H4cwKIaWHt6E6_li1nqSrFCiWhIZnVShEtGSKZawX4WXKq6YFIGNrWwozqYl2CJVR7ks_MmoSTAnGfG4WYQ_B5_cJ-WsPJsNCZe6MEOGNCi7UHdeOz7l69Ls0EDjQwUTjdmvhCqMvho7zv9cbRPaw8BtXV2TcB6hszPJEdGJlnjlhONcoQXxcFXb_5s6WE0YLsMObkLIVszlexaxZThnewzJEt-SSYYMDaRQAH1NxgQOr_8uDpdOruvNsgijEGlvg9htdw=w2124-h960-no?authuser=0'
  )
  embed_content.add_field(name=':goggles:  `/profile`',
                          value='Check your summary stats',
                          inline=False)
  embed_content.add_field(name=':bar_chart:  `/record`',
                          value='See the leaderboard of all the bettors',
                          inline=False)
  embed_content.add_field(name=':game_die:  `/bet`',
                          value='Make your bet on daily matches',
                          inline=False)
  embed_content.add_field(name=':skull:  `/clear`',
                          value='Clear your chat',
                          inline=False)
  return embed_content


@tree.command(name="help", description="Show rules and commands")
async def help(interaction):
  if from_register_channel(interaction):
    await interaction.response.send_message(
      content='You can only use /register in this channel')
    return
  if not from_right_user(interaction):
    await interaction.response.send_message(
      content='Please go to your channel {0} to use this command'.format(
        interaction.channel.name))
    return
  embed_content = get_help_embed()
  await interaction.response.send_message(content='', embeds=[embed_content])


client.run(token)
