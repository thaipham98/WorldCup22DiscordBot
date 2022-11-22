from bet_type import BetType
from result import Result
from user import User

class Calculator:
  def is_asian_handicap(self, choosen):
    return choosen == BetType.HOME.value or choosen == BetType.AWAY.value

  def is_over_under(self, choosen):
    return choosen == BetType.OVER.value or choosen == BetType.UNDER.value

  def calculate_asian_handicap(self, chosen, asian_handicap_odd, result):
    home_score = result[0]
    away_score = result[1]

    if asian_handicap_odd == 0:
      if home_score == away_score:
        return Result.DRAW
      if home_score > away_score:        
        return Result.WIN if chosen == BetType.HOME.value else Result.LOSS
      if home_score < away_score:
        return Result.LOSS if chosen == BetType.HOME.value else Result.WIN
    if asian_handicap_odd < 0:
      away_score += abs(asian_handicap_odd)
      if home_score - away_score == 0.25:
        return Result.HALF_WIN if chosen == BetType.HOME.value else Result.HALF_LOSS
      if home_score - away_score == -0.25:
        return Result.HALF_LOSS if chosen == BetType.HOME.value else Result.HALF_WIN
      if home_score - away_score == 0:
        return Result.DRAW
      if home_score - away_score >= 0.5:
        return Result.WIN if chosen == BetType.HOME.value else Result.LOSS
      if home_score - away_score <= -0.5:
        return Result.LOSS if chosen == BetType.HOME.value else Result.WIN
    if asian_handicap_odd > 0:
      home_score += abs(asian_handicap_odd)
      if away_score - home_score == 0:
        return Result.DRAW
      if away_score - home_score == 0.25:
        return Result.HALF_WIN if chosen == BetType.AWAY.value else Result.HALF_LOSS
      if away_score - home_score == -0.25:
        return Result.HALF_LOSS if chosen == BetType.AWAY.value else Result.HALF_WIN
      if away_score - home_score >= 0.5:
        return Result.WIN if chosen == BetType.AWAY.value else Result.LOSS
      if away_score - home_score <= -0.5:
        return Result.LOSS if chosen == BetType.AWAY.value else Result.WIN

    return None
     
  def calculate_over_under(self, chosen, over_under_odd, result):
    sum = result[0] + result[1]

    if sum == over_under_odd:
      return Result.DRAW
    elif sum >= over_under_odd + 0.5:
      if chosen == BetType.OVER.value:
        return Result.WIN
      if chosen == BetType.UNDER.value:
        return Result.LOSS
    elif sum <= over_under_odd - 0.5:
      if chosen == BetType.OVER.value:
        return Result.LOSS
      if chosen == BetType.UNDER.value:
        return Result.WIN
    elif sum == over_under_odd + 0.25:
      if chosen == BetType.OVER.value:
        return Result.HALF_WIN
      if chosen == BetType.UNDER.value:
        return Result.HALF_LOSS
    elif sum == over_under_odd - 0.25:
      if chosen == BetType.OVER.value:
        return Result.HALF_LOSS
      if chosen == BetType.UNDER.value:
        return Result.HALF_WIN

    return 0

  def parse(self, result):
    split = result.split('-')
    return [int(split[0]), int(split[1])]
  
  def calculate(self, chosen, asian_handicap_odd, over_under_odd, result):
    parsed_result = self.parse(result)
    if len(parsed_result) == 0:
      return 0
      
    if chosen == BetType.UNCHOSEN.value:
      return Result.DRAW
    else:
      if self.is_asian_handicap(chosen):
        return self.calculate_asian_handicap(chosen, asian_handicap_odd, parsed_result)

      elif self.is_over_under(chosen):
        return self.calculate_over_under(chosen, over_under_odd, parsed_result)
          
      


        
      
    