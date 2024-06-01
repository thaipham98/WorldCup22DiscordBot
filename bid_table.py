from replit import db
from bid import Bid


class BidTable:

  def __init__(self):
    self.table = db['bid']

  def add_bid(self, bid):
    bid_id = str(bid.bid_id)
    bid_payload = bid.to_payload()

    if bid_id not in self.table:
      self.table[bid_id] = bid_payload

  def delete_bid(self, bid_id):
    if bid_id in self.table:
      del self.table[bid_id]

  def view_bid(self, bid_id):
    if bid_id in self.table:

      return Bid(bid_id,
                 time_stamp=self.table[bid_id]['time_stamp'],
                 status=self.table[bid_id]['status'],
                 receiver_id=self.table[bid_id]['receiver_id'],
                 star_amount=self.table[bid_id]['star_amount'],
                 current_offers=self.table[bid_id]['current_offers'],
                 winner_id=self.table[bid_id]['winner_id'])

    return None

  def view_all(self):
    bids = []

    for bid_id in self.table.keys():
      bid = Bid(bid_id,
                time_stamp=self.table[bid_id]['time_stamp'],
                status=self.table[bid_id]['status'],
                receiver_id=self.table[bid_id]['receiver_id'],
                star_amount=self.table[bid_id]['star_amount'],
                current_offers=self.table[bid_id]['current_offers'],
                winner_id=self.table[bid_id]['winner_id'])
      bids.append(bid)

    return bids

  def update_bid(self, bid):
    bid_id = str(bid.bid_id)

    if bid_id not in self.table:
      return

    if self.table[bid_id]['bid_id'] != bid_id:
      self.table[bid_id]['bid_id'] = bid_id

    if self.table[bid_id]['time_stamp'] != bid.time_stamp:
      self.table[bid_id]['time_stamp'] = bid.time_stamp
    # Check and update status
    if self.table[bid_id]['status'] != bid.status:
      self.table[bid_id]['status'] = bid.status

    # Check and update receiver_id
    if self.table[bid_id]['receiver_id'] != bid.receiver_id:
      self.table[bid_id]['receiver_id'] = bid.receiver_id

    # Check and update star_amount
    if self.table[bid_id]['star_amount'] != bid.star_amount:
      self.table[bid_id]['star_amount'] = bid.star_amount

    # Check and update current_offers
    if self.table[bid_id]['current_offers'] != bid.current_offers:
      self.table[bid_id]['current_offers'] = bid.current_offers

    # Check and update winner_id
    if self.table[bid_id]['winner_id'] != bid.winner_id:
      self.table[bid_id]['winner_id'] = bid.winner_id
