from replit import db

import events_api
from match import Match
from match_table import MatchTable
from user_table import UserTable

class Migration:
    def __init__(self):
        self.api = events_api.Event_API()
        self.matchDAO = MatchTable()
        self.userDAO = UserTable()
        
    def to_match(self, event):
        
        event_id = event['id']
        #print(event_id)
        match = self.api.get_event(event_id)

        if match['success'] != 1:
            #print(match)
            print("Cannot convert event to match")
            return None

        match_id = match['results'][0]['id']
        home = match['results'][0]['home']['name']
        away = match['results'][0]['away']['name']
        time = int(match['results'][0]['time'])

        event_odd = self.api.get_event_odds(event_id)

        if event_odd['success'] != 1:
            print("Cannot get the event odd")
            return None

        match_odd = event_odd['results']
        matching_dir = int(match_odd['stats']['matching_dir'])

        result = match_odd['odds']['1_2'][0]['ss']
        is_over = (match['results'][0]['ss'] is not None)
        asian_handicap = float(match_odd['odds']['1_2'][0]['handicap']) * matching_dir
        over_under = float(match_odd['odds']['1_3'][0]['handicap'])

        return Match(match_id, home, away, asian_handicap, over_under, result, time, is_over)

    def insert_matches_data(self):
        result = self.api.get_upcoming_events()

        if result['success'] != 1:
            print("Cannot get upcoming events")
            return

        total = result['pager']['total']
        page = result['pager']['page']
        per_page = result['pager']['page']

        events = result['results']

        while total > per_page:
            page += 1
            result = self.api.get_upcoming_events(page=page)

            if result['success'] != 1:
                print("Cannot get upcoming events")
                return

            events += result['results']
            total -= per_page
          
        
        for event in events:
            match = self.to_match(event)
            #print(match.__str__())
            self.matchDAO.add_match(match)

    def add_hopestar(self):
        for key in self.userDAO.table:
          db["user"][key]['hopestar'] = 2

          for match_id in db["user"][key]["history"]:
              db["user"][key]["history"][match_id]['used_hopestar'] = 0
          #user['hopestar'] = 2
      
      
      














