import json
from FileHandler import FileHandler
import uuid

class FileManager():
    def __init__(self, file_config_path, service_config_path):
        self.files = {}
        self.services = {}
        self.load_files_from_db(file_config_path)
        self.load_services_from_db(service_config_path)
        

    def load_files_from_db(self, config_location: str):
        # load files into self.files
        with open(config_location, 'r') as f:
            self.files = json.load(f)

    def load_services_from_db(self, config_location: str):
        # load services into self.services
        with open(config_location, 'r') as f:
            self.services = json.load(f)
         
    def upload(self, file_paths: list[str], service_id: str):
        # upload files to service
        service = self.services[service_id]
        for file_path in file_paths:
            file_id = str(uuid.uuid4())
            parts = FileHandler.break_down_file(file_path, service.max_file_size)
            self.files[file_id] = {
                'service_id': service_id,
                'parts': parts
            }
        
        pass

    def download(self, file_id: str):
        # download file from service
        pass
    
    def get_files(self):
        return self.files
    
    def save_files_to_db(self, config_location: str):
        # save files to db
        with open(config_location, 'w') as f:
            json.dump(self.files, f)
    
    def save_services_to_db(self, config_location: str):
        # save services to db
        with open(config_location, 'w') as f:
            json.dump(self.services, f)

    
    