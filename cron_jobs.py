# cron_jobs.py
from discord.ext import tasks
import datetime
from database import backup_database, get_match_table, get_user_table
from updator import Updator
from utilities import get_daily_bet, generate_bet_item
import time
from config import ADMIN_CHANNEL_ID, BID_CHANNEL_ID, LEADERBOARD_CHANNEL_ID, UPDATE_CHANNEL_ID

# Create a timezone object for UTC+7
vn_tz = datetime.timezone(datetime.timedelta(hours=7))

first_matches_update_time = datetime.time(hour=22, minute=15, tzinfo=vn_tz)
first_matches_after_penalty = datetime.time(hour=23, minute=15, tzinfo=vn_tz)
second_matches_update_time = datetime.time(hour=1, minute=15, tzinfo=vn_tz)
second_matches_after_penalty = datetime.time(hour=2, minute=15, tzinfo=vn_tz)
# TODO: remove 3rd match time when playoff
third_matches_update_time = datetime.time(hour=4, minute=15, tzinfo=vn_tz)
third_matches_after_penalty = datetime.time(hour=5, minute=15, tzinfo=vn_tz)

odd_update_time = datetime.time(hour=8, tzinfo=vn_tz)

morning_remind_time = datetime.time(hour=11, tzinfo=vn_tz)
afternoon_remind_time = datetime.time(hour=14, tzinfo=vn_tz)
before_first_match_remind_time = datetime.time(hour=18, tzinfo=vn_tz)

remind_trading_close_time_1 = datetime.time(hour=16, tzinfo=vn_tz)
remind_trading_close_time_2 = datetime.time(hour=17, tzinfo=vn_tz)
remind_trading_close_time_3 = datetime.time(hour=18, tzinfo=vn_tz)

trading_close_time = datetime.time(hour=19, tzinfo=vn_tz)

leaderboard_update_time = datetime.time(hour=10, minute=30, tzinfo=vn_tz)


def setup_cron_jobs(client, events_api):

  @tasks.loop(time=[
      remind_trading_close_time_1, remind_trading_close_time_2,
      remind_trading_close_time_3
  ])
  async def remind_trading_close_cron_job():
    bid_channel = client.get_channel(BID_CHANNEL_ID)
    if bid_channel is not None:
      await bid_channel.send('@everyone Trading closes at 7 pm!')

  @tasks.loop(time=[
      leaderboard_update_time, first_matches_update_time,
      second_matches_update_time, third_matches_update_time
  ])
  async def leaderboard_update_job():
    leaderboard_list = get_user_table().get_leaderboard()

    if leaderboard_list is None:
      return

    message = "\n".join([
        f"[{index+1}] {user.channel_name}: {user.score} - hopestar: {user.hopestar}"
        for index, user in enumerate(leaderboard_list)
    ])

    leaderboard_channel = client.get_channel(LEADERBOARD_CHANNEL_ID)
    if leaderboard_channel is not None:
      await leaderboard_channel.send(message)

  @tasks.loop(time=[trading_close_time])
  async def close_trading_cron_job():
    updator = Updator()
    await updator.close_trading(client)

  @tasks.loop(time=[odd_update_time])
  async def update_odd_cron_job():
    print("auto update odd ...")
    updator = Updator()
    updator.update_upcoming_matches()
    updator.update_all_user_bet_history()

    admin_channel = client.get_channel(ADMIN_CHANNEL_ID)
    await admin_channel.send("Auto: updated new odds")

  @tasks.loop(time=[
      first_matches_update_time, first_matches_after_penalty,
      second_matches_update_time, second_matches_after_penalty,
      third_matches_update_time, third_matches_after_penalty
  ])
  async def update_result_cron_job():
    print("auto update running ...")
    updator = Updator()
    await updator.send_match_results(client)
    updator.update_ended_matches()
    updator.update_all_user_bet_history()
    await updator.update_user_reward_hopestar(client)

    admin_channel = client.get_channel(ADMIN_CHANNEL_ID)
    await admin_channel.send("Auto update done")

    update_channel = client.get_channel(UPDATE_CHANNEL_ID)
    await update_channel.send("@everyone New odds are available")

  @tasks.loop(time=[
      morning_remind_time, afternoon_remind_time,
      before_first_match_remind_time
  ])
  async def remind_cron_job():
    #print("auto remind ...")
    admin_channel = client.get_channel(ADMIN_CHANNEL_ID)  #channel id here
    users = get_user_table().view_all()
    daily_bet = get_daily_bet(events_api)

    if len(daily_bet) == 0:
      await admin_channel.send("Auto: no matches sent")
      return

    embed_contents = []
    for bet_detail in daily_bet:
      match_id = bet_detail.match_id
      match = get_match_table().view_match(str(match_id))

      if match is None:
        continue
      match_info = match.to_payload()
      embed_contents.append(generate_bet_item(bet_detail, match_info))

    for user in users:
      time.sleep(0.1)
      channel = client.get_channel(user.channel_id)  #channel id here
      if channel is not None:
        await channel.send(
            "Nhắc nhẹ: Hnay có {0} trận nhé. Mấy ông thần vào /bet hộ cái".
            format(len(daily_bet)))
        for embed in embed_contents:
          await channel.send(embed=embed)

    await admin_channel.send("Auto: sent reminder")

  remind_trading_close_cron_job.start()
  leaderboard_update_job.start()
  close_trading_cron_job.start()
  update_odd_cron_job.start()
  update_result_cron_job.start()
  remind_cron_job.start()
