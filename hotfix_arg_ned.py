from replit import db
from result import Result
from backup_db import backup_database

# User ids
nvm = '727084338675449906'
manh = '454821393981243414'
kidz = '468290455952556043'
louis = '268475624715190274'
tung = '303238612319862787'
duc_ember = '741694621666639965'
hieu = '775984015525543967'

dd = '382751403518590977'
bb_besthu = '690285703933853775'
bach_nguyen = '919240081552863252'
kingbach = '607522866778472478'
maxjo = '249403106100510721'
ee = '343447057979408407'
openai = '1045682335326146601'
hungry = '324217720360927233'

# stat keys
win = 'win'
draw = 'draw'
loss = 'loss'


def update_user_stat():
  db[user_table][nvm][win] -= 1
  db[user_table][manh][win] -= 1
  db[user_table][kidz][win] -= 1
  db[user_table][louis][loss] -= 1
  db[user_table][tung][win] -= 1
  db[user_table][duc_ember][win] -= 1
  db[user_table][hieu][win] -= 1

  db[user_table][dd][win] -= 1
  db[user_table][bb_besthu][win] -= 1
  db[user_table][bach_nguyen][loss] -= 1
  db[user_table][kingbach][win] -= 1
  db[user_table][maxjo][loss] -= 1
  db[user_table][ee][win] -= 1
  db[user_table][openai][win] -= 1
  db[user_table][hungry][loss] -= 1


all_users = [
  nvm, manh, kidz, louis, tung, duc_ember, hieu, dd, bb_besthu, bach_nguyen,
  kingbach, maxjo, ee, openai, hungry
]

# Table names
user_table = 'user'
match_table = 'match'

# user table fields
score = 'score'
hopestar = 'hopestar'
history = 'history'
used_hopestar = 'used_hopestar'
result = 'result'

# corrupted match
argen_ned_match = '5982939'


def update_user_score_and_result():
  for user_id in db[user_table]:

    #print(user_id)
    user_result = db[user_table][user_id][history][argen_ned_match][result]

    delta_score_after_match = Result[user_result].value

    print(delta_score_after_match)

    current_user_score = db[user_table][user_id][score]

    #substract score

    db[user_table][user_id][
      score] = current_user_score - delta_score_after_match

    #clear
    db[user_table][user_id][history][argen_ned_match][result] = ''

  # for user_id in all_users:
  #   user_result = db[user_table][user_id][history][argen_ned_match][result]
  #   delta_score_after_match = Result[user_result].value

  #   # TODO: correct the scores
  #   # db[user_table][user_id][score] -= delta_score_after_match

  #   # TODO: clear the result for users
  #   # db[user_table][user_id][history][argen_ned_match][result] = ''

  # print('id', user_id, '|', 'result', user_result, '|', 'delta',
  #       delta_score_after_match, '|', 'score',
  #       db[user_table][user_id][score])


def update_match_result():
  print(db[match_table][argen_ned_match][result])
  # TODO: update match result
  db[match_table][argen_ned_match][result] = '2-2'


# TODO: backup DB then run update
# backup_database()
# update_user_score_and_result()
# update_match_result()
# update_user_stat()