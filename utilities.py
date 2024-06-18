# utilities.py
from config import ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_3, REGISTER_CHANNEL_ID, ADMIN_CHANNEL_ID, BOT_ID, BET_CHANNEL_NAME, VERIFY_CHANNEL_NAME, BID_CHANNEL_ID
from database import get_user_table, get_verification_table, get_bid_table
import discord
from result import get_result_shorthand
from discord.ui import Select, View, Modal, TextInput, Button
import datetime
import pytz
import copy
from bet_type import BetType, bet_type_converter
from bet_model import BetModel
from bid import Bid
from offer import Offer
from bid_status import BidStatus
from user import User

HOPESTAR_PRICE = 10000


def check_user_permission(interaction):
  # Implementation here
  return True


def get_daily_bet(events_api):
  current_time = datetime.datetime.now()
  today = "{:02d}".format(current_time.year) + "{:02d}".format(
      current_time.month) + "{:02d}".format(current_time.day)
  upcoming_daily_matches = events_api.get_upcoming_daily_events(today)
  #print("upcoming:", upcoming_daily_matches, flush=True)
  inplay_matches = events_api.get_inplay_events()
  #print("inplay:", inplay_matches, flush=True)
  ended_daily_matches = events_api.get_ended_daily_event(today)
  #print("ended", ended_daily_matches, flush=True)
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
  #print(daily_bet, flush=True)
  return daily_bet


async def delete_user_channel(client, user_channel_id):
  channel = client.get_channel(user_channel_id)
  await channel.delete()


async def delete_verify_channel(client, verify_channel_id):
  channel = client.get_channel(verify_channel_id)
  await channel.delete()


async def kick_user(client, interaction, user_id):
  user_entity = get_user_table().view_user(user_id)
  if user_entity is None:
    print("There is no user with id = {0} a".format(user_id))
    return 0, 0
  verification_entity = get_verification_table().view_verification(user_id)

  if verification_entity is None:
    print("There is no verification with id = {0} a".format(user_id))
    return 0, 0

  channel_id = user_entity.channel_id
  verify_channel_id = verification_entity.verify_channel_id
  get_user_table().delete_user(user_id)
  get_verification_table().delete_verification(user_id)

  #user = client.get_user(int(user_id))
  #await interaction.guild.kick(user)
  #print("channel_id=", channel_id)
  return channel_id, verify_channel_id


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


async def create_verify_private_channel(client, interaction, user_id,
                                        channel_name):
  user = client.get_user(int(user_id))
  bot = client.get_user(BOT_ID)
  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=VERIFY_CHANNEL_NAME)
  overwrites = {
      guild.default_role: discord.PermissionOverwrite(read_messages=False),
      user: discord.PermissionOverwrite(view_channel=True),
      bot: discord.PermissionOverwrite(view_channel=True)
  }

  guild = interaction.guild
  category = discord.utils.get(guild.categories, name=VERIFY_CHANNEL_NAME)

  verify_channel_name = "verify-" + user.name + "-" + channel_name
  channel = await guild.create_text_channel(verify_channel_name,
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
      interaction.user.id == ADMIN_ID_1 or interaction.user.id == ADMIN_ID_2
      or interaction.user.id == ADMIN_ID_3)


def from_register_channel(interaction):
  return interaction.channel.id == REGISTER_CHANNEL_ID


def get_help_embed():
  embed_content = discord.Embed(type='rich',
                                title='🎯 Help Page!',
                                colour=discord.Colour.from_str('#7F1431'),
                                description="Some commands I'm capable to do:")
  embed_content.set_thumbnail(url='https://i.imgur.com/a35ZmrK.png')
  embed_content.set_image(url='https://i.imgur.com/Z9gcRdb.png')
  embed_content.add_field(name=':star:  `/convert`',
                          value='Convert point to star',
                          inline=False)
  embed_content.add_field(name=':money_mouth: `/request_star`',
                          value='Request to buy star from other user',
                          inline=False)
  embed_content.add_field(name=':eyes:  `/view_bid`',
                          value='View all bids',
                          inline=False)
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
  embed_content.add_field(name=':face_with_peeking_eye:  `/peek`',
                          value='Look at another player summary',
                          inline=False)
  embed_content.add_field(name=':pushpin:  `/peek_bid`',
                          value='Look at a specific bid',
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
      colour=discord.Colour.green() if isOwner else discord.Colour.blue())
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
    if not from_right_user(interaction):
      await interaction.response.send_message(
          content='Please go to your channel to use this command')
      return
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
    if not from_right_user(interaction):
      await interaction.response.send_message(
          content='Please go to your channel to use this command')
      return
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


