import sys
import mariadb
import time
from datetime import datetime, timedelta
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

        if rcounter % 20 == 0:
            time.sleep(1)
        if rcounter % 100 == 0:
            print('hit request limit ... 2 min wait')
            time.sleep(120) # makes sure to not exceed request limit

        player_info = get_ign(puuid, region)
        rcounter += 1

        ign = player_info[0]
        tag = player_info[1]
        
        try:
            cur.execute('''insert into summoners (puuid, ign, tag, tier, subtier, lp)
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
        return 0, rcounter
    
    puuids = cur.fetchall()
    conn.close()
    return puuids

def update_lp_in_summoners_table(server, tier, division, rcounter):
    summoners, rcounter = summoners_in_league(server, 'RANKED_SOLO_5x5', tier, division, rcounter)

    conn = get_conn()
    cur = conn.cursor()

    for summoner in summoners:
        puuid = summoner[0]
        lp = summoner[1] 

        try:
            cur.execute('''update summoners set lp = ? where puuid = ?''', (lp, puuid))
        except mariadb.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return 0, rcounter
        
    conn.commit()
    conn.close()
    return 1, rcounter

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


if __name__ == '__main__':
    puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'