from Service import Service
import uuid
import requests
import json
from OAuth2_0 import OAuth2_0

class GoogleService(Service):
    def __init__(self, credentials: dict, name: str):
        GB15 = 15 * 1024 * 1024 * 1024
        super().__init__(max_storage=GB15, max_file_size=GB15, name=name)
        self.token = credentials
        
    def upload(self, parts: list):
        # Check if user is authenticated
        oauth = OAuth2_0(service_type='Google', name=None, service_id=self.token['service_id'], )
        oauth.check_token()
        
        mime_type = 'application/octet-stream'
        
        parts_ids = []
        for part in parts:
            
            metadata = {
                'name': part[1],
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
            
            response = requests.put(upload_url, data=part[0], headers=headers)
            
            if response.status_code == 200:
                parts_ids.append(response.json()['id'])
                return parts_ids
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
