import pytz
import os
import datetime
import requests

db_url = os.getenv('REPLIT_DB_URL')


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
  backup_table(name='bid')
  backup_table(name='verification')
