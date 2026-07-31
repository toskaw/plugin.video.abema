from lib import Cache, create_tables
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote, urlparse
import requests
import re
from lib.yt_dlp import YoutubeDL
from lib.yt_dlp.extractor.abematv import AbemaTVIE, AbemaLicenseRH
import xbmc
import xbmcaddon
import time
import simplejson as json

PREFIX = '/video.abema'
LIVE =   '/live.abema'
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_license(self, ticket):
        Ydl = YoutubeDL()
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
                res = requests.get(url)
                body = re.sub(b'URI=.*?://', b'URI=\"/live.abema/key/', res.content)
                body = re.sub(b'^#EXT-X-DISCONTINUITY.*$', b'', body, flags=re.MULTILINE)

                self.send_response(res.status_code)
                self.send_header('content-type', res.headers['content-type'])
                self.end_headers()
                self.wfile.write(body)
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
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                self.end_headers()

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
        server_inst = TCPServer((address, port), SimpleHTTPRequestHandler)
    except Exception:
        xbmc.executebuiltin('Quit')
        
    # The follow line is only for test purpose, you have to implement a way to stop the http service!
    #server_inst.serve_forever()
    import threading
    xbmc.log("server start",xbmc.LOGINFO)
    server_thread = threading.Thread(target=server_inst.serve_forever)  # 要求によりスレッドを生成するメソッドをtargetに指定。
    server_thread.daemon = True  # デーモンスレッドにするとメインスレッドが終わるとPythonプログラムが終了してしまう。
    server_thread.start()  # スレッドの受付を開始。

    monitor = xbmc.Monitor()
    
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            server_inst.shutdown()
            break
        
