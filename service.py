from lib import Cache, create_tables
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote, urlparse
import requests
import re
from yt_dlp import YoutubeDL
from yt_dlp.extractor.abematv import AbemaTVIE, AbemaLicenseRH
import xbmc
import xbmcaddon
import time
import simplejson as json
from resources.lib.skiptro import main
import datetime
import html

PREFIX = '/video.abema'
LIVE =   '/live.abema'
PLAYLIST = '/playlist/'
Ydl = YoutubeDL()
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_license(self, ticket):
        Abema = Ydl.get_info_extractor("AbemaTVTitle")        
        lh = AbemaLicenseRH(ie=Abema, logger=None)
        license_data = lh._get_videokey_from_ticket(ticket)
        self.send_response(200)
        self.send_header('content-type', 'binary/octet-stream')
        self.send_header('Content-length', len(license_data))
        self.end_headers()
        self.wfile.write(license_data)

    def do_GET(self):
        path = self.path  # Path with parameters received from request e.g. "/manifest?id=234324"
        xbmc.log('HTTP GET Request received to {}'.format(path),xbmc.LOGINFO)
        if path[0:len(PREFIX)] != PREFIX and path[0:len(LIVE)] != LIVE and path[0:len(PLAYLIST)] != PLAYLIST:
            orig = xbmcaddon.Addon().getSetting(id='orig')
            if orig :
                url = 'https://'+ orig + path
                xbmc.log('redirect url= {}'.format(url),xbmc.LOGINFO)
                #res = requests.get(url)
                #body = res.content
                self.send_response(301)
                self.send_header('Location', url)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
            return
        elif path[0:len(LIVE)] == LIVE:
            try:
                if '/key/' in path:
                    ticket = path[len(LIVE)+len('/key/'):]
                    return self.get_license(ticket)
                url = 'https:/' + path[len(LIVE):]
                orig = urlparse(url).netloc
                xbmcaddon.Addon().setSetting(id='orig', value=orig)
                xbmc.log('HTTP GET url= {}'.format(url),xbmc.LOGINFO)
                ignore = xbmcaddon.Addon().getSettingBool(id='ignore_discont')
                res = requests.get(url)
                body = re.sub(b'URI=.*?://', b'URI=\"/live.abema/key/', res.content)
                if ignore:
                    body = re.sub(b'^#EXT-X-DISCONTINUITY.*$', b'', body, flags=re.MULTILINE)
                self.send_response(res.status_code)
                self.send_header('content-type', res.headers['content-type'])
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                self.end_headers()
        elif path[0:len(PLAYLIST)] == PLAYLIST:
            self.makePlaylist(path)
        else:
            try:
                if '/key/' in path:
                    ticket = path[len(PREFIX)+len('/key/'):]
                    return self.get_license(ticket)
                url = 'https:/' + path[len(PREFIX):]
                orig = urlparse(url).netloc
                xbmcaddon.Addon().setSetting(id='orig', value=orig)
                xbmc.log('HTTP GET url= {}'.format(url),xbmc.LOGINFO)
                res = requests.get(url)
                body = re.sub(b'URI=.*?://', b'URI=\"/video.abema/key/', res.content)
                self.send_response(res.status_code)
                self.send_header('content-type', res.headers['content-type'])
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                self.end_headers()

    def do_HEAD(self):
        path = self.path  # Path with parameters received from request e.g. "/manifest?id=234324"
        xbmc.log('HTTP GET Request received to {}'.format(path),xbmc.LOGINFO)
        if path[0:len(PREFIX)] != PREFIX and path[0:len(LIVE)] != LIVE:
            orig = xbmcaddon.Addon().getSetting(id='orig')
            if orig :
                url = 'https://'+ orig + path
                xbmc.log('redirect url= {}'.format(url),xbmc.LOGINFO)
                #res = requests.get(url)
                #body = res.content
                self.send_response(301)
                self.send_header('Location', url)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
            return
        elif path[0:len(LIVE)] == LIVE:
            try:
                if '/key/' in path:
                    ticket = path[len(LIVE)+len('/key/'):]
                    return self.get_license(ticket)
                url = 'https:/' + path[len(LIVE):]
                orig = urlparse(url).netloc
                xbmcaddon.Addon().setSetting(id='orig', value=orig)
                xbmc.log('HTTP GET url= {}'.format(url),xbmc.LOGINFO)
                ignore = xbmcaddon.Addon().getSettingBool(id='ignore_discont')
                res = requests.get(url)
                body = re.sub(b'URI=.*?://', b'URI=\"/live.abema/key/', res.content)
                if ignore:
                    body = re.sub(b'^#EXT-X-DISCONTINUITY.*$', b'', body, flags=re.MULTILINE)


                self.send_response(res.status_code)
                self.send_header('content-type', res.headers['content-type'])
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.end_headers()
        else:
            try:
                if '/key/' in path:
                    ticket = path[len(PREFIX)+len('/key/'):]
                    return self.get_license(ticket)
                url = 'https:/' + path[len(PREFIX):]
                orig = urlparse(url).netloc
                xbmcaddon.Addon().setSetting(id='orig', value=orig)
                xbmc.log('HTTP GET url= {}'.format(url),xbmc.LOGINFO)
                res = requests.get(url)
                body = re.sub(b'URI=.*?://', b'URI=\"/video.abema/key/', res.content)
                self.send_response(res.status_code)
                self.send_header('content-type', res.headers['content-type'])
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.end_headers()

    def makePlaylist(self, path):
        file = path[len(PLAYLIST):]
        if '.m3u' in file:
            #playlist
            xbmc.log('HTTP GET playlist', xbmc.LOGINFO)
            body = self.getPlaylist()
        else:
            #epg
            xbmc.log('HTTP GET epg', xbmc.LOGINFO)
            body = self.getEPG()
        
        self.send_response(200)
        self.end_headers()
        data = bytes(body, encoding='utf-8')
        self.wfile.write(data)
    
    def getPlaylist(self):
        Abema = Ydl.get_info_extractor("AbemaTVTitle")
        timetable = Abema._call_api(
            'v1/timetable/dataSet', '', {'debug': 'false'})
        body = '#EXTM3U url-tvg="http://127.0.0.1:51041/playlist/abema.xml" refresh="3600"\n\n'
        channels = timetable['channels']
        for channel in channels:
            id = channel['id']
            title = channel['name']
            body += f'#EXTINF:-1  tvg-id="{id}" tvg-logo="https://image.p-c2-x.abema-tv.com/image/channels/{id}/logo.png", {title}\n'
            body += f'http://127.0.0.1:51041/live.abema/ds-linear-abematv.akamaized.net/channel/{id}/playlist.m3u8\n\n'

        return body
    
    def getEPG(self):
        Abema = Ydl.get_info_extractor("AbemaTVTitle")
        timetable = Abema._call_api(
            'v1/timetable/dataSet', '', {'debug': 'false'})
        body = "<?xml version='1.0' encoding='UTF-8'?>\n<tv>\n"
        channels = timetable['channels']
        slots = timetable['slots']
        for channel in channels:
            id = channel['id']
            title = channel['name']
            body += f'<channel id="{id}">\n<display-name>{title}</display-name>\n<icon src="https://image.p-c2-x.abema-tv.com/image/channels/{id}/logo.png" />\n</channel>\n'
        for slot in slots:
            channel = slot['channelId']
            start = self.timestr(slot['startAt'])
            end = self.timestr(slot['endAt'])
            title = html.escape(slot['title'])
            desc = html.escape(slot['content'])
            icon = slot['displayProgramId']
            body += f'<programme channel="{channel}" start="{start}" stop="{end}">\n<title>{title}</title>\n<desc>{desc}</desc>\n<icon src="https://image.p-c2-x.abema-tv.com/image/programs/{icon}/thumb001.png" />\n</programme>\n'
        body += '</tv>'
        return body

    def timestr(self, utime):
        dt = datetime.datetime.fromtimestamp(utime, datetime.timezone.utc)
        return dt.strftime('%Y%m%d%H%M%S +0000')

