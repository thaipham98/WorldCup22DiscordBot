class Verification:

    def __init__(self,
                 user_id,
                 channel_name,
                 verify_channel_id,
                 verified=False):
        self.user_id = user_id
        self.channel_name = channel_name
        self.verify_channel_id = verify_channel_id
        self.verified = verified

    def to_payload(self):
        return {
            'user_id': self.user_id,
            'channel_name': self.channel_name,
            'verify_channel_id': self.verify_channel_id,
            'verified': self.verified
        }
