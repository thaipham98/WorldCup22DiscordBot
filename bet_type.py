from enum import Enum

bet_type_converter = {0: 'UNCHOSEN', 1: 'HOME', 2: 'AWAY', 3: 'OVER', 4: 'UNDER'}
  

class BetType(Enum):
    UNCHOSEN = 0
    HOME = 1
    AWAY = 2
    OVER = 3
    UNDER = 4
    
    