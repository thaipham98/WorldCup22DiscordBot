class Record:
  def __init__(self, user_id, name, channel_name, win, draw, loss, score, history, hopestar, start_match_index, hopestar_reward_granted):
    self.user_id = user_id
    self.channel_name = channel_name
    self.name = name
    self.win = win
    self.draw = draw
    self.loss = loss
    self.score = score
    self.history = history 
    self.hopestar = hopestar
    self.start_match_index = start_match_index
    self.hopestar_reward_granted = hopestar_reward_granted

  def __repr__(self): 
    return "Record name:% s win:% s draw:% s loss:% s score:% s history:% s" % (self.name, self.win, self.draw, self.loss, self.score, self.history)
