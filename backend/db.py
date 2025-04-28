import sys
import mariadb
from datetime import timedelta
from helper_functions import *
from summoner import *
from match import *

def get_conn():
    '''
    Returns connection to lolapp database
    '''
    try:
        conn = mariadb.connect(
            user="jhabib",
            password="123xyz",
            host="localhost",
            port=3306,
            database="lolapp"
        )
    except mariadb.Error as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)
    
    conn.autocommit = False
    return conn

def add_champs_to_db():
    '''
    Adds all lol champs to the db
    '''
    conn = get_conn()
    cur = conn.cursor()
    champs = read_champs_file()

    for champ in champs:
        id = champs[champ]['key']
        short_name = champ
        long_name = champs[champ]['name']

        try:
            cur.execute('''insert into champions(id, short_name, long_name) values (?, ?, ?)''', (id, short_name, long_name))
        except mariadb.Error as e:
            print(f'Database error: {e}')
            conn.close()
            return 0
    conn.commit()
    conn.close()
    return 1

def champ_id_to_short_name(champ_id):
    '''Returns champion short name give champion id (int)'''
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''select short_name from champions where id=?''', (champ_id,))
    except mariadb.Error as e:
        print(f'Database error: {e}')
        conn.close()
        return 0
    
    short_name = cur.fetchall()
    conn.close()
    if not short_name:
        raise ValueError('champ_id is invalid')
    return short_name[0][0]
    
def add_puuids_to_summoners(server, tier, division, rcounter):
    '''
    Adds each summoner in tier/division from given server to summoners database\n
    valid servers: br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ru, sg2, tr1, tw2, vn2\n
    tier: 'IRON', 'GOLD', 'MASTER', etc...\n
    division: 'I', 'II', 'III', or 'IV', use 'I' for MASTER+ tier 
    '''
    summoners, rcounter = summoners_in_league(server, 'RANKED_SOLO_5x5', tier, division, rcounter)
    region = server_to_region(server)
    conn = get_conn()
    cur = conn.cursor()

    for summoner in summoners:
        puuid = summoner[0]
        lp = summoner[1]

        check_rcounter(rcounter)
        player_info = get_ign(puuid, region)
        rcounter += 1

        ign = player_info[0]
        tag = player_info[1]
        
        try:
            cur.execute('''insert into summoners (puuid, ign, tag, tier, division, lp)
                    values (?, ?, ?, ?, ?, ?)''', (puuid, ign, tag, tier, division, lp))
        except mariadb.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return 0, rcounter

    conn.commit()
    conn.close()
    return 1, rcounter

def get_all_puuids_from_db():
    '''returns a list of all puuids in the summoners table'''
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute('''select puuid from summoners''')
    except mariadb.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return 0
    
    puuids = cur.fetchall()
    conn.close()
    return puuids

def update_rank(puuid, tier, division, lp):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute('''update summoners set tier=?, division=?, lp=? where puuid = ?''', (tier, division, lp, puuid))
    except mariadb.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return 0, rcounter
        
    conn.commit()
    conn.close()
    return 1

def add_summoner_matches_to_table_one_day(puuid, region, qid, date, rcounter):
    '''
    Adds all matchids for a given summoner on day date to matches table\n
    valid regions: 'americas', 'apac', 'europe', 'sea'\n
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json\n
    date: datetime object
    '''
    start_time, end_time = date_to_epoch_range(date)
    match_ids, rcounter = get_matchids_from_puuid_epoch_range(puuid, region, start_time, end_time, qid, rcounter)

    conn = get_conn()
    cur = conn.cursor()
    for id in match_ids:
        try:
            cur.execute('''insert ignore into matches (match_id, queue_id, d) values (?, ?, ?)''', (id, qid, date))
        except mariadb.Error as e:
            print(f'Database error: {e}')
            conn.close()
            return 0, rcounter
    conn.commit()
    conn.close()
    return 1, rcounter

def add_summoner_matches_to_table_date_range(puuid, region, qid, date_start, date_end, rcounter):
    '''
    Adds all matchids for a given summoner from date range (inclusive) to matches table\n
    valid regions: 'americas', 'apac', 'europe', 'sea'\n
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json\n
    date_start/end: datetime object\n
    '''
    date = date_start
    while date <= date_end:
        _, rcounter = add_summoner_matches_to_table_one_day(puuid, region, qid, date, rcounter)
        date += timedelta(days=1)

    return 1, rcounter

def add_match_data(match_id, server, rcounter):
    '''
    Adds all match data to the champions match data tables
    valid servers: br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ru, sg2, tr1, tw2, vn2
    '''
    all_data, rcounter = gen_all_match_data(match_id, server, rcounter)
    champ_data = read_champs_file()

    conn = get_conn()
    cur = conn.cursor()
    for puuid in all_data:
        data = all_data[puuid]
        champ_code = data['championId']
        champ = champ_code_to_id(champ_code, champ_data)
        position = data['position']
        win = data['win']
        trinket = data['trinket']
        rank = data['rank']
        tier = rank[0]
        division = rank[1]
        lp = rank[2]
        update_rank(puuid, tier, division, lp)
        avg_rank = data['avg_rank'][0]
        starting_items = None if 'starting_items' not in data else data['starting_items']
        item0 = None if 'item0' not in data else data['item0']
        item1 = None if 'item1' not in data else data['item1']
        item2 = None if 'item2' not in data else data['item2']
        item3 = None if 'item3' not in data else data['item3']
        item4 = None if 'item4' not in data else data['item4']
        item5 = None if 'item5' not in data else data['item5']

        try:
            query = f'''insert ignore into {champ}
(match_id, win, position, individual_rank, game_avg_rank, starting_items, item0, item1, item2, item3, item4, item5, trinket)
values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cur.execute(query, (match_id, win, position, tier, avg_rank, starting_items, item0, item1, item2, item3, item4, item5, trinket))
        except mariadb.Error as e:
            print(f'Database error: {e}')
            conn.close()
            return 0, rcounter
    conn.commit()
    conn.close()
    return 1, rcounter

if __name__ == '__main__':
    puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'
    match_id = 'NA1_5264134274'
    server = 'na1'
    status, rcounter = add_match_data(match_id, server, 1)
    print(f'status: {status}\nrcounter: {rcounter}')