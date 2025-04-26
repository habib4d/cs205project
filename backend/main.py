from zoneinfo import ZoneInfo
from datetime import datetime
from summoner import *
from match import *
from db import *


TIERS = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD'
         'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
DIVISIONS = ['IV', 'III', 'II', 'I']

def add_all_puuids_to_db(rcounter, tier):
    '''Adds every summoner with a rank to summoners table'''
    if tier in ('MASTER', 'GRANDMASTER', 'CHALLENGER'):
        _, rcounter = add_puuids_to_summoners('na1', tier, 'I', rcounter)
    else:
        for div in DIVISIONS:
            _, rcounter = add_puuids_to_summoners('na1', tier, div, rcounter)


def add_all_ranked_matches_to_db(start_date, end_date, rcounter):
    '''
    Adds every match within date range from\n
    summoners in summoner table to matches table
    '''
    puuids = get_all_puuids_from_db()
    for e in puuids:
        puuid = e[0]
        _, rcounter = add_summoner_matches_to_table_date_range(puuid, 'americas', 420, start_date, end_date, rcounter)
    return 1, rcounter




if __name__ == '__main__':
    pass
    # start_date = datetime(2025, 4, 10, tzinfo=ZoneInfo('America/Los_Angeles'))
    # end_date = datetime(2025, 4, 10, tzinfo=ZoneInfo('America/Los_Angeles'))
    # status, rcounter = add_all_ranked_matches_to_db(start_date, end_date, 0)
    # print(f'status: {status}\nrcounter: {rcounter}')

    # ---------------------------------------

    # mydb = 'stats.db'
    # conn = sqlite3.connect(mydb)
    # cursor = conn.cursor()


    # ''' habib4d_puuid = '8XG2EdVepNrwc4w5_BnvPWjoGsdULwNIRFKrzoBBI0oskwMlrRzHD6t4vMCZe-tKyPUVlj5_eMR8eQ'    
    #     SussyBaka2_puuid = "pntMCPZS4W3MPpYWYyHTkzqrod8CzRl7Cxt1QhULmyzaS_S7EmIaI19ngDu1v2NThAZhfjpTllPkEg" '''
  
    # region = 'americas'
    # server = 'NA1' 
    
    # # retrieves all puuids of a certain rank
    # masters_puuids = summoners_in_league('RANKED_SOLO_5x5', 'MASTER', "I")
    # master_match_ids = []
    # for puuid in masters_puuids[0:3]:
    #     #grabs 100 matches per puuid for the first 3 puuids
    #     #time sleep 120 to not over do rate limit
    #     match_id = get_match_ids(puuid, region, 100)
    #     master_match_ids.append(match_id)
    #     time.sleep(120)

    # unique_match_ids = set()

    # for lst in master_match_ids:
    #     for match_id in lst:
    #         unique_match_ids.add(match_id)

    # for match_id in unique_match_ids:
    #     unix_date = get_match_raw(match_id, region)['info']['gameCreation']

    #     try:
    #         cursor.execute('insert into matches values (?, ?)',(match_id,unix_date))
    #     except sqlite3.Error as er:
    #         conn.close()
    #         f'SQL error: {er}'

    #     time.sleep(1.2)
    
    # conn.commit()


    # try:
    #     cursor.execute(' select * from matches ')
    # except sqlite3.Error as er:
    #     conn.close()
    #     f'SQL error: {er}' 
    
    # result = cursor.fetchall()
    # cursor.close()
    # print(result)
    
