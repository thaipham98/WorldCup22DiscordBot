from bet_type import BetType
from result import Result


class Calculator:
  def is_asian_handicap(choosen):
    return choosen == BetType.HOME or choosen == BetType.AWAY

  def is_over_under(choosen):
    return choosen == BetType.OVER or choosen == BetType.UNDER

  def calculate_asian_handicap(choosen, asian_handicap_odd, result):
    home_score = result[0]
    away_score = result[1]

      
    
    

  

  def calculate_over_under(choosen, over_under_odd, result):
    sum = result[0] + result[1]

    if sum == over_under_odd:
      return Result.DRAW
    elif sum >= over_under_odd + 0.5:
      if choosen == BetType.OVER:
        return Result.WIN
      if choosen == BetType.UNDER:
        return Result.LOSS
    elif sum <= over_under_odd - 0.5:
      if choosen == BetType.OVER:
        return Result.LOSS
      if choosen == BetType.UNDER:
        return Result.WIN
    elif sum == over_under_odd + 0.25:
      if choosen == BetType.OVER:
        return Result.HALF_WIN
      if choosen == BetType.UNDER:
        return Result.HALF_LOSS
    elif sum == over_under_odd - 0.25:
      if choosen == BetType.OVER:
        return Result.HALF_LOSS
      if choosen == BetType.UNDER:
        return Result.HALF_WIN
          
    
  
  
  def calculate(self, choosen, asian_handicap_odd, over_under_odd, result):
    if choosen == BetType.UNCHOOSEN:
      return Result.DRAW
    else:
      if self.is_asian_handicap(choosen):
        return self.calculate_asian_handicap(choosen, asian_handicap_odd, result)

      elif self.is_over_under(choosen):
        return self.calculate_over_under(choosen, over_under_odd, result)
          
      


        
      
    