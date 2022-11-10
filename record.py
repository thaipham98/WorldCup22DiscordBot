class Record:
  def __init__(self, name, win, draw, loss, history):
    self.name = name
    self.win = win
    self.draw = draw
    self.loss = loss
    self.history = history 

  def __repr__(self): 
    return "Record name:% s win:% s draw:% s loss:% s history:% s" % (self.name, self.win, self.draw, self.loss, self.history) 