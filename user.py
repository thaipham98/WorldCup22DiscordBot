class User:
  def __init__(self, id, name, channel_id, channel_name, win, draw, loss, score, history):
        self.id = id
        self.name = name
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.win = win
        self.draw = draw
        self.loss = loss
        self.score = score
        self.history = history

  def to_payload(self):
        return {'name': self.name, 'channel_id': self.channel_id, 'channel_name': self.channel_name, 'win': self.win, 'draw': self.draw, 'loss': self.loss, 'score': self.score, "history": self.history}
