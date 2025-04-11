import sys
import mariadb
import time
from datetime import datetime, timedelta
from main import *
from helper_functions import date_to_epoch_range

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

def add_puuids_to_summoners(server, tier, division):
    '''
    Adds each summoner in tier/division from given server to summoners database
    tier: 'IRON', 'GOLD', 'MASTER', etc...
    division: 'I', 'II', 'III', or 'IV', use 'I' for MASTER+ tier
    '''
    summoners = summoners_in_league(server, 'RANKED_SOLO_5x5', tier, division)
    region = server_to_region(server)
    time.sleep(122)

    conn = get_conn()
    cur = conn.cursor()
    c = 1
    for summoner in summoners:
        puuid = summoner[0]
        lp = summoner[1]

        if (c % 19) == 0:
            time.sleep(2)
        if (c % 99) == 0:
            print('hit request limit ... 2 min wait')
            time.sleep(122) # makes sure to not exceed request limit
        player_info = get_ign(puuid, region)
        ign = player_info[0]
        tag = player_info[1]
        
        try:
            cur.execute('''insert into summoners (puuid, ign, tag, tier, subtier, lp)
                    values (?, ?, ?, ?, ?, ?)''', (puuid, ign, tag, tier, division, lp))
        except mariadb.Error as e:
            print(f"Database error: {e}")
            conn.close()
            return 0
        c += 1

    conn.commit()
    conn.close()
    return 1

def update_lp_in_summoners_table(server, tier, division):
    summoners = summoners_in_league(server, 'RANKED_SOLO_5x5', tier, division)

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
            return 0
        
    conn.commit()
    conn.close()
    return 1

def add_summoner_matches_to_table_one_day(puuid, region, qid, date, rcounter):
    '''
    Adds all matchids for a given summoner on day date to matches table
    valid regions: 'americas', 'apac', 'europe', 'sea'
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json
    date: datetime object
    '''
    start_time, end_time = date_to_epoch_range(date)
    match_ids = get_all_matchids(puuid, region, start_time, end_time, qid)

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
    Adds all matchids for a given summoner from date range (inclusive) to matches table
    valid regions: 'americas', 'apac', 'europe', 'sea'
    queueid: see https://static.developer.riotgames.com/docs/lol/queues.json
    date_start/end: datetime object
    '''
    date = date_start
    while date <= date_end:
        _, rcounter = add_summoner_matches_to_table_one_day(puuid, region, qid, date, rcounter)
        date += timedelta(days=1)

    return rcounter

    


if __name__ == '__main__':
    puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'
    date = datetime(2025, 4, 1)
    date_end = datetime(2025, 4, 12)