from replit import db

import events_api
from match import Match
from match_table import MatchTable
from user_table import UserTable
from bet_type import BetType
from calculator import Calculator
from random import randint
from result import Result
import copy
from user import User
import datetime


class Updator:

  def __init__(self):
    self.api = events_api.Event_API()
    self.match_table = MatchTable()
    self.user_table = UserTable()
    self.calculator = Calculator()

  def _from_event_to_match(self, event):
    if event is None:
      return None

    event_id = event['id']
    #print(event_id)
    match = self.api.get_event(event_id)

    if match['success'] != 1:
      #print(match)
      print("Cannot convert event to match")
      return None

    match_id = match['results'][0]['id']
    home = match['results'][0]['home']['name']
    away = match['results'][0]['away']['name']
    time = int(match['results'][0]['time'])

    event_odd = self.api.get_event_odds(event_id)

    if event_odd['success'] != 1:
      print("Cannot get the event odd")
      return None

    match_odd = event_odd['results']
    matching_dir = int(match_odd['stats']['matching_dir'])

    result = match_odd['odds']['1_2'][0]['ss']
    is_over = (match['results'][0]['ss'] is not None)

    asian_handicap = 0
    over_under = 0
    if match_odd['odds']['1_2'][0]['time_str'] is None:
      asian_handicap = float(
        match_odd['odds']['1_2'][0]['handicap']) * matching_dir
    else:
      match_entity = self.match_table.view_match(str(event_id))
      if match_entity is not None:
        asian_handicap = match_entity.asian_handicap
    if match_odd['odds']['1_3'][0]['time_str'] is None:
      over_under = float(match_odd['odds']['1_3'][0]['handicap'])
    else:
        match_entity = self.match_table.view_match(str(event_id))
        if match_entity is not None:
          over_under = match_entity.over_under
    return Match(match_id, home, away, asian_handicap, over_under, result,
                 time, is_over)

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
          #print("old:", old_match_payload)
          #print("new:", updated_match_payload)
          self.match_table.update_match(updated_matches_map[match_id])
    print("Done updating ended matches")

    
  
  def _get_upcoming_events(self):
    current_time = datetime.datetime.now()
    today = "{:02d}".format(current_time.year) + "{:02d}".format(
    current_time.month) + "{:02d}".format(current_time.day)

    result = self.api.get_upcoming_daily_events(today)
    #print(result)

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

    for match in matches:
      if match.id not in map:
        map[match.id] = match

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
            #changed_odd_matches.append(updated_matches_map[match_id])
            #print("old:", old_match_payload)
            #print("new:", updated_match_payload)
            self.match_table.update_match(updated_matches_map[match_id])
    print("Done updating upcoming matches")
    #return changed_odd_matches

  def update_user_bet_history(self, user_id):
    user = self.user_table.view_user(str(user_id))
    matches = self.match_table.list_all_matches()
    updated_user = copy.deepcopy(user)
    for match in matches:
      match_id = match.id
      if match_id not in updated_user.history:
        updated_user.history[match_id] = {
          "bet_option": BetType.UNCHOSEN.value,
          "result": "",
          'time': match.time
        }
      if match.is_over:
        #user did not bet
        #updated_user = copy.deepcopy(user)
        if updated_user.history[match_id][
            'bet_option'] == BetType.UNCHOSEN.value:
          updated_user.history[match_id]['bet_option'] = randint(1, 4)

        #print(updated_user.history[match_id]['result'] == '')
        #print(updated_user.history[match_id]['result'] == '')
        if updated_user.history[match_id]['result'] == '':
          result = self.calculator.calculate(
            updated_user.history[match_id]['bet_option'], match.asian_handicap,
            match.over_under, match.result)
          #print(updated_user.name, match_id, result.name)

          updated_user.history[match_id]['result'] = result.name
          #print(match_id, updated_user.history[match_id]['result'])
          updated_user.score += result.value

          if result == Result.WIN or result == Result.HALF_WIN:
            updated_user.win += 1

          if result == Result.LOSS or result == Result.HALF_LOSS:
            updated_user.loss += 1

          if result == Result.DRAW:
            updated_user.draw += 1

    #print(updated_user.name, updated_user.score, updated_user.history)
    self.user_table.update_user(updated_user)

  def update_all_user_bet_history(self):
    users = self.user_table.view_all()

    matches = self.match_table.list_all_matches()

    for user in users:
      #print(user)
      updated_user = copy.deepcopy(user)
      for match in matches:
        match_id = match.id
        if match_id not in updated_user.history:
          #print("processing:", match_id)
          #print("before:", user.history)
          #print(type(user.history))
          # updated_user = User(user.user_id, user.name, user.channel_id, user.channel_name, user.win, user.draw, user.loss, user.score, user.history)
          # updated_user.history[match_id] = {}
          # updated_user.history[match_id]['bet_option'] = BetType.UNCHOSEN
          # updated_user.history[match_id]['result'] = ""
          # updated_user.history[match_id]['time'] = match.time

          updated_user.history[match_id] = {
            "bet_option": BetType.UNCHOSEN.value,
            "result": "",
            'time': match.time
          }

          # user.history[match_id] = {}
          # user.history[match_id]['bet_option'] = BetType.UNCHOSEN
          # user.history[match_id]['result'] = ""
          # user.history[match_id]['time'] = match.time

          #print("after:", user.history)
          # user.history[match_id] = {

          # }
          #print("here")

        if match.is_over:
          #user did not bet
          #updated_user = copy.deepcopy(user)
          if updated_user.history[match_id][
              'bet_option'] == BetType.UNCHOSEN.value:
            updated_user.history[match_id]['bet_option'] = randint(1, 4)

          #print(updated_user.history[match_id]['result'] == '')
          #print(updated_user.history[match_id]['result'] == '')
          if updated_user.history[match_id]['result'] == '':
            result = self.calculator.calculate(
              updated_user.history[match_id]['bet_option'],
              match.asian_handicap, match.over_under, match.result)
            #print(updated_user.name, match_id, result.name)

            updated_user.history[match_id]['result'] = result.name
            #print(match_id, updated_user.history[match_id]['result'])
            updated_user.score += result.value

            if result == Result.WIN or result == Result.HALF_WIN:
              updated_user.win += 1

            if result == Result.LOSS or result == Result.HALF_LOSS:
              updated_user.loss += 1

            if result == Result.DRAW:
              updated_user.draw += 1

      #print(updated_user.name, updated_user.score, updated_user.history)
      self.user_table.update_user(updated_user)

    print("Done updating user bet history")
