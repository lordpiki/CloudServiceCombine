import uuid
import json


class Service():

    def __init__ (self, name: str, max_storage: int=None, max_file_size: int=None, credentials:dict=None):
        self.max_storage = max_storage
        self.max_file_size = max_file_size
        self.name = name
    
    def upload(self, parts: list) -> list[str]:
        raise NotImplementedError

    def download(self, parts_ids: list[str]) -> list:
        raise NotImplementedError

    def get_storage_info(self):
        raise NotImplementedError

    def get_service_name(self) -> str:
        raise NotImplementedError
    