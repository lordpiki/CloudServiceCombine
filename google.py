import base64
import hashlib
import json
import os
import secrets
import requests
from urllib.parse import urlencode
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

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

class GoogleDriveUploader:
    def __init__(self, client_id):
        self.client_id = client_id
        self.redirect_uri = 'http://127.0.0.1:8080'  # Changed to 127.0.0.1
        self.token = None
        
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
    
    def upload_file(self, file_path, mime_type=None):
        """Upload a file to Google Drive"""
        if not self.token:
            raise Exception("No valid token. Please authenticate first.")
            
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        file_name = os.path.basename(file_path)
        
        metadata = {
            'name': file_name,
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
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
            
        headers = {
            'Content-Length': str(len(file_data))
        }
        
        response = requests.put(upload_url, data=file_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"File upload failed: {response.text}")

def main():
    # Your Desktop application client ID
    CLIENT_ID = '1094592796250-5l2fg4g55t865kcgefhm61450arumsn2.apps.googleusercontent.com'
    
    # Initialize uploader
    uploader = GoogleDriveUploader(CLIENT_ID)
    
    # Get authorization URL and start local server
    auth_url = uploader.get_authorization_url()
    server, server_thread = uploader.get_auth_code()
    
    # Open browser for authorization
    print("Opening browser for authorization...")
    webbrowser.open(auth_url)
    
    # Wait for the authorization code
    while OAuthCallbackHandler.auth_code is None:
        pass
    
    # Exchange authorization code for tokens
    tokens = uploader.get_tokens(OAuthCallbackHandler.auth_code)
    print("Successfully obtained access token")
    
    # Upload a file
    file_path = "arc.png"
    result = uploader.upload_file(file_path)
    print(f"File uploaded successfully. File ID: {result['id']}")
    
    # Download the file back
    def download_file(file_id, destination_path):
        """Download a file from Google Drive"""
        if not uploader.token:
            raise Exception("No valid token. Please authenticate first.")
        
        headers = {
            'Authorization': f'Bearer {uploader.token["access_token"]}'
        }
        
        response = requests.get(
            f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media',
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            with open(destination_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully to {destination_path}")
        else:
            raise Exception(f"File download failed: {response.text}")

    # Example usage
    file_id = result['id']
    destination_path = "downloaded_arc.png"
    download_file(file_id, destination_path)

if __name__ == "__main__":
    main() 