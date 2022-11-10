from record import Record

most_recent_match = 10

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

  def to_record(self):
    bet_history = []
    
    for match_id in self.history.keys():
      detail = self.history[match_id]
      result = detail['result']
      if result is not None:
        bet_history.append(result)

    count = min(most_recent_match, len(bet_history))

    return Record(self.name, self.win, self.draw, self.loss, bet_history[-count:])
    
  def to_payload(self):
        return {'name': self.name, 'channel_id': self.channel_id, 'channel_name': self.channel_name, 'win': self.win, 'draw': self.draw, 'loss': self.loss, 'score': self.score, "history": self.history}