def update_hopestar_after_converting(user_id, hopestar_amount):
  user = get_user_table().view_user(user_id)

  if user is None:
    return False

  if user.score < hopestar_amount * HOPESTAR_PRICE:
    return False

  updated_user = copy.deepcopy(user)
  updated_user.hopestar += hopestar_amount
  updated_user.score -= hopestar_amount * HOPESTAR_PRICE

  get_user_table().update_user(updated_user)

  return True


def generate_star_convert_modal(current_score):
  convert_modal = Modal(title="Mua sao đê")
  convert_star_input = TextInput(label="Đang có " + str(current_score) +
                                 " điểm. Mỗi sao 10k. Mua bn?",
                                 required=True,
                                 max_length=5,
                                 min_length=1)

  async def on_submit(interaction):
    try:
      convert_star_input_value = int(convert_star_input.value)
      if convert_star_input_value is None:
        await interaction.response.send_message(content='Viết đ gì đấy?')
        return
      if convert_star_input_value < 1:
        await interaction.response.send_message(content='Hack ăn loz à?')
        return
      star_buyable = convert_star_input_value * HOPESTAR_PRICE <= current_score
      if not star_buyable:
        await interaction.response.send_message(content='Nghèo như chó đòi mua'
                                                )
        return
      result = update_hopestar_after_converting(str(interaction.user.id),
                                                convert_star_input_value)
      if not result:
        await interaction.response.send_message(content='Chưa mua được đâu')
      else:
        new_score = current_score - convert_star_input_value * HOPESTAR_PRICE
        await interaction.response.send_message(
            content='You bought ' + str(convert_star_input_value) +
            ' hopestar.' + ' Old hopestar balance: ' + str(current_score) +
            '. New hopestar balance: ' + str(new_score))
    except Exception as e:
      print(e)
      await interaction.response.send_message(content='Viết đ gì đấy?')
      return

  convert_modal.add_item(convert_star_input)
  convert_modal.on_submit = on_submit
  return convert_modal


def generate_request_star_modal(client, receiver: discord.User):
  request_star_modal = Modal(title=f"Mua sao từ thằng {receiver.name} đê")

  request_star_amount_input = TextInput(label="Mua bn sao?",
                                        required=True,
                                        max_length=5,
                                        min_length=1)
  request_star_price_input = TextInput(label="Giá bn?",
                                       required=True,
                                       max_length=5,
                                       min_length=1)

  async def on_confirm_request_star(interaction):
    try:
      sender_entity = get_user_table().view_user(str(interaction.user.id))
      receiver_entity = get_user_table().view_user(str(receiver.id))
      if receiver_entity is None:
        await interaction.response.send_message(content='Làm đ có th này?')
        return
      receiver_channel = client.get_channel(receiver_entity.channel_id)
      if receiver_channel is None:
        await interaction.response.send_message(content='Th này làm đ có kênh?'
                                                )
        return

      if sender_entity is None:
        await interaction.response.send_message(content='Mày ko tồn tại')
        return
      request_star_amount_input_value = int(request_star_amount_input.value)
      if request_star_amount_input_value is None:
        await interaction.response.send_message(content='Viết đ gì đấy?')
        return
      if request_star_amount_input_value < 1:
        await interaction.response.send_message(content='Hack ăn loz à?')
        return
      if request_star_amount_input_value > receiver_entity.hopestar:
        await interaction.response.send_message(content='Thằng kia ko đủ sao')
        return

      request_star_price_input_value = int(request_star_price_input.value)
      if request_star_price_input_value is None:
        await interaction.response.send_message(content='Viết đ gì đấy?')
        return
      if request_star_price_input_value < 1:
        await interaction.response.send_message(content='Hack ăn loz à?')
        return
      if request_star_price_input_value > sender_entity.score:
        await interaction.response.send_message(content='Ko đủ điểm')
        return

      bid = create_bid(str(receiver.id), request_star_amount_input_value)
      if bid is None:
        await interaction.response.send_message(content='Không thể tạo bid')
        return

      offer = Offer(bid.bid_id, str(interaction.user.id),
                    request_star_price_input_value,
                    int(datetime.datetime.now().timestamp()))
      add_offer_to_bid_succeeded = add_or_update_offer_to_bid(
          bid.bid_id, offer)
      if not add_offer_to_bid_succeeded:
        await interaction.response.send_message(content='Không thể tạo bid')
        return

      await receiver_channel.send(
          content=
          f"Thằng {interaction.user.name} đã yêu cầu mua {request_star_amount_input_value} sao với giá {request_star_price_input} từ bạn"
      )

      bid_channel = client.get_channel(BID_CHANNEL_ID)
      if bid_channel is not None:
        await bid_channel.send(
            content=
            f"[**Start bid**][**Bid {bid.bid_id}**]: <@{interaction.user.id}> bid {request_star_amount_input_value} star(s) for {request_star_price_input} from <@{receiver.id}>."
        )

      await interaction.response.send_message(
          content=
          f"Bạn đã yêu cầu mua {request_star_amount_input_value} sao với giá {request_star_price_input} từ thằng {receiver.name}"
      )

      return
    except Exception as e:
      print(e)
      await interaction.response.send_message(content='Viết đ gì đấy?')
      return

  request_star_modal.add_item(request_star_amount_input)
  request_star_modal.add_item(request_star_price_input)
  request_star_modal.on_submit = on_confirm_request_star
  return request_star_modal


