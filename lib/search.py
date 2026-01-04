import sqlite3 as sql
import xbmcgui
import xbmcplugin
import re
from lib.abema import fetch_episodes, fetch_episode, find_title, fetch_series_info
from lib import database, localize, get_url

class Search:
    def insert(self, title):
        with sql.connect(database()) as conn:
            conn.execute(f'INSERT OR REPLACE INTO history (title) VALUES (?)', (title,),)

    def select(self):
        favs = []

        with sql.connect(database()) as conn:
            cur = conn.execute(f'SELECT title FROM history ORDER BY id DESC')
            favs = cur.fetchall()

        return favs

    def delete(self, title):
        with sql.connect(database()) as conn:
            conn.execute(f'DELETE FROM history WHERE title = ?', (title,),)

    def list(self, _HANDLE):
        histories = self.select()
        list = []
        title = ""
        
        for history in histories:
            li = xbmcgui.ListItem(history[0])
            list.append(li)

        #keybord input
        li = xbmcgui.ListItem('INPUT title')
        list.append(li)
        
        dialog = xbmcgui.Dialog()
        selected_index = dialog.select('history', list)
        if selected_index >= len(histories):
            dialog = xbmcgui.Dialog()
            title = dialog.input('Input title', type=xbmcgui.INPUT_ALPHANUM)
            match = re.match(r'^abema:(.*)$', title)
            if match:
                tmp = match.group(1)
                param = tmp.split('/')
                series = param[0]
                season_id = None
                if len(param) > 1:
                    season_id = param[1].replace(' ', '_')
                info = fetch_series_info(series)
                title = info['title']
                if season_id :
                    for season in info['seasons'] :
                        if season['id'] != season_id :
                            continue;
                        title = season.get('name', title)
            self.insert(title)

        elif selected_index >= 0:
            title = histories[selected_index]
        if not title:
            return
        results = find_title(title)

        # create video list
        xbmcplugin.setPluginCategory(_HANDLE, 'Search')
        xbmcplugin.setContent(_HANDLE, 'movies')

        context = (localize(30020), 'save_series')

        for result in results:
            label = result['title']
            liz = xbmcgui.ListItem(label, offscreen=True)
            vid_info = liz.getVideoInfoTag()
            vid_info.setTitle(label)
            vid_info.setMediaType('video')
            liz.setArt({'thumb': result['image']})
            liz.setProperty('IsPlayable', 'true')
            context_menu_item = (context[0], 'RunPlugin({})'.format(get_url(action=context[1], series=result['url'], series_title=label)))
            liz.addContextMenuItems([context_menu_item])
            url = get_url(action='list_series', category='Search', series=result['url'], series_title=label)
            xbmcplugin.addDirectoryItem(handle=_HANDLE, url=url, listitem=liz, isFolder=True)

        xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(_HANDLE)
