from match import Match
from replit import db

class MatchTable:
  def __init__(self):
    self.table = db['match']


  def view_match(self, match_id : str):
    if match_id not in self.table:
      return None

    return Match(id=match_id, home=self.table[match_id]['home'], away=self.table[match_id]['away'], asian_handicap=self.table[match_id]['asian_handicap'],over_under=self.table[match_id]['over_under'],result=self.table[match_id]['result'],time=self.table[match_id]['time'],is_over=self.table[match_id]['is_over'])
  
  def add_match(self, match):
    match_payload = match.to_payload()
    
    if match.id not in self.table:
        self.table[match.id] = match_payload
  
        