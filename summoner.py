import requests
import time
from helper_functions import make_url


def get_puuid(summoner_name, tag, region):
    '''
    Returns puuid given name#tag and region
    valid regions: 'americas', 'asia', 'europe', 'esports'
    '''
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}'
    api_url = make_url(url)
    resp = requests.get(api_url)
    player_info = resp.json()
    
    return player_info['puuid']

def get_ign(puuid,  region):
    '''
    Returns ign and tag geven puuid and region
    valid regions: 'americas', 'asia', 'europe', 'esports'
    '''
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}'
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(resp.satus_code)

    result = resp.json()
    ign = result['gameName']
    tag = result['tagLine']

    return ign, tag

def summoners_in_league(server, queue, tier, division):
    '''
    Returns a list of all puuids for each summoner in a tier and division
    valid regions: br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ru, sg2, tr1, tw2, vn2
    queue: 'RANKED_SOLO_5x5'
    tier: 'IRON', 'GOLD', 'MASTER', etc...
    division: 'I', 'II', 'III', or 'IV', use 'I' for MASTER+ tier
    '''
    page = 1
    summoners = []
    while True:
        url = f'https://{server}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}'
        api_url = make_url(url)
        resp = [ [e['puuid'], e['leaguePoints']] for e in requests.get(api_url).json() ]

        if resp:
            summoners += resp
            page += 1
            if (page % 99) == 0:
                time.sleep(120) # makes sure to not exceed request limit
        else:
            break
    return summoners