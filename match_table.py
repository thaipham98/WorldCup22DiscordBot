from match import Match
from replit import db

class MatchTable:
  def __init__(self):
    self.table = db['match']

  def add_match(self, match):
    match_payload = match.to_payload()
    match_table = db["match"]
  
    if match.id not in match_table:
        db["match"][match.id] = match_payload
        