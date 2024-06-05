# database.py
import datetime
import os
import requests
import pytz
from user_table import UserTable
from match_table import MatchTable
from bid_table import BidTable
from verification_table import VerificationTable
from replit import db

db_url = os.getenv('REPLIT_DB_URL')


def get_verification_table():
    return VerificationTable()


def get_user_table():
    return UserTable()


def get_bid_table():
    return BidTable()


def get_match_table():
    return MatchTable()


def backup_table(name):
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    dt = datetime.datetime.now(tz)
    today_date_str = dt.strftime('%Y-%m-%d-%H-%M')
    request_url = f"{db_url}/{name}"
    res = requests.get(request_url)

    if not os.path.exists('backup'):
        os.mkdir('backup')

    if not os.path.exists(f"backup/{today_date_str}"):
        os.mkdir(f"backup/{today_date_str}")

    with open(f"backup/{today_date_str}/{name}_table.json", "w") as outfile:
        outfile.write(res.text)


def backup_database():
    backup_table(name='user')
    backup_table(name='match')
    backup_table(name='verification')
    backup_table(name='bid')


# db['user']['1169333893493706812']['score'] = 100000
# print(db['user']['1169333893493706812'])
#del db['user']['379414630256082944']
#db['verification'] = {}
# del db['user']['379414630256082944']
#del db['user']['770647343371911208']
#del db['user']['1169333893493706812']
# # del db['bid']
#db['bid']= {}
# print(db['bid'])
# print(db['user'])
