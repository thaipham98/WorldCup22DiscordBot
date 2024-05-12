# utilities.py
from config import ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_3, REGISTER_CHANNEL_ID, ADMIN_CHANNEL_ID, BOT_ID, BET_CHANNEL_NAME
from database import get_user_table
import discord
from result import get_result_shorthand
from discord.ui import Select, View
import datetime
import pytz
import copy
from bet_type import BetType, bet_type_converter
from bet_model import BetModel


def check_user_permission(interaction):
    # Implementation here
    return True

def get_daily_bet(events_api):
  current_time = datetime.datetime.now()
  today = "{:02d}".format(current_time.year) + "{:02d}".format(
    current_time.month) + "{:02d}".format(current_time.day)
  # today = '20221201'
  # TODO: replace this temp date with today date above
  upcoming_daily_matches = events_api.get_upcoming_daily_events(today)
  #print("upcoming:",upcoming_daily_matches)
  inplay_matches = events_api.get_inplay_events()
  #print("inplay:",inplay_matches)
  ended_daily_matches = events_api.get_ended_daily_event(today)
  #print("ended",ended_daily_matches)
  #daily_matches = events_api.get_upcoming_daily_events('20221121')

  #daily_matches = upcoming_daily_matches + inplay_matches + ended_daily_matches
  daily_matches = []
  if upcoming_daily_matches['success'] == 1:
    daily_matches += upcoming_daily_matches['results']

  if inplay_matches['success'] == 1:
    daily_matches += inplay_matches['results']

  if ended_daily_matches['success'] == 1:
    daily_matches += ended_daily_matches['results']

  #daily_matches = upcoming_daily_matches
  bet_model = BetModel()

  #print(daily_matches)
  daily_bet = bet_model.from_daily_matches_to_daily_bet(daily_matches)
  return daily_bet

async def delete_user_channel(client, user_channel_id):
  channel = client.get_channel(user_channel_id)
  await channel.delete()

async def kick_user(client, interaction, user_id):
  user_entity = get_user_table().view_user(user_id)
  if user_entity is None:
    print("There is no user with id = {0} a".format(user_id))
    return 0

  channel_id = user_entity.channel_id
  get_user_table().delete_user(user_id)

  user = client.get_user(int(user_id))
  #await interaction.guild.kick(user)
  #print("channel_id=", channel_id)
  return channel_id

async def create_private_channel(client, interaction, user_id, channel_name):
  user = client.get_user(int(user_id))
  bot = client.get_user(BOT_ID)
  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=BET_CHANNEL_NAME)
  overwrites = {
    guild.default_role: discord.PermissionOverwrite(read_messages=False),
    user: discord.PermissionOverwrite(view_channel=True),
    bot: discord.PermissionOverwrite(view_channel=True)
  }

  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=BET_CHANNEL_NAME)

  channel = await guild.create_text_channel(channel_name,
                                            overwrites=overwrites,
                                            category=category)

  return user, channel

def update_hopestar_selection_for_user(user_id, match_id, selection):
  user = get_user_table().view_user(user_id)

  if user is None:
    return

  updated_user = copy.deepcopy(user)
  updated_user.history[match_id]['used_hopestar'] = selection

  if selection:
    updated_user.hopestar -= 1
  else:
    updated_user.hopestar += 1
  get_user_table().update_user(updated_user)

async def send_bet_message(interaction, bet_detail, user_bet_for_match,
       match_info):
    embed_content = generate_bet_item(bet_detail, match_info, user_bet_for_match)
    view = generate_bet_actions(bet_detail, user_bet_for_match, match_info)
    await interaction.followup.send(content='Lên kèo',
                  embeds=[embed_content],
                  view=view)

def update_selection_for_user(user_id, match_id, selection):
  user = get_user_table().view_user(user_id)
  if user is None:
    return

  updated_user = copy.deepcopy(user)

  updated_user.history[match_id]['bet_option'] = selection

  get_user_table().update_user(updated_user)

def formatTime(epoch):
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  dt = datetime.datetime.fromtimestamp(epoch, tz)
  # print it
  return dt.strftime('%d/%m/%Y %H:%M')

def from_right_user(interaction):
  user_id = str(interaction.user.id)
  user = get_user_table().view_user(user_id)
  if user is None:
    return False
  return interaction.channel.id == user.channel_id


