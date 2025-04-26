import requests
import json
import time
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

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

def server_to_region(server):
    d = {'br1': 'americas', 'eun1': 'europe', 'euw1': 'europe' , 'jp1': 'asia', 
         'kr': 'asia', 'la1': 'americas', 'la2': 'americas', 'me1': 'asia', 
         'na1': 'americas', 'oc1': 'asia', 'ru': 'asia', 'sg2': 'asia', 
         'tr1': 'europe', 'tw2': 'asia', 'vn2': 'asia'}
    return d[server]

def check_rcounter(rcounter):
    if rcounter % 20 == 0:
        time.sleep(1)
    if rcounter % 100 == 0:
        print('hit request limit ... 2 min wait')
        time.sleep(120) # makes sure to not exceed request limit

def rank_to_int(rank):
    tier, division, lp = rank[0], rank[1], rank[2]
    tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    divisions = ['IV', 'III', 'II', 'I']

    tier_idx = 0
    while tier != tiers[tier_idx]:
        tier_idx += 1
    div_idx = 0
    while division != divisions[div_idx]:
        div_idx += 1

    a = (400 * tier_idx) if tier_idx <= 6 else 2800
    b = (100 * div_idx) if tier_idx <= 6 else 0
    return a + b + lp

def int_to_rank(num):
    tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    divisions = ['IV', 'III', 'II', 'I']
    
    tier_idx = num // 400
    div_idx = (num - tier_idx) // 100
    lp = num - tier_idx - div_idx
    
    return tiers[tier_idx], divisions[div_idx], lp

def calc_avg_rank(ranks):
    '''Calculates average rank given list of ranks (each ranks is a tuple)'''
    # challenger/gm case
    gm_count = 0
    chall_count = 0
    for rank in ranks:
        if rank[0] == 'GRANDMASTER':
            gm_count += 1
        elif rank[0] == 'CHALLENGER':
            chall_count += 1
    if gm_count > 0 or chall_count > 0:
        if chall_count > gm_count:
            return 'CHALLENGER', 'I', 0
        return 'GRANDMASTER', 'I', 0
    
    # general case
    ranks_nums = []
    for rank in ranks:
        ranks_nums.append(rank_to_int(rank))
    avg = sum(ranks_nums) / len(ranks_nums)
    return int_to_rank(avg)

def date_to_epoch_range(date: datetime):
    '''Converts date object to epoch (seconds) range'''
    t0 = date.timestamp()
    return int(t0), int(t0 + 86399)

def write_items_file():
    ''' Stores most recent item info into items.json '''
    url = 'https://ddragon.leagueoflegends.com/cdn/15.7.1/data/en_US/item.json'
    item_data = requests.get(url).json()
    with open('../loldata/items.json', 'w') as f:
        json.dump(item_data, f, indent=4)
    return 1

def write_champs_file():
    ''' Stores most recent champ info into items.json '''
    url = 'https://ddragon.leagueoflegends.com/cdn/15.8.1/data/en_US/champion.json'
    champ_data = requests.get(url).json()
    with open('../loldata/champs.json', 'w') as f:
        json.dump(champ_data, f, indent=4)
    return 1

def read_item_file():
    with open('../loldata/items.json', 'r') as f:
        item_data = json.load(f)
    return item_data['data']

def read_champs_file():
    with open('../loldata/champs.json', 'r') as f:
        champ_data = json.load(f)
    return champ_data['data']

def get_item_names(item_ids):
    ''' Gets a list of item names from a list of item ids '''
    item_data = read_item_file()
    item_names = []
    for id in item_ids:
        if type(id) != str:
            id = str(id)

        if id == '0':
            item_names.append(None)
        else:
            item_names.append(item_data[id]['name'])
    return item_names

def item_str_to_list(item_string):
    '''Converts item string to list of item ids (each itemId must have len 4)'''
    return [item_string[i:i+4] for i in range(0, len(item_string), 4)]

if __name__ == '__main__':
    print(write_items_file())
    print(write_champs_file())

