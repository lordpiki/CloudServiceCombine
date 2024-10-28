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
import time

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
    def __init__(self, service_type: str, name: str=None, service_id: str = None):
        if name:
            self.service = service_type
            self.name = name
            self.load_config()
        else:
            self.service_id = service_id
            self.load_service(service_id, service_type)
        
    
    def load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            service = config[self.service]
            self.client_id = service['client_id']
            self.redirect_uri = service['redirect_uri']
            self.scope = service['scope']
            self.auth_url = service['auth_url']
            self.token_url = service['token_url']
    
    def load_service(self, service_id: str, service_type: str):
        with open(SERVICES_PATH, 'r') as f:
            services = json.load(f)
            self.service = services[service_id]
            self.token = self.service['credentials']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            service = config[service_type]
            self.client_id = service['client_id']

    def save_to_services(self):
        services = {}
        service_id = str(uuid.uuid4())
        with open(SERVICES_PATH, 'r') as f:
            services = json.load(f)
        
        # Save service_id to credentials so we can identify the service later in case of a refresh token
        self.token['service_id'] = service_id
        with open(SERVICES_PATH, 'w') as f:
            services[service_id] = {
                'service_name': self.service,
                'credentials': self.token,
                'created_at': time.time(),
                'name': self.name
                
            } 
            json.dump(services, f)
    
    
    def check_token(self):
        if time.time() - self.service['created_at'] > self.token['expires_in']:
            self.refresh_token()
        
    def refresh_access_token(self):
        """Use the refresh token to get a new access token"""
        refresh_token = self.token['credentials']['refresh_token']
        if not refresh_token:
            raise Exception("No refresh token available. Please authenticate again.")

        data = {
            'client_id': self.client_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            new_tokens = response.json()
            self.token['access_token'] = new_tokens['access_token']
            self.token['expires_in'] = new_tokens['expires_in']
            
        else:
            raise Exception(f"Token refresh failed: {response.text}")
        
        with open(SERVICES_PATH, 'w') as f:
            services = json.load(f)
            services[self.service_id]['credentials'] = self.token
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
            print(self.token)
            return self.token
        else:
            raise Exception(f"Token exchange failed: {response.text}")
