import requests
import sqlite3
#import pandas as pd


def make_url(url):
    with open('.api_key.txt', 'r') as f:
        api_key = f.read()

    c = '?'
    if c in url:
        c = '&'

    return f'{url}{c}api_key={api_key}'

def get_puuid(summoner_name, tag, region):
    url = (f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}')
    api_url = make_url(url)
    resp = requests.get(api_url)
    return resp
    player_info = resp.json()
    return player_info['puuid']

def get_match_ids(puuid, region, count):
    url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid + 
        f"/ids?start=0&count={count}"
    )
    api_url = make_url(url)

    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids

def get_match_raw(match_id, region):
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

def masters_puuids_retrieval(region, count):
    queue = "RANKED_SOLO_5x5"
    if region == 'americas':
        region = 'na1'
    url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/league/v4/masterleagues/by-queue/" + 
        queue
    )
    api_url = make_url(url)
    print(api_url)
    print("https://na1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=RGAPI-2711f6ce-843f-4a6f-8317-0fa47b9f070b")
    resp = requests.get(api_url)
    masters_player_data = resp.json()
    list_of_masters_puuids = []
    i = 0
    while i < count:
        if (masters_player_data["entries"][i]["inactive"]) == True:
            i += 1
            count += 1
            continue
        else:
            list_of_masters_puuids.append(masters_player_data["entries"][i]["puuid"])
            i += 1
    return list_of_masters_puuids

if __name__ == '__main__':
    mydb = 'stats.db'
    habib4d_puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'
    SussyBaka2_puuid = "pntMCPZS4W3MPpYWYyHTkzqrod8CzRl7Cxt1QhULmyzaS_S7EmIaI19ngDu1v2NThAZhfjpTllPkEg"
    #puuid = SussyBaka2_puuid #change this to habib to work with yours
    region = 'americas'
    masters_puuids = masters_puuids_retrieval(region, 100)
    for puuid in masters_puuids:
            match_ids = get_match_ids(puuid, region, 1)

            keys, data = get_match_data(puuid, match_ids, region)
            update_db(keys, data, mydb)

    #masters_puuids_retrieval(region, 30)

    conn = sqlite3.connect(mydb)
    cursor = conn.cursor()

    try:
        cursor.execute(''' select * from player_game_stats; ''')
    except sqlite3.Error as er:
        conn.close()
        f'SQL error: {er}'
    
    result = cursor.fetchall()
    print(result)
