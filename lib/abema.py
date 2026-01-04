from lib.yt_dlp import YoutubeDL
from lib.yt_dlp.extractor.abematv import AbemaTVTitleIE

import json

Ydl = YoutubeDL()
Abema = Ydl.get_info_extractor("AbemaTVTitle")

def get_categories():
    categories = Abema._call_api('v1/video/genres', "", {'subscriptionType': 'basic', 'device': 'web', 'genreStructured': 'true'})
    cats = []
    for category in categories['genres']:
        episodes = fetch_episodes(category['id'], False)
        if len(episodes) != 0 :
            cats.append(category)
    return cats

def fetch_episodes(category, all=True):
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
        if not all:
            finish = True
    return data

def fetch_episode(id):
    #https://api.p-c3-e.abema-tv.com/v1/video/programs/19-171_s1_p1?division=0&include=tvod
    data = Abema._call_api(f'v1/video/programs/{id}', "", {'division': '0', 'include': 'tvod'})
    #https://api.p-c3-e.abema-tv.com/v1/video/b/programs/536-1_s1_p1
    air =  Abema._call_api(f'v1/video/b/programs/{id}', "", None)
    data['data'] = air['data']
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
def find_title(title):
    data = []
    #https://api.p-c3-e.abema-tv.com/v1/search/modules?query=%E3%81%86%E3%81%97%E3%81%8A&device=WEB&itemLimit=8
    resp = Abema._call_api(f'v1/search/modules', "", {'query': title, 'device': 'WEB', 'itemLimit': '5'})
    for module in resp['modules'] :
        if module['id'] == 'package':
            item = module['items'] 
            results = item['content']['results']
            for result in results :
                if 'videoSeries' in result['contentData'].keys():
                    info = result['contentData']['videoSeries']
                    series = result['contentId']
                else:
                    info = result['contentData']['videoSeason']
                    series = info['seriesId'] + '/' + result['contentId']
                object = {}
                object['title'] = info['title']
                object['image'] = info['thumbnailPortrait']['urlPrefix']\
                    + '/' + info['thumbnailPortrait']['filename']\
                    + '?' + info['thumbnailPortrait']['query']

                object['url'] = series
                data.append(object)
    return data

def fetch_series_info(series_id):
    resp = Abema._call_api(f'v1/contentlist/series/{series_id}', "", {'includes': 'liveEvent.slot'})

    return resp
