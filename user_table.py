from replit import db
from user import User

class UserTable:
  def __init__(self):
    self.table = db['user']

  def add_user(self, user):
    user_id = str(user.id)
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
      return User(user_id, self.table[user_id]['name'], self.table[user_id]['channel_id'], self.table[user_id]['channel_name'], self.table[user_id]['win'], self.table[user_id]['draw'], self.table[user_id]['loss'], self.table[user_id]['score'], self.table[user_id]['history'])
    
    return None
    
    