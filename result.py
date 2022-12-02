from aenum import Enum, NoAlias

converter = {
  'WIN': 'W',
  'HALF_WIN': 'HW',
  'LOSS': 'L',
  'HALF_LOSS': 'HL',
  'DRAW': 'D',
  'DOUBLE_WIN': 'W*',
  'DOUBLE_HALF_WIN': 'HW*',
  'DOUBLE_DRAW' : 'D*',
  'DOUBLE_LOSS' : 'L*',
  'DOUBLE_HALF_LOSS' : 'HL*'
}

star = {
  'W': 'W*',
  'HW': 'HW*',
  'D': 'D*',
  'L': 'L*',
  'HL': 'HL*'
}

class Result(Enum):

  _settings_ = NoAlias
  
  DOUBLE_WIN = 20000
  DOUBLE_HALF_WIN = 15000
  DOUBLE_DRAW = 10000
  DOUBLE_LOSS = -20000
  DOUBLE_HALF_LOSS = -10000
  WIN = 10000
  HALF_WIN = 7500
  LOSS = 0
  HALF_LOSS = 2500
  DRAW = 5000

star_converter = {
  Result.WIN : Result.DOUBLE_WIN,
  Result.HALF_WIN : Result.DOUBLE_HALF_WIN,
  Result.DRAW : Result.DOUBLE_DRAW,
  Result.LOSS : Result.DOUBLE_LOSS,
  Result.HALF_LOSS : Result.DOUBLE_HALF_LOSS
}

def get_star_result(result):
  return star_converter[result]

def get_star_name(name):
  return star[name]

def get_result_shorthand(name):
  return converter[name]
