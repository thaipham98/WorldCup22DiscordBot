from replit import db
import replit
from verification import Verification

class VerificationTable:
  def __init__(self):
    self.table = db['verification']

  def add_verification(self, verification):
    user_id = verification.user_id
    verification_payload = verification.to_payload()
    if user_id not in self.table:
      self.table[user_id] = verification_payload

  def delete_verification(self, user_id):
    if user_id in self.table:
      del self.table[user_id]

  def view_verification(self, user_id):
    
    if user_id in self.table:
      return Verification(user_id, channel_name=self.table[user_id]['channel_name'], verify_channel_id=self.table[user_id]['verify_channel_id'], verified=self.table[user_id]['verified'])

  def verify(self, user_id):
    if user_id in self.table[user_id]:
      self.table[user_id]['verified'] = True
    return
    
    