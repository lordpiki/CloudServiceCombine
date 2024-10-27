import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        OAuthCallbackHandler.auth_code = query_components.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authorization successful! You can close this window.")
        
        threading.Thread(target=self.server.shutdown).start()