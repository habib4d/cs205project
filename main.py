import requests
import sqlite3
import time
#import pandas as pd


def make_url(url):
    '''
    Adds an api key to a url
    '''
    with open('.api_key.txt', 'r') as f:
        api_key = f.read()

    c = '?'
    if c in url:
        c = '&'

    return f'{url}{c}api_key={api_key}'


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
    result = resp.json()
    ign, tag = result['gameName'], result['tagLine']

    return ign, tag


def get_match_ids(puuid, region, count):
    '''
    Returns a list of match ids with size given puuid and region
    valid regions: 'americas', 'apac', 'europe', 'sea'
    '''
    url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid + 
        f"/ids?start=0&count={count}"
    )
    api_url = make_url(url)
    print(puuid)
    page = 1
    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids

def get_match_raw(match_id, region):
    '''
    Returns a dictionary of all of the match data given match_id and region
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
    match_data = resp.json()
    return match_data

def find_player_data(match_data, puuid):
    '''
    Given match data and a puuid for a player from that match returns a list
    return list: [champion played, kills, deaths, assists, win/loss]
    '''
    players = match_data['metadata']['participants']
    i = players.index(puuid)

    player_data = match_data['info']['participants'][i]
    champion = player_data['championName']
    k = player_data['kills']
    d = player_data['deaths']
    a = player_data['assists']
    win = player_data['win']

    return [champion, k, d, a, win]

def get_match_data(puuid, match_ids, region):
    keys = ['champion', 'kills', 'deaths', 'assists', 'win']
    data = { key: [] for key in keys }
    for id in match_ids:
        raw_data = get_match_raw(id, region)
        player_data = find_player_data(raw_data, puuid)
        #print(player_data)

        for i in range(len(player_data)):
            key = keys[i]
            stat = player_data[i]
            data[key].append(stat)

    return keys, data
    
def update_db(keys, data, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    for i in range(len(data[keys[0]])):
        values = tuple( data[key][i] for key in keys )
        print(values)
        try:
            cursor.execute(''' insert into player_game_stats(champion, kills, deaths, assists, win) \
                        values (?, ?, ?, ?, ?); ''', values)
        except sqlite3.Error as er:
            conn.close()
            print(f'SQL error: {er}')
            return
        
    conn.commit()

def summoners_in_league(region, queue, tier, division):
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
        url = f'https://na1.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}'
        api_url = make_url(url)
        resp = [ e['puuid'] for e in requests.get(api_url).json() ]

        if resp:
            summoners += resp
            page += 1
            if (page % 99) == 0:
                time.sleep(120) # makes sure to not exceed request limit
        else:
            break
    return summoners






if __name__ == '__main__':

    mydb = 'stats.db'
    conn = sqlite3.connect(mydb)
    cursor = conn.cursor()


    ''' habib4d_puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'
        SussyBaka2_puuid = "pntMCPZS4W3MPpYWYyHTkzqrod8CzRl7Cxt1QhULmyzaS_S7EmIaI19ngDu1v2NThAZhfjpTllPkEg" '''
  
    region = 'americas'
    server = 'NA1' 
    
    # retrieves all puuids of a certain rank
    masters_puuids = summoners_in_league('RANKED_SOLO_5x5', 'MASTER', "I")
    master_match_ids = []
    for puuid in masters_puuids[0:3]:
        #grabs 100 matches per puuid for the first 3 puuids
        #time sleep 120 to not over do rate limit
        match_id = get_match_ids(puuid, region, 100)
        master_match_ids.append(match_id)
        time.sleep(120)

    unique_match_ids = set()

    for lst in master_match_ids:
        for match_id in lst:
            unique_match_ids.add(match_id)

    for match_id in unique_match_ids:
        unix_date = get_match_raw(match_id, region)['info']['gameCreation']

        try:
            cursor.execute('insert into matches values (?, ?)',(match_id,unix_date))
        except sqlite3.Error as er:
            conn.close()
            f'SQL error: {er}'

        time.sleep(1.2)
    
    cursor.commit()


    try:
        cursor.execute(' select * from matches ')
    except sqlite3.Error as er:
        conn.close()
        f'SQL error: {er}' 
    
    result = cursor.fetchall()
    cursor.close()
    print(result)
    
