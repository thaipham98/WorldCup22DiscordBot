from replit import db
import replit
from user import User

class UserTable:
  def __init__(self):
    self.table = db['user']

  def add_user(self, user):
    user_id = str(user.user_id)
    #print("add", type(user_id))
    user_payload = user.to_payload()
    if user_id not in self.table:
      # print("creating user_id", user_id)
      # print("adding", type(user_id))
      self.table[user_id] = user_payload

    # print("from add_user self", self.table)
    # print("from add_user", db['user'])

  def delete_user(self, user_id):
    print(db['user'])
    if user_id in self.table:
      del self.table[user_id]
    
    #print(db['user'])

  def view_user(self, user_id):
    # print(type(user_id))
    # print("from view UserTable self", self.table)
    # print("from view UserTable", db['user'])
    
    if user_id in self.table:
      #print("found")
      return User(user_id, name=self.table[user_id]['name'],channel_id=self.table[user_id]['channel_id'],channel_name=self.table[user_id]['channel_name'],win=self.table[user_id]['win'], draw=self.table[user_id]['draw'],loss=self.table[user_id]['loss'],score=self.table[user_id]['score'], history=replit.database.to_primitive(self.table[user_id]['history']))
      # return User(user_id, name=self.table.get(user_id).get('name'),channel_id=self.table.get(user_id).get('channel_id'),channel_name=self.table.get(user_id).get('channel_name'),win=self.table.get(user_id).get('win'), draw=self.table.get(user_id).get('draw'),loss=self.table.get(user_id).get('loss'),score=self.table.get(user_id).get('score'), history=replit.database.to_primitive(self.table.get(user_id).get('history')))
    
    return None

  def update_user(self, user):
    user_id = user.user_id
    if user_id not in self.table:
      return

    #print('727084338675449906' == user_id)
    #print(db['user']['727084338675449906']['history'])
    #print(db['user'])
    #print(self.table)
    #print("curr:",self.table[user_id]['history'])
    #print("new:", user.history)
    if self.table[user_id]['name'] != user.name:
      self.table[user_id]['name'] = user.name

    if self.table[user_id]['channel_id'] != user.channel_id:
      self.table[user_id]['channel_id'] = user.channel_id

    if self.table[user_id]['channel_name'] != user.channel_name:
      self.table[user_id]['channel_name'] = user.channel_name

    if self.table[user_id]['win'] != user.win:
      self.table[user_id]['win'] = user.win

    if self.table[user_id]['draw'] != user.draw:
      self.table[user_id]['draw'] = user.draw

    if self.table[user_id]['loss'] != user.loss:
      self.table[user_id]['loss'] = user.loss

    if self.table[user_id]['score'] != user.score:
      self.table[user_id]['score'] = user.score

    if self.table[user_id]['history'] != user.history:
      self.table[user_id]['history'] = user.history
      #self.table[user_id].set(['history'],user.history)

    # for match_id in user.history.keys():
    #   if match_id not in self.table[user_id]['history']:
    #     print("setting history")
    #     # self.table[user_id]['history'][match_id] = {
    #     #     "bet_option": 0,
    #     #     "result": "",
    #     #     'time': 123
    #     # }
    #     print(user.history[match_id] == {
    #         "bet_option": 0,
    #         "result": "",
    #         'time': 123
    #     })
    #     self.table[user_id]['history'][match_id] = user.history[match_id]
    #     #set(self.table[user_id]['history'][match_id], {})
    #     if 'bet_option' in user.history[match_id]:
    #       print("set bet option to", user.history[match_id]['bet_option'])
    #       self.table[user_id]['history'][match_id]['bet_option'] = user.history[match_id]['bet_option']
    #     if 'result' in user.history[match_id]:
    #       print("set result to", user.history[match_id]['result'])
    #       self.table[user_id]['history'][match_id]['result'] = user.history[match_id]['result']
    #     if 'time' in user.history[match_id]:
    #       print("set time to", user.history[match_id]['time'])
    #       self.table[user_id]['history'][match_id]['time'] = user.history[match_id]['time']
    #   else:
    #     if 'bet_option' in user.history[match_id]:
    #       if 'bet_option' not in self.table[user_id]['history'][match_id]:
    #         self.table[user_id]['history'][match_id]['bet_option'] = user.history[match_id]['bet_option']
    #       else:
    #         if self.table[user_id]['history'][match_id]['bet_option'] != user.history[match_id]['bet_option']:
    #           self.table[user_id]['history'][match_id]['bet_option'] = user.history[match_id]['bet_option']
              
    #     if 'result' in user.history[match_id]:
    #       if 'result' not in self.table[user_id]['history'][match_id]:
    #         self.table[user_id]['history'][match_id]['result'] = user.history[match_id]['result']
    #       else:
    #         if self.table[user_id]['history'][match_id]['result'] != user.history[match_id]['result']:
    #           self.table[user_id]['history'][match_id]['result'] = user.history[match_id]['result']
    #     if 'time' in user.history[match_id]:
    #       if 'time' not in self.table[user_id]['history'][match_id]:
    #         self.table[user_id]['history'][match_id]['time'] = user.history[match_id]['time']
    #       else:
    #         if self.table[user_id]['history'][match_id]['time'] != user.history[match_id]['time']:
    #           self.table[user_id]['history'][match_id]['time'] = user.history[match_id]['time']
  
  def view_all(self):
    users = []

    for user_id in self.table.keys():
      user = User(user_id, name=self.table[user_id]['name'],channel_id=self.table[user_id]['channel_id'],channel_name=self.table[user_id]['channel_name'],win=self.table[user_id]['win'], draw=self.table[user_id]['draw'],loss=self.table[user_id]['loss'],score=self.table[user_id]['score'], history=replit.database.to_primitive(self.table[user_id]['history']))
      users.append(user)

    return users

    
    
    