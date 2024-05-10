# database.py
import os
from user_table import UserTable
from match_table import MatchTable

db_url = os.getenv('REPLIT_DB_URL')

def get_user_table():
    return UserTable()

def get_match_table():
    return MatchTable()

def backup_table(name):
    # Implementation here
    pass

def backup_database():
    backup_table(name='user')
    backup_table(name='match')