def generate_view_bid_embed_content(bid_item: Bid, is_receiver: bool):
  receiver_entity = get_user_table().view_user(bid_item.receiver_id)
  if receiver_entity is None:
    return None
  embed_content = discord.Embed(
      colour=discord.Colour.red() if is_receiver else discord.Colour.green(),
      type='rich',
      title=
      f"Bid {bid_item.bid_id}: Request {receiver_entity.name} {bid_item.star_amount} star(s)"
  )
  all_offers = get_all_offers_from_bid(bid_item.bid_id)
  for offer in all_offers:
    sender_entity = get_user_table().view_user(offer.sender_id)
    if sender_entity is None:
      continue
    embed_content.add_field(name=f"{sender_entity.name}",
                            value=f"{offer.price}")
  if bid_item.winner_id is not None:
    embed_content.set_footer(text="Winner is chosen")
  return embed_content


def generate_view_matches_embed_content(matches):
  embed_content = discord.Embed(colour=discord.Colour.green(),
                                type='rich',
                                title="New matches results update:")

  for idx, match in enumerate(matches, 1):
    # Add field with formatted name and value
    field_name = f"**Home: {match.home} - Away: {match.away}**"
    match_time = f'{formatTime(match.time)} VN time'
    field_value = f"{match.result}\n{match_time}\n___"

    embed_content.add_field(name=field_name, value=field_value, inline=False)

  return embed_content


def generate_view_bid_select_winner_view(client, bid_item: Bid):
  view = View(timeout=None)
  all_offers = get_all_offers_from_bid(bid_item.bid_id)
  current_winner_id = bid_item.winner_id
  winner_list = []
  for offer in all_offers:
    sender_entity = get_user_table().view_user(offer.sender_id)
    if sender_entity is None:
      continue
    winner_list.append({"label": sender_entity.name, "value": offer.sender_id})
  winner_options = [
      discord.SelectOption(label=item['label'],
                           value=item['value'],
                           default=current_winner_id == item['value'])
      for item in winner_list
  ]
  winner_select = Select(options=winner_options)

  async def on_winner_select_callback(interaction):
    if not from_right_user(interaction):
      await interaction.response.send_message(content='Ko có quyền')
      return
    selection = winner_select.values[0]
    if selection is None:
      return
    winner_entity = get_user_table().view_user(selection)
    if winner_entity is None:
      return
    update_bid_winner(bid_item.bid_id, selection)
    # TODO: deduct score from selected winner
    bid_channel = client.get_channel(BID_CHANNEL_ID)
    if bid_channel is not None:
      await bid_channel.send(
          content=
          f"[**Chose winner**][**Bid {bid_item.bid_id}**]: <@{interaction.user.id}> chose a winner!"
      )
    await interaction.response.send_message(
        content=f"You chose {winner_entity.name}")

  decline_bid_confirm_btn = Button(label="Decline bid",
                                   style=discord.ButtonStyle.red,
                                   disabled=bid_item.winner_id is None)

  async def on_decline_bid_confirm_callback(interaction):
    if not from_right_user(interaction):
      await interaction.response.send_message(content='Ko có quyền')
      return
    decline_bid(bid_item.bid_id)
    # TODO: refund if needed
    bid_channel = client.get_channel(BID_CHANNEL_ID)
    if bid_channel is not None:
      await bid_channel.send(
          content=
          f"[**Clear winner**][**Bid {bid_item.bid_id}**]: <@{interaction.user.id}> unchose the winner"
      )
    await interaction.response.send_message(
        content=f'Đã từ chối bid (id: {bid_item.bid_id})')

  winner_select.callback = on_winner_select_callback
  decline_bid_confirm_btn.callback = on_decline_bid_confirm_callback
  view.add_item(winner_select)
  view.add_item(decline_bid_confirm_btn)
  return view


