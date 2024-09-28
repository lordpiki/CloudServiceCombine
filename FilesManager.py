import json
import uuid
from DiscordService import DiscordService
import time

class FilesManager:
    def __init__(self, json_file_path):
        self.fp = json_file_path
        self.tasks = {}
        
    def add_file(self, file_path, service="discord"):
        file_id = str(uuid.uuid4())
        file_name = file_path.split('/')[-1]
        self.tasks[service].append({'type': 'upload', 'file_path': file_path, 'file_id': file_id})
        
    
    def upload_all_files(self):
        active_threads = []
        
        for service in self.tasks:
            if service == 'discord':
                ds = DiscordService(self.tasks[service])
                active_threads.append(ds.thread)
                
            
        for thread in active_threads:
            thread.join()    
    
    
    def remove_file(self, file_id):
        pass
    
    def download_file(self, file_id):
        pass
    
    def get_files(self, sorted_by=None): 
        if sorted_by == 'name':
            pass
        elif sorted_by == 'size':
            pass
        elif sorted_by == 'date':
            pass
        elif sorted_by == 'service':
            pass
        elif sorted_by == 'type':
            pass
        else:
            pass
        
if __name__ == '__main__':
    fm = FilesManager('files.json')
    fm.add_file('test.png')
    fm.get_files()