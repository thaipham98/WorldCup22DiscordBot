class DailyBet:

  def __init__(self, match_id, time, home, away, asian_handicap, over_under):
    self.match_id = match_id
    self.time = time
    self.home = home
    self.away = away
    self.asian_handicap = asian_handicap
    self.over_under = over_under

  def __repr__(self):
    return "DailyBet home:% s away:% s asian_handicap:% s over_under:% s" % (
      self.home, self.away, self.asian_handicap, self.over_under)