def generate_view_bid_make_bid_modal(client, bid_id):
  make_bid_modal = Modal(title="Bid đê")
  make_bid_input = TextInput(label=f"Bid cho cai [ID: {bid_id}] de",
                             required=True,
                             max_length=5,
                             min_length=1)

  async def on_submit(interaction):
    try:
      if not from_right_user(interaction):
        await interaction.response.send_message(content='Ko có quyền')
        return
      make_bid_input_value = int(make_bid_input.value)
      sender_entity = get_user_table().view_user(str(interaction.user.id))
      if sender_entity is None:
        await interaction.response.send_message(content='Mày ko tồn tại')
        return
      if make_bid_input_value is None:
        await interaction.response.send_message(content='Viết đ gì đấy?')
        return
      if make_bid_input_value < 1:
        await interaction.response.send_message(content='Hack ăn loz à?')
        return
      if make_bid_input_value > sender_entity.score:
        await interaction.response.send_message(content='Ko đủ điểm')
        return
      if make_bid_input_value % 500 != 0:
        await interaction.response.send_message(
            content='Điểm phải chia hết cho 500. Điểm lẻ ăn loz à?')
        return
      bid_entity = get_bid_table().view_bid(bid_id)
      if bid_entity is None:
        await interaction.response.send_message(content='Kèo đ tồn tại')
        return
      bid_star_amount = bid_entity.star_amount
      if make_bid_input_value > HOPESTAR_PRICE * bid_star_amount:
        await interaction.response.send_message(content='Phá giá ăn loz à?')
        return

      current_winner_id = bid_entity.winner_id
      if str(interaction.user.id) == current_winner_id:
        current_winner_offer = bid_entity.current_offers[current_winner_id]
        if current_winner_offer is None:
          await interaction.response.send_message(content='Mày đã bid đâu?')
          return
        current_winner_offer_entity = from_dict_to_offer(
            bid_entity.current_offers[current_winner_id])
        if make_bid_input_value <= current_winner_offer_entity.price:
          await interaction.response.send_message(content='Giảm bid ăn loz à?')
          return

      offer = Offer(bid_id, str(interaction.user.id), make_bid_input_value,
                    int(datetime.datetime.now().timestamp()))
      add_offer_to_bid_succeeded = add_or_update_offer_to_bid(bid_id=bid_id,
                                                              offer=offer)
      if not add_offer_to_bid_succeeded:
        await interaction.response.send_message(content='Không thể tạo bid')
        return

      bid_channel = client.get_channel(BID_CHANNEL_ID)
      if bid_channel is not None:
        await bid_channel.send(
            content=
            f"[**Counter bid**][**Bid {bid_id}**]:  <@{interaction.user.id}> bid against {bid_entity.star_amount} star(s) with {make_bid_input_value} from <@{bid_entity.receiver_id}>."
        )

      await interaction.response.send_message(
          content=f'[Bid ID: {bid_id}]: đã bid {make_bid_input_value}')
      return
    except Exception as e:
      print(e)
      await interaction.response.send_message(content='Viết đ gì đấy?')
      return

  make_bid_modal.add_item(make_bid_input)
  make_bid_modal.on_submit = on_submit
  return make_bid_modal


