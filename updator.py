from replit import db

from config import UPDATE_CHANNEL_ID, BID_CHANNEL_ID, MATCH_RESULTS_CHANNEL_ID
import events_api
from match import Match
from match_table import MatchTable
from streak import get_user_total_reward_hopestar
from user_table import UserTable
from bet_type import BetType
from calculator import Calculator
from result import Result
import copy
from user import User
from bid_table import BidTable
import datetime
from result import star_converter
from bid_status import BidStatus
from utilities import from_dict_to_offer, get_ongoing_bids, processed_transaction, generate_view_matches_embed_content


class Updator:

  def __init__(self):
    self.api = events_api.Event_API()
    self.match_table = MatchTable()
    self.user_table = UserTable()
    self.calculator = Calculator()
    self.bid_table = BidTable()

  def _from_event_to_match(self, event):
    if event is None:
      return None

    event_id = event['id']
    match = self.api.get_event(event_id)

    if match['success'] != 1:
      print("Cannot convert event to match")
      return None

    match_id = match['results'][0]['id']
    home = match['results'][0]['home']['name']
    away = match['results'][0]['away']['name']
    time = int(match['results'][0]['time'])

    #get result from bet365
    event_odd = self.api.get_event_odds(event_id, source='bet365')

    if event_odd['success'] != 1:
      print("Cannot get the event odd")
      return None

    match_odd = event_odd['results']
    matching_dir = int(match_odd['stats']['matching_dir'])
    is_over = (match['results'][0]['ss'] is not None)

    result = None

    if is_over:
      home_score = match['results'][0]['scores']['2']['home']
      away_score = match['results'][0]['scores']['2']['away']
      result = f'{home_score}-{away_score}'

    #get odd from ysb88
    event_odd = self.api.get_event_odds(event_id)

    if event_odd['success'] != 1:
      print("Cannot get the event odd")
      return None
    match_odd = event_odd['results']

    asian_handicap = 0
    over_under = 0

    match_entity = self.match_table.view_match(str(event_id))
    if match_entity is not None:
      asian_handicap = match_entity.asian_handicap
      over_under = match_entity.over_under
    else:
      asian_handicap = float(
          match_odd['odds']['1_2'][0]['handicap']) * matching_dir
      over_under = float(match_odd['odds']['1_3'][0]['handicap'])

    return Match(match_id, home, away, asian_handicap, over_under, result,
                 time, is_over)

  async def send_match_results(self, client):
    #BACH TODO
    ended_events_from_api = self._get_ended_events()
    updated_matches = [
        self._from_event_to_match(event) for event in ended_events_from_api
    ]
    old_matches = self.match_table.list_all_matches()
    new_results = []
    updated_matches_map = self._to_map(updated_matches)
    old_matches_map = self._to_map(old_matches)
    for match_id in updated_matches_map.keys():
      if match_id not in old_matches_map or not old_matches_map[
          match_id].result:
        new_results.append(updated_matches_map[match_id])
    new_results.sort(key=lambda x: x.time, reverse=False)
    match_results_channel = client.get_channel(MATCH_RESULTS_CHANNEL_ID)
    if new_results:
      embed_content = generate_view_matches_embed_content(new_results)
      await match_results_channel.send(content='', embeds=[embed_content])
    return

  def _get_ended_events(self):
    current_time = datetime.datetime.now()
    today = "{:02d}".format(current_time.year) + "{:02d}".format(
        current_time.month) + "{:02d}".format(current_time.day)

    result = self.api.get_ended_daily_event(today)

    if result['success'] != 1:
      print("Cannot get ended events")
      return

    total = result['pager']['total']
    page = result['pager']['page']
    per_page = result['pager']['page']

    events = result['results']

    while total > per_page:
      page += 1
      result = self.api.get_upcoming_events(page=page)

      if result['success'] != 1:
        print("Cannot get ended events")
        return

      events += result['results']
      total -= per_page

    return events

  def update_ended_matches(self):
    ended_events_from_api = self._get_ended_events()
    updated_matches = [
        self._from_event_to_match(event) for event in ended_events_from_api
    ]
    updated_matches_map = self._to_map(updated_matches)

    for match_id in updated_matches_map.keys():
      updated_match_payload = updated_matches_map[match_id].to_payload()

    old_matches = self.match_table.list_all_matches()
    old_matches_map = self._to_map(old_matches)

    for match_id in updated_matches_map.keys():
      if match_id not in old_matches_map:
        self.match_table.add_match(updated_matches_map[match_id])
      else:
        old_match_payload = old_matches_map[match_id].to_payload()
        updated_match_payload = updated_matches_map[match_id].to_payload()

        if updated_match_payload != old_match_payload:
          print("update match ...")
          self.match_table.update_match(updated_matches_map[match_id])
    print("Done updating ended matches")

  def _get_upcoming_events(self):
    current_time = datetime.datetime.now()

    today = "{:02d}".format(current_time.year) + "{:02d}".format(
        current_time.month) + "{:02d}".format(current_time.day)

    result = self.api.get_upcoming_daily_events(today)

    if result['success'] != 1:
      print("Cannot get upcoming events")
      return

    total = result['pager']['total']
    page = result['pager']['page']
    per_page = result['pager']['page']

    events = result['results']

    while total > per_page:
      page += 1
      result = self.api.get_upcoming_events(page=page)

      if result['success'] != 1:
        print("Cannot get upcoming events")
        return

      events += result['results']
      total -= per_page

    return events

  def _to_map(self, matches):
    map = {}

    for i in range(len(matches)):
      match = matches[i]

      #handle if two matches happen at the same time
      if i > 0:
        prev_match = matches[i-1]
        if match.time == prev_match.time:
          match.time += 1
        
      map[match.match_id] = match
    
    return map

  def update_upcoming_matches(self):
    upcoming_events_from_api = self._get_upcoming_events()
    updated_matches = [
        self._from_event_to_match(event) for event in upcoming_events_from_api
    ]
    updated_matches_map = self._to_map(updated_matches)

    old_matches = self.match_table.list_all_matches()
    old_matches_map = self._to_map(old_matches)

    changed_odd_matches = []
    for match_id in updated_matches_map.keys():
      if match_id not in old_matches_map:
        self.match_table.add_match(updated_matches_map[match_id])
      else:
        old_match_payload = old_matches_map[match_id].to_payload()
        updated_match_payload = updated_matches_map[match_id].to_payload()

        if updated_match_payload != old_match_payload:

          if updated_match_payload['is_over'] == False:
            print("update match ...")
            self.match_table.update_match(updated_matches_map[match_id])
    print("Done updating upcoming matches")

  def update_user_bet_history(self, user_id):
    user = self.user_table.view_user(str(user_id))
    if user is None:
      return
    matches = self.match_table.list_all_matches()
    updated_user = copy.deepcopy(user)
    for match in matches:
      match_id = match.id
      if match_id not in updated_user.history:
        updated_user.history[match_id] = {
            "bet_option": BetType.UNCHOSEN.value,
            "result": "",
            'time': match.time,
            'used_hopestar': 0
        }
      if match.is_over:
        if updated_user.history[match_id]['result'] == '':
          if updated_user.history[match_id][
              'bet_option'] == BetType.UNCHOSEN.value:
            updated_user.history[match_id]['result'] = Result.LOSS.name
            updated_user.loss += 1
            updated_user.score += Result.LOSS.value
          else:
            result = self.calculator.calculate(
                updated_user.history[match_id]['bet_option'],
                match.asian_handicap, match.over_under, match.result)
            if result == Result.WIN or result == Result.HALF_WIN:
              updated_user.win += 1

            if result == Result.LOSS or result == Result.HALF_LOSS:
              updated_user.loss += 1

            if result == Result.DRAW:
              updated_user.draw += 1

            if updated_user.history[match_id]['used_hopestar']:
              result = star_converter[result]

            updated_user.history[match_id]['result'] = result.name
            updated_user.score += result.value
    self.user_table.update_user(updated_user)

  def update_all_user_bet_history(self):
    users = self.user_table.view_all()

    matches = self.match_table.list_all_matches()

    for user in users:
      updated_user = copy.deepcopy(user)
      for match in matches:
        match_id = match.id
        if match_id not in updated_user.history:
          updated_user.history[match_id] = {
              "bet_option": BetType.UNCHOSEN.value,
              "result": "",
              'time': match.time,
              'used_hopestar': 0
          }

        if match.is_over:
          if updated_user.history[match_id]['result'] == '':
            if updated_user.history[match_id][
                'bet_option'] == BetType.UNCHOSEN.value:
              updated_user.history[match_id]['result'] = Result.LOSS.name
              updated_user.loss += 1
              updated_user.score += Result.LOSS.value
            else:
              result = self.calculator.calculate(
                  updated_user.history[match_id]['bet_option'],
                  match.asian_handicap, match.over_under, match.result)
              if result == Result.WIN or result == Result.HALF_WIN:
                updated_user.win += 1

              if result == Result.LOSS or result == Result.HALF_LOSS:
                updated_user.loss += 1

              if result == Result.DRAW:
                updated_user.draw += 1

              if updated_user.history[match_id]['used_hopestar']:
                result = star_converter[result]

              updated_user.history[match_id]['result'] = result.name
              updated_user.score += result.value

      self.user_table.update_user(updated_user)

    print("Done updating user bet history")

  async def update_user_reward_hopestar(self, client):
    users = self.user_table.view_all()
    for user in users:
      updated_user = copy.deepcopy(user)
      user_total_reward_hopestar = get_user_total_reward_hopestar(
          updated_user.user_id)
      user_current_reward_hopestar = updated_user.hopestar_reward_granted
      hopestar_to_add = 0
      if user_total_reward_hopestar > user_current_reward_hopestar:
        hopestar_to_add = user_total_reward_hopestar - user_current_reward_hopestar
        updated_user.hopestar += hopestar_to_add
        updated_user.hopestar_reward_granted = user_total_reward_hopestar
      self.user_table.update_user(updated_user)

      if hopestar_to_add > 0:
        update_channel = client.get_channel(UPDATE_CHANNEL_ID)
        if update_channel is not None:
          await update_channel.send(
              content=
              f"<@{user.user_id}> has been rewarded {hopestar_to_add} hopestar"
          )
    print("Done updating user bet hopestar")

  async def close_trading(self, client):
    bid_channel = client.get_channel(BID_CHANNEL_ID)
    if bid_channel is not None:
      await bid_channel.send(
          content=
          "@everyone Trading has closed. All transactions have been processed."
      )

    ongoing_bids = get_ongoing_bids()

    for bid in ongoing_bids:
      bid_id = bid.bid_id

      updated_bid = copy.deepcopy(bid)

      winner_id = bid.winner_id

      if winner_id is None:
        updated_bid.status = BidStatus.CLOSED.value
        await bid_channel.send(
            content=
            f"[**CLOSED**][**Bid {bid_id}**]: Bid {bid_id} toward <@{bid.receiver_id}> has been closed because there is no winner"
        )
      else:
        winner_offer = from_dict_to_offer(bid.current_offers[winner_id])
        price = winner_offer.price
        transaction_successful = processed_transaction(bid.winner_id,
                                                       bid.receiver_id,
                                                       bid.star_amount, price)
        if transaction_successful:
          updated_bid.status = BidStatus.SUCCESS.value
          await bid_channel.send(
              content=
              f"[**SUCCESS**][**Bid {bid_id}**]: <@{winner_id}> has won the bid, successfully purchased {bid.star_amount} star(s) with {price} from <@{bid.receiver_id}>"
          )
        else:
          updated_bid.status = BidStatus.FAILED.value
          await bid_channel.send(
              content=
              f"[**FAIL**][**Bid {bid_id}**]: Transaction failed due to insufficient point or star balance"
          )

      self.bid_table.update_bid(updated_bid)
