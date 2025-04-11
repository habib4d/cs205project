import requests
import sqlite3
import time


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
    
    conn.commit()


    try:
        cursor.execute(' select * from matches ')
    except sqlite3.Error as er:
        conn.close()
        f'SQL error: {er}' 
    
    result = cursor.fetchall()
    cursor.close()
    print(result)
    
