from daily_bet import DailyBet

class Match:
    def __init__(self, id, home, away, asian_handicap, over_under, result, time, is_over):
        self.id = id
        self.home = home
        self.away = away
        self.asian_handicap = asian_handicap
        self.over_under = over_under
        self.result = result
        self.time = time
        self.is_over = is_over

    def to_payload(self):
        return {'home': self.home, 'away': self.away, 'asian_handicap': self.asian_handicap, 'over_under': self.over_under, 'result': self.result, 'time': self.time, 'is_over': self.is_over}

    def to_daily_bet(self):
      return DailyBet(match_id= self.id,time=self.time,home=self.home,away=self.away,asian_handicap=self.asian_handicap,over_under=self.over_under)


