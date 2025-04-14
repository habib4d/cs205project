from main import *


def summoners_in_league(queue, tier, division, page):
    url = f'https://na1.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}'
    api_url = make_url(url)
    resp = requests.get(api_url)

    return resp

data = summoners_in_league('RANKED_SOLO_5x5', 'GOLD', 'II', '1')
