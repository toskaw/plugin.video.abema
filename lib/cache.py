import sqlite3 as sql
import json

from time import time

from lib.abema import fetch_episodes, fetch_episode_group, fetch_seasons
from lib import database, strip_or_none


class Cache:
    def get(self, category):
        data = None

        with sql.connect(database()) as conn:
            cur = conn.execute(f'SELECT data FROM categories WHERE id = ?', (category,),)
            results = cur.fetchall()

        if len(results) > 0:
            data = json.loads(results[0][0])   

        return data
    
    def get_all(self):
        data = []
        
        with sql.connect(database()) as conn:
            cur = conn.execute(f'SELECT id, data FROM categories')
            results = cur.fetchall()

        for result in results:
            data.append({'id': str(result[0]), 'json': json.loads(result[1])})  

        return data

    def insert(self, category, data, expire_after=14400.0):
        expires_at = round(time() + expire_after)
        
        with sql.connect(database()) as conn:
            conn.execute(f'INSERT OR REPLACE INTO categories (id,expires,data) VALUES (?,?,?)', (category, expires_at, json.dumps(data),),)


    def delete_expired(self):
        with sql.connect(database()) as conn:
            conn.execute(f'DELETE FROM categories WHERE expires <= ?', (round(time()),),)
            conn.execute(f'DELETE FROM series WHERE expires <= ?', (round(time()),),)
            conn.execute(f'DELETE FROM episodes WHERE expires <= ?', (round(time()),),)

    def delete_cache(self):
        with sql.connect(database()) as conn:
            conn.execute(f'DELETE FROM categories')
            conn.execute(f'DELETE FROM series')
            conn.execute(f'DELETE FROM episodes')
        
    def get_or_download(self, category):
        json_episodes = self.get(category)
        if not json_episodes:
            json_episodes = fetch_episodes(category)
            self.insert(category, json_episodes)
        return json_episodes

    def get_episode_group(self, series):
        data = None

        with sql.connect(database()) as conn:
            cur = conn.execute(f'SELECT data FROM series WHERE id = ?', (series,),)
            results = cur.fetchall()

        if len(results) > 0:
            data = json.loads(results[0][0])   

        return data

    def insert_episode_group(self, series, data, expire_after=14400.0):
        expires_at = round(time() + expire_after)
        
        with sql.connect(database()) as conn:
            conn.execute(f'INSERT OR REPLACE INTO series (id,expires,data) VALUES (?,?,?)', (series, expires_at, json.dumps(data),),)
            
    def get_or_download_series(self, series):
        json_episodes = self.get_episode_group(series)
        if not json_episodes:
            json_episodes = fetch_seasons(series)
            self.insert_episode_group(series, json_episodes)
        return json_episodes

    def get_episode_list(self, season, eg):
        data = None
        id = season + '_' + eg
        with sql.connect(database()) as conn:
            cur = conn.execute(f'SELECT data FROM episodes WHERE id = ?', (id,),)
            results = cur.fetchall()

        if len(results) > 0:
            data = json.loads(results[0][0])   

        return data

    def insert_episode_list(self, season, eg, data, expire_after=14400.0):
        expires_at = round(time() + expire_after)
        id = season + '_' + eg
        with sql.connect(database()) as conn:
            conn.execute(f'INSERT OR REPLACE INTO episodes (id,expires,data) VALUES (?,?,?)', (id, expires_at, json.dumps(data),),)
            
    def get_or_download_list(self, season, eg):
        json_episodes = self.get_episode_list(season, eg)
        if not json_episodes:
            json_episodes = fetch_episode_group(season, eg)
            self.insert_episode_list(season, eg, json_episodes)
        return json_episodes

    def get_episodes(self, category):
        json_episodes = self.get_or_download(category)
            
        episodes = []

        for episode in json_episodes:
            series_id = episode['seriesId']
            series_title = episode['title']
            episodes.append({ 'name': series_title,
                              'series': series_id, 
                              'thumb': episode['thumbComponent']['urlPrefix']
                              + '/' + episode['thumbComponent']['filename']
                              + '?' + episode['thumbComponent']['query'],
                              'fanart': episode['thumbPortraitComponent']['urlPrefix']
                              + '/' + episode['thumbPortraitComponent']['filename']
                              + '?' + episode['thumbPortraitComponent']['query'],
                              'genre': category, 
                              'series_title': series_title })

        return episodes

    def get_series_episodes(self, series):
        json_episodes = self.get_or_download_series(series)
            
        episodes = []

        for episode in json_episodes:
            season_id = episode['id']
            if 'name' in episode:
                season_title = episode['name']
            else:
                season_title = ""
            episodes.append({ 'name': season_title,
                              'season': season_id,
                              'episodeGroups': episode.get('episodeGroups'),
                              'thumb': episode['thumbComponent']['urlPrefix']
                              + '/' + episode['thumbComponent']['filename']
                              + '?' + episode['thumbComponent']['query']})

        return episodes

    def get_eg_episodes(self, season, group):
        json_episodes = self.get_or_download_list(season, group)
            
        episodes = []

        for episode in json_episodes:
            if 'video' in episode:
                type = episode['video']['terms'][0]['onDemandType']
            else:
                type = episode['terms'][0]['onDemandType']
            if type == 3 :
                video_id = episode['id']
                video_title = episode['episode']['title']
                episodes.append({ 'name': video_title,
                                  'video': video_id,
                                  'desc': episode['episode']['content'],
                                  'thumb': episode['thumbComponent']['urlPrefix']
                                  + '/' + episode['thumbComponent']['filename']
                                  + '?' + episode['thumbComponent']['query']})
                
        return episodes

