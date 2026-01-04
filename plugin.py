import sys
from urllib.parse import parse_qsl, urlparse
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon

import re

from lib import abema
from lib import Cache
from lib import Search

from lib import log, show_info, check_if_kodi_supports_manifest, extract_info, extract_manifest_url_from_info, get_url, refresh, get_adaptive_type_from_url, localize, clear_thumbnails

_HANDLE = int(sys.argv[1])

def list_videos(category):
    xbmcplugin.setPluginCategory(_HANDLE, category)
    xbmcplugin.setContent(_HANDLE, 'movies')
    
    videos = []
    context = (localize(30020), 'save_series')

    videos = Cache().get_episodes(category)

    for video in videos:
        label = video['series_title']

        list_item = xbmcgui.ListItem(label=label, offscreen=True)
        vid_info = list_item.getVideoInfoTag()
        vid_info.setTitle(label)
        vid_info.setGenres([video['genre']])
        vid_info.setTvShowTitle(video['name'])
        vid_info.setMediaType('video')
        list_item.setProperty('IsPlayable', 'true')
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['fanart'], 'poster': video['fanart']})

        if context:
            context_menu_item = (context[0], 'RunPlugin({})'.format(get_url(action=context[1], series=video['series'], series_title=video['series_title'])))
            list_item.addContextMenuItems([context_menu_item])

            
        url = get_url(action='list_series', category=category, series=video['series'], series_title=video['series_title'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(_HANDLE)

def list_series(category, series, title):
    xbmcplugin.setPluginCategory(_HANDLE, title)
    xbmcplugin.setContent(_HANDLE, 'movies')

    videos = []
    context = (localize(30020), 'save_season')

    videos = Cache().get_series_episodes(series)

    for video in videos:
        if video['episodeGroups'] :    
            for eg in video['episodeGroups']:
                label = video['name'] + "-" +  eg['name']
                list_item = xbmcgui.ListItem(label=label, offscreen=True)
        
                vid_info = list_item.getVideoInfoTag()
                vid_info.setTitle(label)
                vid_info.setGenres([category])
                vid_info.setTvShowTitle(video['name'])
                vid_info.setMediaType('video')
                list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
                list_item.setProperty('IsPlayable', 'true')

                if context:
                    context_menu_item = (context[0], 'RunPlugin({})'.format(get_url(action=context[1], series=title, season=video['season'], group=eg['id'], title=video.get('name',""))))
                    list_item.addContextMenuItems([context_menu_item])

                url = get_url(action='list_episodes', season=video['season'], group=eg['id'], title=label)
                is_folder = True
                xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
        else:
            label = video['name']
            list_item = xbmcgui.ListItem(label=label, offscreen=True)
        
            vid_info = list_item.getVideoInfoTag()
            vid_info.setTitle(label)
            vid_info.setGenres([category])
            vid_info.setTvShowTitle(video['name'])
            vid_info.setMediaType('video')
            list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
            list_item.setProperty('IsPlayable', 'true')

            if context:
                context_menu_item = (context[0], 'RunPlugin({})'.format(get_url(action=context[1], series=series, season=video['season'], group="None", title=label)))
                list_item.addContextMenuItems([context_menu_item])
            
            url = get_url(action='list_episodes', season=video['season'], group="None", title=label)
            is_folder = True
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(_HANDLE)

def list_episodes(season, group, title):
    xbmcplugin.setPluginCategory(_HANDLE, title)
    xbmcplugin.setContent(_HANDLE, 'movies')

    videos = []
    context = None

    videos = Cache().get_eg_episodes(season, group)

    for video in videos:
        label = video['name']
        list_item = xbmcgui.ListItem(label=label, offscreen=True)
        
        vid_info = list_item.getVideoInfoTag()
        vid_info.setTitle(label)
        vid_info.setTvShowTitle(label)
        vid_info.setPlot(video['desc'])
        vid_info.setMediaType('video')
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        list_item.setProperty('IsPlayable', 'true')

        url = get_url(action='play', video=video['video'])
        is_folder = False

        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(_HANDLE)
    
def get_categories():
    cats = abema.get_categories()

    return cats

def list_categories():
    xbmcplugin.setPluginCategory(_HANDLE, '...')
    xbmcplugin.setContent(_HANDLE, 'movies')

    categories = get_categories()
    for item in categories:
        list_item = xbmcgui.ListItem(label=item['name'], offscreen=True)

        vid_info = list_item.getVideoInfoTag()
        vid_info.setTitle(item['name'])
        vid_info.setGenres([item['id']])
        vid_info.setMediaType('video')

        url = get_url(action='listing', category=item['id'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    #search
    list_item = xbmcgui.ListItem(label='Search', offscreen=True)
    url = get_url(action='search')
    is_folder = True
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)

def play_video(video):
    url = f'https://abema.tv/video/episode/{video}'
    info = extract_info(url)
    url = extract_manifest_url_from_info(info)

    adaptive_type = False

    if url:
        adaptive_type = get_adaptive_type_from_url(url)

    if not url or not check_if_kodi_supports_manifest(adaptive_type):
        err_msg = localize(33000)
        log(err_msg)
        show_info(err_msg)
        raise Exception(err_msg)

    # proxy
    res = urlparse(url)
    url = 'http://127.0.0.1:51041/video.abema/' + res.netloc + res.path
    list_item = xbmcgui.ListItem(info['title'], path=url)
    list_item.setProperty("IsPlayable","true")
    
    if adaptive_type:
        list_item.setMimeType('application/x-mpegURL')
        list_item.setContentLookup(False)
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        #list_item.setProperty('inputstream.adaptive.manifest_type', adaptive_type)

    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=list_item)

def save_series(series, title):
    title = re.sub(r'[\\/:*?"<>|]+','', title)
    path = xbmcaddon.Addon().getSetting('savefolder') + title
    
    scr = f'yt-dlp -f b https://abema.tv/video/title/{series}'
    try:
        if not xbmcvfs.exists(path):
            #create folder
            xbmcvfs.mkdir(path)
        path = path + '/dl.sh'
        #create dl.sh
        dl_sh = xbmcvfs.File(path, 'w')
        dl_sh.write(scr)
        dl_sh.close()
    except Exception as e:  
        xbmc.log(f"エラーが発生しました: {e}", xbmc.LOGERROR)
    return

def save_season(series, season, group, title):
    title = re.sub(r'[\\/:*?"<>|]+','', title)
    series = re.sub(r'[\\/:*?"<>|]+','', series)
    
    path = xbmcaddon.Addon().getSetting('savefolder') + series
    series_id = season.split('_')[0]
    scr = ''
    if group != 'None':
        scr = f'yt-dlp -f b https://abema.tv/video/title/{series_id}?s={season}'
    else:
        scr = f'yt-dlp -f b https://abema.tv/video/title/{series_id}'

    try:
        if not xbmcvfs.exists(path):
            #create folder
            xbmcvfs.mkdir(path)

        path = path + '/' + title
        if not xbmcvfs.exists(path):
            #create folder
            xbmcvfs.mkdir(path)
        
        path = path + '/dl.sh'
        #create dl.sh
        dl_sh = xbmcvfs.File(path, 'w')
        dl_sh.write(scr)
        dl_sh.close()
    except Exception as e:  
        xbmc.log(f"エラーが発生しました: {e}", xbmc.LOGERROR)
    return


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        action = params['action']
        if action == 'listing':
            list_videos(params['category'])
        elif action == 'play':
            play_video(params['video'])
        elif action == 'list_series':
            list_series(params['category'], params['series'], params['series_title'])
        elif action == 'list_episodes':
            list_episodes(params['season'], params['group'], params['title'])
        elif action == 'save_series':
            save_series(params['series'], params['series_title'])
        elif action == 'save_season':
            save_season(params['series'], params['season'], params['group'], params.get('title',"シーズン1"))
        elif action == 'thumbnails':
            clear_thumbnails()
        elif action == 'search':
            Search().list(_HANDLE)
        elif action == 'cache':
            Cache().delete_cache()
            func = "Container.Refresh"
            xbmc.executebuiltin(func)
        else:
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])
