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

# Table names
user_table = 'user'
match_table = 'match'

# user table fields
score = 'score'
hopestar = 'hopestar'
history = 'history'
used_hopestar = 'used_hopestar'
result = 'result'
name = 'name'


def check_user_score_and_result():
  all_res = []
  for user_id in db[user_table]:
    user_record = db[user_table][user_id]
    score = 0
    user_name = user_record[name]
    for match_id in user_record[history]:
      bet_result = user_record[history][match_id][result]
      score += Result[bet_result].value
    print(user_name, score)


check_user_score_and_result()