def sendJSON(method, json_params = {}):

    #This the generated JSON-RPC query code
    params = json.dumps({"jsonrpc":"2.0",
                         "method": method,
                         "params": json_params,
                         "id":0})

    #Response data is a binary string and I want to read it easily
    responseObject = xbmc.executeJSONRPC(params)

    return json.loads(responseObject).get("result")
            
if __name__ == '__main__':
    #initialize DB
    create_tables()
    
    # cache warming
    cache = Cache()
    cache.delete_expired()

    try:    
        address = '127.0.0.1'  # Localhost
        # The port in this example is fixed, DO NOT USE A FIXED PORT!
        # Other add-ons, or operating system functionality, or other software may use the same port!
        # You have to implement a way to get a random free port
        port = 51041
        server_inst = TCPServer((address, port), SimpleHTTPRequestHandler, bind_and_activate=False)
        server_inst.allow_reuse_address = True
        server_inst.server_bind()
        server_inst.server_activate()
    except Exception:
        #xbmc.executebuiltin('Quit')
        raise
        
    # The follow line is only for test purpose, you have to implement a way to stop the http service!
    #server_inst.serve_forever()
    import threading
    xbmc.log("server start",xbmc.LOGINFO)
    server_thread = threading.Thread(target=server_inst.serve_forever)  # 要求によりスレッドを生成するメソッドをtargetに指定。
    server_thread.daemon = True  # デーモンスレッドにするとメインスレッドが終わるとPythonプログラムが終了してしまう。
    server_thread.start()  # スレッドの受付を開始。

    #monitor = xbmc.Monitor()
    main()
    
    #while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        #if monitor.waitForAbort(10):
    # Abort was requested while waiting. We should exit
    server_inst.shutdown()
    server_inst.server_close()  # ソケットを閉じる
    server_thread.join()  # スレッドの終了を待つ

        
    xbmc.log("server stop",xbmc.LOGINFO)
