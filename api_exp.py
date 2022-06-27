import env
import requests
import time



riot_api_key = env.riot_api_key
my_puuid = 'YUYpGhggndqqGjTbJf_vfCO8r6pEwepm8PTLobOkX9dFVKV5B5QDGhrElvukJfSwSCw4d_4ipPKpFA'

base_url = 'https://americas.api.riotgames.com'
# solo ranked summoner's rift 5v5
queue_id = 420


urls= []

def get_match_history(puuid):
    
    start=  0
    count= 20

    response = requests.get(f'{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue_id}&start={start}&count={count}', headers=env.headers)
    return response.json()

def get_match_data_from(matches):

    match_data = {}

    for match in matches:
        match_stats_url = f'/lol/match/v5/matches/{match}'
        response = requests.get(f'{base_url}{match_stats_url}', headers=env.headers).json()
        
        match_data[match] = response['info']['participants']

    return match_data

if __name__ == '__main__':
    matches = get_match_history(my_puuid)
    data = get_match_data_from(matches)
    for key, values in data.items():
        for participant in values:
            print(f'Each person: {participant["summonerName"]}')
        
