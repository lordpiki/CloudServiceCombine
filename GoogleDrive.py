from Service import Service
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

class GoogleDrive():

    def upload(self, file_path):
        creds, _ = google.auth.default()
        try:
            # create drive api client
            service = build("drive", "v3", credentials=creds)

            file_metadata = {"name": file_path}
            media = MediaFileUpload(file_path, mimetype="image/png")
            # pylint: disable=maybe-no-member
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f'File ID: {file.get("id")}')

        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None

        return file.get("id")

    def download(self, file_id):
        pass

    def get_storage_info(self):
        pass
    
    def get_service_name(self):
        return self.__class__.__name__
    
    def get_file_names():
        pass
    
if __name__ == "__main__":
    gd = GoogleDrive()
    gd.upload("test.jpeg")
    print(gd.get_service_name())