from enum import Enum

converter = {
  'HOME': 'H',
  'HALF_WIN': 'HW',
  'LOSS': 'L',
  'HALF_LOSS': 'HL',
  'DRAW': 'D'
}


class Result(Enum):
  WIN = 10000
  HALF_WIN = 7500
  LOSS = 0
  HALF_LOSS = 2500
  DRAW = 5000


def get_result_shorthand(name):
  return converter[name]
