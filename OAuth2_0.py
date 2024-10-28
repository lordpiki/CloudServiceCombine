import secrets
import base64
import hashlib
from urllib.parse import urlencode
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import threading
from urllib.parse import urlparse, parse_qs
import uuid
import json

CONFIG_PATH = 'auth_config.json'
SERVICES_PATH = 'services.json'

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

class OAuth2_0:
    def __init__(self, service: str, name: str):
        self.service = service
        self.name = name
        self.load_config()
        pass
    
    def load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            service = config[self.service]
            self.client_id = service['client_id']
            self.redirect_uri = service['redirect_uri']
            self.scope = service['scope']
            self.auth_url = service['auth_url']
            self.token_url = service['token_url']
    
    def save_to_services(self):
        services = {}
        with open(SERVICES_PATH, 'r') as f:
            services = json.load(f)
        
        with open(SERVICES_PATH, 'w') as f:
            services[str(uuid.uuid4())] = {
                'service_name': self.service,
                'credentials': self.token,
                'name': self.name
            } 
            json.dump(services, f)
 
    def auth(self):
        # Get authorization URL and start local server
        auth_url = self.get_authorization_url()
        server, server_thread = self.get_auth_code()
        
        # Open browser for authorization
        print("Opening browser for authorization...")
        webbrowser.open(auth_url)
        
        # Wait for the authorization code
        while OAuthCallbackHandler.auth_code is None:
            pass
        
        self.token = self.get_tokens(OAuthCallbackHandler.auth_code)
        self.save_to_services()
        return self.token

    @staticmethod
    def generate_pkce_pair():
        """Generate PKCE code verifier and challenge"""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')

        return code_verifier, code_challenge
        
    def get_authorization_url(self):
        """Generate authorization URL with PKCE"""
        self.code_verifier, code_challenge = OAuth2_0.generate_pkce_pair()
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scope,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return self.auth_url + urlencode(params)
        
    def get_auth_code(self):
        """Start local server to receive authorization code"""
        server = HTTPServer(('127.0.0.1', 8080), OAuthCallbackHandler)  # Changed to 127.0.0.1
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return server, server_thread  
    
    def get_tokens(self, auth_code):
        
        """Exchange authorization code for tokens"""
        token_url = self.token_url
        
        data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code': auth_code,
            'code_verifier': self.code_verifier,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            self.token = response.json()
            return self.token
        else:
            raise Exception(f"Token exchange failed: {response.text}")
        