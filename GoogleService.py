from Service import Service
import uuid
import requests
import json


class GoogleService(Service):
    def __init__(self, credentials: dict, name: str):
        GB15 = 15 * 1024 * 1024 * 1024
        super().__init__(max_storage=GB15, max_file_size=GB15, name=name)
        self.client_id = credentials['client_id']
        self.redirect_uri = credentials['redirect_uri']
        self.token = credentials['token']
        
    def upload(self, parts: list):
        # Check if user is authenticated
        if not self.token:
            self.authenticate()
        
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        parts_ids = []
        for part in parts:
            
            metadata = {
                'name': uuid.uuid4(),
                'mimeType': mime_type
            }
            
            headers = {
                'Authorization': f'Bearer {self.token["access_token"]}',
                'Content-Type': 'application/json; charset=UTF-8'
            }
            
            response = requests.post(
                'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable',
                headers=headers,
                data=json.dumps(metadata)
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to initiate upload: {response.text}")

            upload_url = response.headers['Location']
            
            headers = {
                        'Content-Length': str(len(part))
                    }
            
            response = requests.put(upload_url, data=part, headers=headers)
            
            if response.status_code == 200:
                parts_ids.append(response.json()['id'])
            else:
                raise Exception(f"Failed to upload part: {response.text}")
    
    def download(self, parts_ids: list):
        parts = []
        for part_id in parts_ids:
            headers = {
                'Authorization': f'Bearer {self.token["access_token"]}'
            }
            
            response = requests.get(
                f'https://www.googleapis.com/drive/v3/files/{part_id}?alt=media',
                headers=headers
            )
            
            if response.status_code == 200:
                # chunk_parts = []
                # for chunk in response.iter_content(1024):
                    # chunk_parts.append(chunk)
                # parts.append(b''.join(chunk_parts))
                
                parts.append(response.content)
            else:
                raise Exception(f"Failed to download part: {response.text}")
        
        return parts
    
    def authenticate(self):
        # Importing here because this function is only called once, so to avoid memory usage we import here
        import secrets
        import base64
        import hashlib
        from urllib.parse import urlencode
        import webbrowser
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from OAuthCallbackHandler import OAuthCallbackHandler

        def generate_pkce_pair(self):

            
            """Generate PKCE code verifier and challenge"""
            code_verifier = secrets.token_urlsafe(64)
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip('=')
            
            return code_verifier, code_challenge
        
        def get_authorization_url(self):
            """Generate authorization URL with PKCE"""
            self.code_verifier, code_challenge = self.generate_pkce_pair()
            
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': 'https://www.googleapis.com/auth/drive.file',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            return 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
        
        def get_auth_code(self):
            """Start local server to receive authorization code"""
            server = HTTPServer(('127.0.0.1', 8080), OAuthCallbackHandler)  # Changed to 127.0.0.1
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return server, server_thread  
        
        def get_tokens(self, auth_code):
            
            """Exchange authorization code for tokens"""
            token_url = 'https://oauth2.googleapis.com/token'
            
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
            
        