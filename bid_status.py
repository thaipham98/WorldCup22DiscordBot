from enum import Enum

bid_status_converter = {0: 'ONGOING', 1: 'SUCCESS', 2: 'FAILED', 3: 'CLOSED'}


class BidStatus(Enum):
    ONGOING = 0
    SUCCESS = 1
    FAILED = 2
    CLOSED = 3
