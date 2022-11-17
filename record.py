class Record:
  def __init__(self, user_id, name, win, draw, loss, score, history):
    self.user_id = user_id
    self.name = name
    self.win = win
    self.draw = draw
    self.loss = loss
    self.score = score
    self.history = history 

  def __repr__(self): 
    return "Record name:% s win:% s draw:% s loss:% s score:% s history:% s" % (self.name, self.win, self.draw, self.loss, self.score, self.history)