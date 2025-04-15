import requests
import time
from pprint import pprint
import json
from helper_functions import *

def get_match_ids_from_puuid(puuid, region, start_time, end_time, queueid, i, count):
    '''
    Returns a list (size count) of match ids for a given summoner\n
    valid regions: 'americas', 'apac', 'europe', 'sea'\n
    start/end time: epoch in seconds\n
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json\n
    i: starting index to get match ids from\n
    count: number of matches past index i to return
    '''
    url = (f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/' + 
           f'ids?startTime={start_time}&endTime={end_time}&queue={queueid}&start={i}&count={count}')
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(f'status code: {resp.status_code}')
        return 0

    match_ids = resp.json()
    return match_ids

def get_matchids_from_puuid_epoch_range(puuid, region, start_time, end_time, queueid, rcounter):
    '''
    Returns a list of all matchids for a given summoner between start_time and end_time\n
    valid regions: 'americas', 'apac', 'europe', 'sea'\n
    start/end time: epoch in seconds\n
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json
    '''
    rcounter = rcounter
    i = 0
    match_ids = []

    while True:
        new_ids = get_match_ids_from_puuid(puuid, region, start_time, end_time, queueid, i, 100)
        rcounter += 1
        if new_ids == [] or new_ids == 0:
            break
        match_ids += new_ids
        i += 100

        if rcounter % 20 == 0:
            time.sleep(1)
        if rcounter % 100 == 0:
            print('hit request limit ... wait 2 min')
            time.sleep(120)
    return match_ids, rcounter

def get_match_raw(match_id, region):
    '''
    Returns a dictionary of all of the match data given match_id and region\n
    valid regions: 'americas', 'apac', 'europe', 'sea'
    '''
    url = (
        "https://" + 
        region + 
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id
    )
    api_url = make_url(url)
    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(f'status code: {resp.status_code}')
        return 0
        
    match_data = resp.json()
    return match_data

def get_match_timeline(match_id, region):
    '''
    Returns match timeline given match_id\n
    valid regions: 'americas', 'apac', 'europe', 'sea'
    '''
    url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline'
    api_url = make_url(url)

    resp = requests.get(api_url)
    if resp.status_code != 200:
        print(f'status code: {resp.status_code}')
        return 0
        
    timeline = resp.json()
    return timeline

def timeline_participant_to_puuid(timeline):
    '''
    Retruns a dictionary key: participantId, value: puuid
    '''
    dict = {}
    for d in timeline['info']['participants']:
        id = d['participantId']
        puuid = d['puuid']
        dict[id] = puuid
    return dict
        

if __name__ == '__main__':
    match_id = 'NA1_5264134274'
    region = 'americas'













# def find_player_data(match_data, puuid):
#     '''
#     Given match data and a puuid for a player from that match returns a list
#     return list: [champion played, kills, deaths, assists, win/loss]
#     '''
#     players = match_data['metadata']['participants']
#     i = players.index(puuid)

#     player_data = match_data['info']['participants'][i]
#     champion = player_data['championName']
#     k = player_data['kills']
#     d = player_data['deaths']
#     a = player_data['assists']
#     win = player_data['win']

#     return [champion, k, d, a, win]

# def get_match_data(puuid, match_ids, region):
#     keys = ['champion', 'kills', 'deaths', 'assists', 'win']
#     data = { key: [] for key in keys }
#     for id in match_ids:
#         raw_data = get_match_raw(id, region)
#         player_data = find_player_data(raw_data, puuid)

#         for i in range(len(player_data)):
#             key = keys[i]
#             stat = player_data[i]
#             data[key].append(stat)

#     return keys, data