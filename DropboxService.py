from Service import Service
import uuid
import requests
import json
from OAuth2_0 import OAuth2_0

class DropboxService(Service):
    def __init__(self, credentials: dict, name: str):
        GB5 = 5 * 1024 * 1024 * 1024
        super().__init__(max_storage=GB5, max_file_size=GB5, name=name)
        self.token = credentials
    
    def upload(self, parts:list):
        # Check if user is authenticated
        if not self.token:
            oauth = OAuth2_0("Dropbox", self.name)
            self.token = oauth.auth()
        
        parts_ids = []
        for part in parts:
            file_name = part[1]
            headers = {
                'Authorization': f"Bearer {self.token['access_token']}",
                'Dropbox-API-Arg': json.dumps({"path": f"/{file_name}", "mode": "add", "autorename": True}),
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(
                'https://content.dropboxapi.com/2/files/upload',
                headers=headers,
                data=part[0]
            )
            
            if response.status_code == 200:
                parts_ids.append(response.json()['id'])
            else:
                raise Exception(f"Failed to upload part: {response.text}")
        return parts_ids
        
    def download(self, parts_ids: list):
        parts = []
        for part_id in parts_ids:
            headers = {
                'Authorization': f"Bearer {self.token['access_token']}",
                'Dropbox-API-Arg': json.dumps({"path": part_id})
            }
            
            response = requests.post(
                'https://content.dropboxapi.com/2/files/download',
                headers=headers
            )
            
            if response.status_code == 200:
                # chunk_parts = []
                # for chunk in response.iter_content(chunk_size=1024):
                #     if chunk:
                #         chunk_parts.append(chunk)
                # parts.append(b''.join(chunk_parts))
                
                parts.append(response.content)
            else:
                raise Exception(f"Failed to download part: {response.text}")
        return parts