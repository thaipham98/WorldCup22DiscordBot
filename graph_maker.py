from match_table import MatchTable
from user_table import UserTable

user_table = UserTable()
match_table = MatchTable()

user_current_score = {}
user_list = []
match_list = []


def get_score_from_result(result):
  if result == 'WIN':
    return 10000
  elif result == 'HALF_WIN':
    return 7500
  elif result == 'DRAW':
    return 5000
  elif result == 'HALF_LOSS':
    return 2500
  elif result == 'LOSS':
    return 0
  else:
    return 0


for user in user_table.view_all():
  user_obj = user.to_payload()
  user_list.append(user_obj)
  user_current_score[user_obj['user_id']] = 0

for match in match_table.list_all_matches():
  match_obj = match.to_payload()
  if (match_obj['is_over'] == True):
    match_list.append(match_obj)

sorted_match_list = sorted(match_list, key=lambda x: x['time'])

data_set = []

for match in sorted_match_list:
  match_id = match['id']
  data_row = []
  data_row.append(f"{match['home']}-{match['away']}")
  for user in user_list:
    score = get_score_from_result(user['history'][match_id]['result'])
    user_current_score[user['user_id']] += score
    data_row.append(str(user_current_score[user['user_id']]))
  data_set.append(';'.join(data_row))

bottom_title = ['Matches']
for user in user_list:
  bottom_title.append(user['channel_name'])

print(';'.join(bottom_title))
print('\n'.join(data_set))
