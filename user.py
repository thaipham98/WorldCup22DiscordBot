from record import Record
from collections import OrderedDict

most_recent_match = 10


class User:

  def __init__(self, user_id, name, channel_id, channel_name, win, draw, loss,
               score, history, hopestar, start_match_index, hopestar_reward_granted):
    self.user_id = user_id
    self.name = name
    self.channel_id = channel_id
    self.channel_name = channel_name
    self.win = win
    self.draw = draw
    self.loss = loss
    self.score = score
    # {<match_id>: {'bet_option': 'xxx', 'result': 'xxx', 'time': 'xxx', 'used_hopestar': xxx}}
    self.history = history
    self.hopestar = hopestar
    self.start_match_index = start_match_index
    self.hopestar_reward_granted = hopestar_reward_granted


  def get_all_record(self):
    bet_history = []

    ordered_match_history = OrderedDict(
        sorted(self.history.items(), key=lambda x: x[1]['time'], reverse=True))

    for match_id in ordered_match_history:
      detail = self.history[match_id]
      result = detail['result']
      if result != '':
        bet_history.append(result)

    return Record(self.user_id, self.name, self.channel_name, self.win,
                  self.draw, self.loss, self.score, bet_history,
                  self.hopestar, self.start_match_index, self.hopestar_reward_granted)
  
  def to_record(self):
    bet_history = []

    ordered_match_history = OrderedDict(
        sorted(self.history.items(), key=lambda x: x[1]['time'], reverse=True))

    for match_id in ordered_match_history:
      detail = self.history[match_id]
      result = detail['result']
      if result != '':
        bet_history.append(result)

    count = min(most_recent_match, len(bet_history))

    return Record(self.user_id, self.name, self.channel_name, self.win,
                  self.draw, self.loss, self.score, bet_history[:count],
                  self.hopestar, self.start_match_index, self.hopestar_reward_granted)

  def to_payload(self):
    return {
        'user_id': self.user_id,
        'name': self.name,
        'channel_id': self.channel_id,
        'channel_name': self.channel_name,
        'win': self.win,
        'draw': self.draw,
        'loss': self.loss,
        'score': self.score,
        "history": self.history,
        "hopestar": self.hopestar,
        "start_match_index": self.start_match_index,
        "hopestar_reward_granted": self.hopestar_reward_granted
    }