def from_admin(interaction):
  return interaction.channel.name == 'admin' and interaction.channel_id == ADMIN_CHANNEL_ID and (
      interaction.user.id == ADMIN_ID_1
      or interaction.user.id == ADMIN_ID_2
      or interaction.user.id == ADMIN_ID_3)

def from_register_channel(interaction):
  return interaction.channel.id == REGISTER_CHANNEL_ID

def get_help_embed():
  embed_content = discord.Embed(type='rich',
                                title='🎯 Help Page!',
                                colour=discord.Colour.from_str('#7F1431'),
                                description="Some commands I'm capable to do:")
  embed_content.set_thumbnail(
    url=
    'https://lh3.googleusercontent.com/pw/AL9nZEXNJywRGO5N_wo6lmEf4L0S6uDroOgskWeCtBbcTm8kuunOI_Jm-RS1MwnaGLPO8ZNBc7QgbtXJcBLR5U6SG3cnmXauJ157I-1rb6lc6SN3_qeRWFAoLFLd8gbUmsxRa7gQKit_RXvca0gKhz2rsW_D=s887-no?authuser=0'
  )
  embed_content.set_image(url='https://i.imgur.com/Z9gcRdb.png')
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
  embed_content.set_footer(text=f"Hopestar balance: {user_record.hopestar}")
  return embed_content

def generate_bet_item(bet_detail, match_info, user_bet_for_match=None):
  embed_content = discord.Embed(
    type='rich',
    title=
    f'{bet_detail.home} (home) - {bet_detail.away} (away) {":star:" if (user_bet_for_match is not None and user_bet_for_match["used_hopestar"]) else ""}',
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

def generate_bet_actions(bet_detail, user_bet_for_match, match_info):
  lock_time_before_match = 15 * 60
  bet_changable = int(datetime.datetime.now().timestamp()
                      ) <= bet_detail.time - lock_time_before_match

  default_bet = user_bet_for_match["bet_option"] if user_bet_for_match else None
  # FOR TEST: default_bet = BetType.OVER.value

  view = View(timeout=None)
  bet_select = Select(options=[
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

  async def on_bet_select_callback(interaction):
    select_changable = int(datetime.datetime.now().timestamp()
                           ) <= bet_detail.time - lock_time_before_match
    if not select_changable:
      await interaction.response.edit_message(
        content='Quá giờ r đừng có ăn gian', view=None)
      return
    selection = int(bet_select.values[0])
    update_selection_for_user(str(interaction.user.id), bet_detail.match_id,
                              selection)

    await interaction.response.send_message(
      content=
      f"You chose {bet_type_converter[selection]} for match {match_info['home']} - {match_info['away']} | ah: {match_info['asian_handicap']} - ou: {match_info['over_under']}"
    )

  bet_select.callback = on_bet_select_callback
  view.add_item(bet_select)

  default_hopestar = user_bet_for_match[
    "used_hopestar"] if user_bet_for_match else 0

  hopestar_select = Select(options=[
    discord.SelectOption(label='Use hopestar',
                         value=1,
                         default=default_hopestar == 1),
    discord.SelectOption(label='Not use hopestar',
                         value=0,
                         default=default_hopestar == 0)
  ],
                           disabled=not bet_changable or match_info['is_over'])

  async def on_hopestar_select_callback(interaction):
    select_changable = int(datetime.datetime.now().timestamp()
                           ) <= bet_detail.time - lock_time_before_match
    if not select_changable:
      await interaction.response.edit_message(
        content='Quá giờ r đừng có ăn gian', view=None)
      return
    selection = int(hopestar_select.values[0])

    user_id = str(interaction.user.id)
    user = get_user_table().view_user(user_id)

    if selection and not user.hopestar:
      await interaction.response.send_message(content='Hết sao rồi!')
      return

    if user.history[bet_detail.match_id]['used_hopestar'] != selection:
      update_hopestar_selection_for_user(user_id, bet_detail.match_id,
                                         selection)

    await interaction.response.send_message(
      content=
      f"You {'selected' if selection == 1 else 'did not select'} hopestar for match {match_info['home']} - {match_info['away']} | ah: {match_info['asian_handicap']} - ou: {match_info['over_under']}"
    )

  hopestar_select.callback = on_hopestar_select_callback
  view.add_item(hopestar_select)

  return view

