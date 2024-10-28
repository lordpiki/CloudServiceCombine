from Service import Service
import uuid
import requests
import json
from OAuth2_0 import OAuth2_0

class GoogleService(Service):
    def __init__(self, credentials: dict, name: str):
        GB15 = 15 * 1024 * 1024 * 1024
        super().__init__(max_storage=GB15, max_file_size=GB15)
        self.name = name
        self.token = credentials
        
    def upload(self, parts: list):
        # Check if user is authenticated
        if not self.token:
            oauth = OAuth2_0("Google", self.name)
            self.token = oauth.auth()
        
        mime_type = 'application/octet-stream'
        
        parts_ids = []
        for part in parts:
            
            metadata = {
                'name': str(uuid.uuid4()),
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
    
service = GoogleService(credentials=None, name='Google1')
service.upload([b'Hello', b'World'])