import env
import requests
import time
import datetime


riot_api_key = env.riot_api_key
my_puuid = 'YUYpGhggndqqGjTbJf_vfCO8r6pEwepm8PTLobOkX9dFVKV5B5QDGhrElvukJfSwSCw4d_4ipPKpFA'

base_url = 'https://americas.api.riotgames.com'
# solo ranked summoner's rift 5v5
queue_id = 420


urls= []

def get_match_history(puuid):
    start=  0
    count= 100

    response = requests.get(f'{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue_id}&start={start}&count={count}', headers=env.headers)
    return response.json()

def get_match_data_from(match):
    """returns dictionary of match id as key and 
    match data as value"""

    match_data = {}
    
    match_stats_url = f'/lol/match/v5/matches/{match}'
    response = requests.get(f'{base_url}{match_stats_url}', headers=env.headers).json()
    
    match_data[match] = response

    return match_data


class Match:
    def __init__(self,matchid):
        
        self.matchid = matchid
        self.match_data = get_match_data_from(matchid)
        self.participants = self.get_participants()
        self.start_u, self.stop_u, self.creation = self.get_game_time()

        self.puuids = self.match_data[self.matchid]['metadata']['participants']

        self.start_dt = datetime.datetime.fromtimestamp(self.start_u/1000)
        self.stop_dt = datetime.datetime.fromtimestamp(self.stop_u/1000)

        self.game_duration_u = self.stop_u - self.start_u
        self.game_duration_dt = self.stop_dt - self.start_dt

        self.blue_team, self.red_team = self.get_teams()
        self.blue_won = self.get_team_win()
        self.red_won = not self.blue_won

        self.players = {}
        for puuid in self.puuids:
            self.players[puuid] = PlayerAtTimeOfGame(puuid, self).games_before_match
        


    def get_participants(self):
        #print(self.match_data)
        participants = []

        for participant in self.match_data[self.matchid]['info']['participants']:
            participants.append(participant['summonerName'])
        
        return participants

    def get_teams(self):
        blue_team = []
        red_team = []

        for team in self.match_data[self.matchid]['info']['participants']:
            if team['teamId'] == 100:
                blue_team.append(team['summonerName'])
            else:
                red_team.append(team['summonerName'])

        return blue_team, red_team
    

    def get_game_time(self):
        start = self.match_data[self.matchid]['info']['gameStartTimestamp']
        finish = self.match_data[self.matchid]['info']['gameEndTimestamp']
        creation = self.match_data[self.matchid]['info']['gameCreation'] / 1000

        return start, finish, creation

    def get_team_win(self):

        for team in self.match_data[self.matchid]['info']['participants']:
            if team['teamId'] == 100:
                if team['win'] == True:
                    return True
                else:
                    return False

class PlayerAtTimeOfGame:

    def __init__(self, puuid, match):
        self.puuid = puuid
        self.match_data = match.match_data
        self.matchid = match.matchid
        self.creation = int(self.match_data[match.matchid]['info']['gameCreation'] / 1000)
        self.games_before_match = self.get_games_before_current_game()

    def get_games_before_current_game(self):
        limiting_time = self.creation - 1
        response = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?endTime={limiting_time}&queue=420&start=0&count=100', headers=env.headers).json()

        return response


if __name__ == '__main__':
    basic_match_id = 'NA1_4169229565'
    NA1_4169229565 = Match(basic_match_id)
    print(NA1_4169229565.participants)
    print(NA1_4169229565.game_duration_dt)   
    print(NA1_4169229565.blue_team) 
    print(NA1_4169229565.start_u)
    print(NA1_4169229565.players)


    
    
#class Player:
#    def __init__(self, ):
