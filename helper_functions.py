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

def date_to_epoch_range(date: datetime):
    '''
    converts date object to epoch (seconds) range
    '''
    t0 = date.timestamp()
    return t0, t0 + 86399

if __name__ == '__main__':
    date = datetime(2025, 4, 11, tzinfo=ZoneInfo('America/Los_Angeles'))
    utc = timezone.utc
    new_date = date.astimezone(utc)
    print(date_to_epoch_range(date))
    print(date_to_epoch_range(new_date))

