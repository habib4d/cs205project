import requests
import time
from helper_functions import make_url


def get_puuid(summoner_name, tag, region):
    '''
    Returns puuid given name#tag and region\n
    valid regions: 'americas', 'asia', 'europe', 'esports'
    '''
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}'
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(f'status code: {resp.status_code}')

    player_info = resp.json()
    return player_info['puuid']

def get_ign(puuid, region):
    '''
    Returns ign and tag geven puuid and region\n
    valid regions: 'americas', 'asia', 'europe', 'esports'
    '''
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(f'status code: {resp.status_code}')

    result = resp.json()
    ign = result['gameName']
    tag = result['tagLine']

    return ign, tag

def summoners_in_league(server, queue, tier, division, rcounter):
    '''
    Returns a list of all puuids for each summoner in a tier and division\n
    valid servers: br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ru, sg2, tr1, tw2, vn2\n
    queue: 'RANKED_SOLO_5x5'\n
    tier: 'IRON', 'GOLD', 'MASTER', etc...\n
    division: 'I', 'II', 'III', or 'IV', use 'I' for MASTER+ tier
    '''
    rcounter = rcounter
    page = 1
    summoners = []
    while True:
        url = f'https://{server}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}'
        api_url = make_url(url)
        resp = requests.get(api_url)
        if resp.status_code != 200:
            print(f'status code: {resp.status_code}')
        
        data = [ [e['puuid'], e['leaguePoints']] for e in resp.json() ]
        rcounter += 1

        if data:
            summoners += data
            page += 1
            if rcounter % 20 == 0:
                time.sleep(1)
            if rcounter % 100 == 0:
                print('request limit reached ... 2 min wait')
                time.sleep(120)
        else:
            break
    return summoners, rcounter