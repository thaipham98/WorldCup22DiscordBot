import os
import requests

token = os.getenv('API_TOKEN')
url = "https://api.b365api.com"
sport_id = 1  #Soccer
league_id = 1040  #C1
source = 'ysb88'


class Event_API:

    def __init__(self):
        self.url = url
        self.token = token
        self.sport_id = sport_id
        self.league_id = league_id

    def get_ended_events(self, sport_id=sport_id, league_id=league_id, page=1):
        payload = {
            'sport_id': sport_id,
            'league_id': league_id,
            'token': token,
            'page': page
        }
        endpoint = url + "/v3/events/ended"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_upcoming_events(self,
                            sport_id=sport_id,
                            league_id=league_id,
                            page=1):
        payload = {
            'sport_id': sport_id,
            'league_id': league_id,
            'token': token,
            'page': page
        }
        endpoint = url + "/v3/events/upcoming"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_ended_daily_event(self,
                              day,
                              sport_id=sport_id,
                              league_id=league_id,
                              page=1):
        payload = {
            'sport_id': sport_id,
            'league_id': league_id,
            'token': token,
            'page': page,
            'day': day
        }
        endpoint = url + "/v3/events/ended"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_inplay_events(self, sport_id=sport_id, league_id=league_id):
        payload = {
            'sport_id': sport_id,
            'league_id': league_id,
            'token': token
        }
        endpoint = url + "/v3/events/inplay"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_upcoming_daily_events(self,
                                  day,
                                  sport_id=sport_id,
                                  league_id=league_id,
                                  page=1):
        payload = {
            'sport_id': sport_id,
            'league_id': league_id,
            'token': token,
            'page': page,
            'day': day
        }
        endpoint = url + "/v3/events/upcoming"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_event_odds(self, event_id, source=source):
        payload = {'event_id': event_id, 'source': source, 'token': token}
        endpoint = url + "/v2/event/odds"
        response = requests.get(endpoint, payload)

        return response.json()

    def get_event(self, event_id):
        payload = {'event_id': event_id, 'token': token}
        endpoint = url + "/v1/event/view"
        response = requests.get(endpoint, payload)

        return response.json()


# if __name__ == "__main__":
#     api = Event_API()

#     api.get_upcoming_events(sport_id, league_id)
