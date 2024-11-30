# General imports
import json
import uuid
import humanize

# Specific imports
from FileHandler import FileHandler

# Service imports
from DiscordService import DiscordService
from GoogleService import GoogleService
from DropboxService import DropboxService


class FileManager():
    def __init__(self, file_config_path: str, service_config_path: str):
        self.files = {}
        self.services = {}
        self.file_config_path = file_config_path
        self.service_config_path = service_config_path
        self.load_files_from_db()
        self.load_services_from_db()
         
    def upload(self, file_paths: list[str], service_id: str):
        # Get the service object
        service = self.services[service_id]
        
        
        # For each file path, upload the file to the service
        for file_path in file_paths:
            file_id = str(uuid.uuid4())
            file_size = humanize.naturalsize(FileHandler.get_file_size(file_path))
            if "Bytes" in file_size:
                file_size = file_size.replace("Bytes", "B")
            # Break down file into parts
            parts = FileHandler.break_down_file(file_path, service.max_file_size)
            if len(parts) == 1:
                parts = [(parts[0], FileHandler.extract_name_from_path(file_path))]
            else:
                parts = [(part, str(uuid.uuid4())) for part in parts]
            # Upload the parts to the service, and get back the service provided ids for each part
            parts_ids = service.upload(parts)
            
            # Save the file info to the files dictionary
            self.files[file_id] = {
                'file_name': FileHandler.extract_name_from_path(file_path),
                'service_id': service_id,
                'uuid': file_id,
                'file_size': file_size,
                'parts_ids': parts_ids
            }
            
            self.save_files_to_db()

    def download(self, file_ids: str):
        # For each file id, get the file info and download the parts from the service
        for file_id in file_ids:
            file_info = self.files[file_id]
            service = self.services[file_info['service_id']]
            parts = service.download(file_info['parts_ids'])
            # Reassemble the parts into a file and save it to the disk
            FileHandler.reasseble_file(file_info['file_name'], parts)        
        
    def get_files(self):
        return self.files
    
    
    # DB functions
    def save_files_to_db(self):
        # save files to db
        with open(self.file_config_path, 'w') as f:
            json.dump(self.files, f)
    
    def save_services_to_db(self):
        # save services to db
        with open(self.service_config_path, 'w') as f:
            json.dump(self.services, f)

    def load_files_from_db(self):
        # load files into self.files
        with open(self.file_config_path, 'r') as f:
            self.files = json.load(f)

    def load_services_from_db(self):
        # load services into self.services
        with open(self.service_config_path, 'r') as f:
            # All currently supported services
            service_classes = {
                'Discord': DiscordService,
                'Google': GoogleService,
                'Dropbox': DropboxService
            }
            # Load services from db
            services_dict = json.load(f)
            # For each service, create the matching service object and add it to self.services
            for service_id, service in services_dict.items():
                service_class = service_classes.get(service['service_name'])
                if service_class:
                    self.services[service_id] = service_class(credentials=service['credentials'], name=service['name'])
    
    
manager = FileManager('files.json', 'services.json')
# manager.upload(['./arc.png'], '4082da61-b40d-42a4-8c96-60742c67174d')
manager.download(['bb21f81d-30a3-4aaa-b03b-debfa2f203a9'])
# manager.upload(['./arc.png'], '4082da61-b40d-42a4-8c96-60742c67174d')
# manager.upload(['./arc.png'], '03d408f4-6d82-4824-a257-cd8258a9393d')
# manager.download(['5afc706c-d53d-40c7-b120-e65e3cf41b69'])
# manager.download(["51bfef09-9d36-4574-9b57-b98e3865c088"])