def generate_view_bid_make_bid_view(client, bid_item: Bid):
  view = View(timeout=None)

  counter_bid_confirm_btn = Button(label="Counter bid",
                                   style=discord.ButtonStyle.green)

  async def on_counter_bid_confirm_callback(interaction):
    if not from_right_user(interaction):
      await interaction.response.send_message(content='Ko có quyền')
      return
    make_bid_modal = generate_view_bid_make_bid_modal(client, bid_item.bid_id)
    await interaction.response.send_modal(make_bid_modal)

  counter_bid_confirm_btn.callback = on_counter_bid_confirm_callback

  view.add_item(counter_bid_confirm_btn)
  return view


def create_bid(receiver_id, star_amount):
  bid_id = str(len(get_bid_table().view_all()) + 1)

  if bid_id in get_bid_table().view_all():
    return None

  bid = Bid(bid_id, int(datetime.datetime.now().timestamp()), receiver_id,
            star_amount)

  get_bid_table().add_bid(bid)

  return bid


def update_bid_winner(bid_id, winner_id):
  bid = get_bid_table().view_bid(bid_id)

  if bid is None:
    return

  updated_bid = copy.deepcopy(bid)
  updated_bid.winner_id = winner_id
  get_bid_table().update_bid(updated_bid)


def add_or_update_offer_to_bid(bid_id, offer):
  bid = get_bid_table().view_bid(bid_id)

  if bid is None:
    return False

  updated_bid = copy.deepcopy(bid)

  updated_bid.current_offers[offer.sender_id] = offer.to_dict()

  get_bid_table().update_bid(updated_bid)

  return True


def from_dict_to_offer(offer_dict):
  bid_id = offer_dict['bid_id']
  sender_id = offer_dict['sender_id']
  price = offer_dict['price']
  time_stamp = offer_dict['time_stamp']

  return Offer(bid_id, sender_id, price, time_stamp)


def get_all_offers_from_bid(bid_id):
  bid = get_bid_table().view_bid(bid_id)

  if bid is None:
    return []

  offers = []

  for key in bid.current_offers:
    offers.append(from_dict_to_offer(bid.current_offers[key]))
  offers.sort(key=lambda x: x.time_stamp, reverse=True)

  return offers


def get_ongoing_bids():
  bids = get_bid_table().view_all()

  ongoing_bids = []

  for bid in bids:
    if bid.status == BidStatus.ONGOING.value:
      ongoing_bids.append(bid)

  ongoing_bids.sort(key=lambda x: x.time_stamp, reverse=False)

  return ongoing_bids


def categorize_bids(receiver_id):
  bids = get_bid_table().view_all()

  bids_to_receiver = []
  bids_to_others = []

  for bid in bids:
    if bid.status != BidStatus.ONGOING.value:
      continue
    if bid.receiver_id == receiver_id:
      bids_to_receiver.append(bid)
    else:
      bids_to_others.append(bid)

  bids_to_receiver.sort(key=lambda x: x.time_stamp, reverse=True)
  bids_to_others.sort(key=lambda x: x.time_stamp, reverse=True)

  return bids_to_receiver, bids_to_others


def decline_bid(bid_id):
  bid = get_bid_table().view_bid(bid_id)

  if bid is None:
    return

  updated_bid = copy.deepcopy(bid)
  updated_bid.winner_id = None
  get_bid_table().update_bid(updated_bid)


def processed_transaction(buyer_id, seller_id, star_amount, price):
  buyer = get_user_table().view_user(buyer_id)
  seller = get_user_table().view_user(seller_id)

  if buyer is None:
    return False

  if seller is None:
    return False

  if buyer.score < price:
    return False

  if seller.hopestar < star_amount:
    return False

  updated_buyer = copy.deepcopy(buyer)
  updated_buyer.score -= price
  updated_buyer.hopestar += star_amount
  get_user_table().update_user(updated_buyer)

  updated_seller = copy.deepcopy(seller)
  updated_seller.score += price
  updated_seller.hopestar -= star_amount
  get_user_table().update_user(updated_seller)

  return True
