from replit import db
from migration import Migration

# del db['user']['775984015525543967']
#db['user']['607522866778472478']['history']['5847607']['bet_option'] = 3

# ghana_uruguay = '5882834'
# korea_portugal = '5882865'
# serbia_switz = '5882832'
# cameroon_brazil = '5882833'

# nvm = '727084338675449906'
# hieu = '775984015525543967'

# db['user'][nvm]['hopestar'] = 2
# db['user'][hieu]['hopestar'] = 2

# # db['user'][nvm]['history'][serbia_switz]['result'] = ''
# # db['user'][nvm]['history'][cameroon_brazil]['result'] = ''
# # db['user'][hieu]['history'][serbia_switz]['result'] = ''
# # db['user'][hieu]['history'][cameroon_brazil]['result'] = ''

# # db['match'][serbia_switz]['result'] = ''
# # db['match'][serbia_switz]['is_over'] = False


# db['match'][serbia_switz]['result'] = '1-1'
# db['match'][serbia_switz]['is_over'] = True

# # db['match'][cameroon_brazil]['result'] = ''
# # db['match'][cameroon_brazil]['is_over'] = False

# db['match'][cameroon_brazil]['result'] = '2-1'
# db['match'][cameroon_brazil]['is_over'] = True

migration = Migration()
migration.add_hopestar()



