class Service():

    def login(self):
        raise NotImplementedError
    
    def upload(self, file_path):
        raise NotImplementedError

    def download(self, file_id):
        raise NotImplementedError

    def get_storage_info(self):
        raise NotImplementedError

    def get_service_name(self):
        raise NotImplementedError
    
    def get_file_names():
        raise NotImplementedError
