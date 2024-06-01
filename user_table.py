from replit import db
import replit
from user import User


class UserTable:

  def __init__(self):
    self.table = db['user']

  def add_user(self, user):
    user_id = str(user.user_id)
    user_payload = user.to_payload()
    if user_id not in self.table:
      self.table[user_id] = user_payload

  def delete_user(self, user_id):
    if user_id in self.table:
      del self.table[user_id]

  def view_user(self, user_id):
    if user_id in self.table:

      return User(user_id,
                  name=self.table[user_id]['name'],
                  channel_id=self.table[user_id]['channel_id'],
                  channel_name=self.table[user_id]['channel_name'],
                  win=self.table[user_id]['win'],
                  draw=self.table[user_id]['draw'],
                  loss=self.table[user_id]['loss'],
                  score=self.table[user_id]['score'],
                  history=replit.database.to_primitive(
                      self.table[user_id]['history']),
                  hopestar=self.table[user_id]['hopestar'],
                  start_match_index=self.table[user_id]['start_match_index'],
                  hopestar_reward_granted=self.table[user_id]
                  ['hopestar_reward_granted'])

    return None

  def update_user(self, user):
    user_id = user.user_id
    if user_id not in self.table:
      return

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

    if self.table[user_id]['hopestar'] != user.hopestar:
      self.table[user_id]['hopestar'] = user.hopestar

    if self.table[user_id]['start_match_index'] != user.start_match_index:
      self.table[user_id]['start_match_index'] = user.start_match_index

    if self.table[user_id][
        'hopestar_reward_granted'] != user.hopestar_reward_granted:
      self.table[user_id][
          'hopestar_reward_granted'] = user.hopestar_reward_granted

  def view_all(self):
    users = []

    for user_id in self.table.keys():
      user = User(user_id,
                  name=self.table[user_id]['name'],
                  channel_id=self.table[user_id]['channel_id'],
                  channel_name=self.table[user_id]['channel_name'],
                  win=self.table[user_id]['win'],
                  draw=self.table[user_id]['draw'],
                  loss=self.table[user_id]['loss'],
                  score=self.table[user_id]['score'],
                  history=replit.database.to_primitive(
                      self.table[user_id]['history']),
                  hopestar=self.table[user_id]['hopestar'],
                  start_match_index=self.table[user_id]['start_match_index'],
                  hopestar_reward_granted=self.table[user_id]
                  ['hopestar_reward_granted'])
      users.append(user)

    return users

  def get_leaderboard(self):
    leaderboard = self.view_all()
    leaderboard.sort(key=lambda x: x.score, reverse=True)
    return leaderboard
