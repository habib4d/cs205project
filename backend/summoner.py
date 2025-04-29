import requests
import time
from helper_functions import *
from pprint import pprint


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

        if len(data) > 0:
            summoners += data
            page += 1
            check_rcounter(rcounter)
        else:
            break
    return summoners, rcounter

def get_rank(server, puuid):
    '''
    Returns a player's rank given server and puuid\n
    valid servers: br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ru, sg2, tr1, tw2, vn2\n
    '''
    url = f'https://{server}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}'
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        pprint(f'status code: {resp.status_code}')

    result = resp.json()[0]
    tier = result['tier']
    rank = result['rank']
    lp = result['leaguePoints']

    return tier, rank, lp