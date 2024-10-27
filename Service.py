import uuid
import json


class Service():

    def __init__ (self, max_storage, max_file_size, service_id, name):
        self.max_storage = max_storage
        self.max_file_size = max_file_size
        self.service_id = service_id
        self.name = name
    
    
    def upload(self, files: list):
        raise NotImplementedError

    def download(self, file_id):
        raise NotImplementedError

    def get_storage_info(self):
        raise NotImplementedError

    def get_service_name(self):
        raise NotImplementedError
    
    def get_file_names():
        raise NotImplementedError
