from offer import Offer
from typing import List, Dict


class Bid:

  def __init__(self,
               bid_id,
               time_stamp,
               receiver_id,
               star_amount,
               current_offers={},
               winner_id=None,
               status=0):
    self.bid_id = bid_id
    self.time_stamp = time_stamp
    self.status = status
    self.receiver_id = receiver_id
    self.star_amount = star_amount
    self.current_offers = current_offers
    self.winner_id = winner_id

  def to_payload(self):
    return {
        'bid_id': self.bid_id,
        'time_stamp': self.time_stamp,
        'status': self.status,
        'receiver_id': self.receiver_id,
        'star_amount': self.star_amount,
        'current_offers': self.current_offers,
        'winner_id': self.winner_id
    }

  # def get_all_offers(self):
  #   all_offers = self.current_offers
  #   all_offers_ascending = sorted(all_offers,
  #                                 key=lambda x: x.time_stamp,
  #                                 reverse=True)
  #   return all_offers_ascending
