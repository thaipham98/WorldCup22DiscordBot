class Offer:

  def __init__(self, bid_id, sender_id, price, time_stamp):
    self.bid_id = bid_id
    self.sender_id = sender_id
    self.price = price
    self.time_stamp = time_stamp

  def to_dict(self):
    return {
        'bid_id': self.bid_id,
        'sender_id': self.sender_id,
        'price': self.price,
        'time_stamp': self.time_stamp
    }

  def __repr__(self):
    return "Offer bid_id:%s sender_id:%s price:%s time_stamp:%s" % (
        self.bid_id, self.sender_id, self.price, self.time_stamp)

  def to_payload(self):
    return {
        'bid_id': self.bid_id,
        'sender_id': self.sender_id,
        'price': self.price,
        'time_stamp': self.time_stamp
    }

    
