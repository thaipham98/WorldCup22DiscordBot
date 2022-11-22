from replit import db
from events_api import Event_API
from daily_bet import DailyBet
from match_table import MatchTable


class BetModel:

  def __init__(self):
    self.api = Event_API()
    self.match_table = MatchTable()

  def from_daily_matches_to_daily_bet(self, daily_matches):
    #print(self.match_table.table)
    #print(db['match'])
    daily_bet = []
    for result in daily_matches:
      match_id = result['id']
      match = self.match_table.view_match(match_id)
      if match is not None:
        daily_bet.append(match.to_daily_bet())

    return daily_bet
