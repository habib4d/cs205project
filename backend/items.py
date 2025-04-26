from match import *
from helper_functions import *

def get_starting_items(timeline):
    '''Returns a dict with puuid to list of starting item'''
    item_data = read_item_file()
    pairing = timeline_participant_to_puuid(timeline)

    items = []
    frame = timeline['info']['frames'][1]
    for event in frame['events']:
        if 'itemId' in event:
            items.append(event)

    item_dict = { puuid: [] for puuid in pairing.values() }
    for item in items:
        if item['type'] == 'ITEM_PURCHASED':
            itemId = str(item['itemId'])
            data = item_data[itemId]
            if 'into' not in data:
                participantId = item['participantId']
                puuid = pairing[participantId]
                item_dict[puuid].append(itemId)
    return item_dict

def get_legendary_items(timeline):
    '''Returns a dict with puuid to list of item ids in order\n'''
    item_data = read_item_file()
    pairing = timeline_participant_to_puuid(timeline)

    items = []
    for frame in timeline['info']['frames'][2:]:
        for event in frame['events']:
            if 'itemId' in event:
                items.append(event)

    
    item_dict = { puuid: [] for puuid in pairing.values() }
    for item in items:
        if item['type'] == 'ITEM_PURCHASED':
            itemId = str(item['itemId'])
            if itemId in ['1083']:
                # removes cull
                continue
            data = item_data[itemId]
            if 'into' not in data:
                if 'Trinket' not in data['tags'] and 'Consumable' not in data['tags']:
                    participantId = item['participantId']
                    puuid = pairing[participantId]
                    item_dict[puuid].append(itemId)
    return item_dict

def itemid_dict_to_name_dict(item_dict):
    for puuid in item_dict:
        item_dict[puuid] = get_item_names(item_dict[puuid])
    return item_dict

def get_end_items_from_player_index(match_raw, idx):
    ''' Returns a list of item ids given a summoner index '''
    item_ids = []
    for i in range(7):
        id = match_raw['info']['participants'][idx][f'item{i}']
        item_ids.append(id)
    return item_ids

def get_end_items_all_summoners(match_raw):
    items = []
    for i in range(10):
        items.append(get_end_items_from_player_index(match_raw, i))
    return items

def get_item_match_data(timeline):
    starting_items = get_starting_items(timeline)
    legendary_items = get_legendary_items(timeline)
    return starting_items, legendary_items
    

if __name__ == '__main__':
    match_id = 'NA1_5264134274'
    region = 'americas'

    timeline = get_match_timeline(match_id, region)
    items = get_item_match_data(timeline)
    