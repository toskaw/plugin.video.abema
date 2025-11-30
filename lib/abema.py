from lib.yt_dlp import YoutubeDL
from lib.yt_dlp.extractor.abematv import AbemaTVTitleIE

import json

Ydl = YoutubeDL()
Abema = Ydl.get_info_extractor("AbemaTVTitle")

def get_categories():
    categories = Abema._call_api('v1/video/genres', "", {'subscriptionType': 'basic', 'device': 'web', 'genreStructured': 'true'})
    return categories['genres']

def fetch_episodes(category):
    data = []
    finish = False
    next = ''
    while not finish:
        resp = Abema._call_api(f'v1/video/featureGenres/{category}/cards', "", {'limit': 20, 'onlyFree':'true', 'next': next})
        if resp['cards'] :    
            data.extend(resp['cards'])
        if resp['paging']:
            next = resp['paging']['next']
        else:
            finish = True
    return data

def fetch_episode(id):
    (uid, token) = fetch_api_token()
    resp = requests.get(URL_LIST_INFO.format(id, uid, token), headers={'x-tver-platform-type': 'web'}, timeout=10)
    data = resp.json()

    return data

def fetch_seasons(series_id):
    data = []
    resp = Abema._call_api(f'v1/contentlist/series/{series_id}', "", {'includes': 'liveEvent.slot'})
    data.extend(resp['seasons'])

    return data
    
def fetch_episode_group(season, episode):
    data = []
    offset = 0
    finish = False
    if episode != 'None':
        while not finish:
            resp = Abema._call_api(f'v1/contentlist/episodeGroups/{episode}/contents', "", {'seasonId': season, 'limit': 20, 'includes': 'liveEvent.slot', 'offset': offset})
            if resp['episodeGroupContents'] :
                data.extend(resp['episodeGroupContents'])
                offset += len(resp['episodeGroupContents'])
            else:
                finish = True
    else:
        while not finish:
            series = season.split('_')[0]
            #https://api.p-c3-e.abema-tv.com/v1/video/series/89-66/programs?seasonId=89-66_s99&order=-seq&limit=20&offset=0
            resp = Abema._call_api(f'v1/video/series/{series}/programs', "", {'seasonId': season, 'limit': 20, 'order': '-seq', 'offset': offset})
            if resp['programs'] :
                data.extend(resp['programs'])
                offset += len(resp['programs'])
            else:
                finish = True
    return data
