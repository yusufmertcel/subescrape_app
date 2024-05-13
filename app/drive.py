from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

class Google_Drive:

    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.settings['client_config_file'] = r'client_secrets.json'
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)

    def create_folder(self, folderName):
        file_metadata = {
            'title': folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.drive.CreateFile(file_metadata)
        folder.Upload()
        return folder['id']

    def list_files(self):
        file_list = self.drive.ListFile({'q': "'Data' in parents and trashed=false"}).GetList()
        print(file_list)
        took = False
        files = list()
        for file1 in file_list:
            print('title: %s, id: %s' % (file1['title'], file1['id']))
            files.append((file1['title'], file1['id']))

        return files

    def upload_file(self, fileName, folderId):
        with open(fileName,"r") as file:
            file_drive = self.drive.CreateFile({'title':os.path.basename(file.name),
                                            'parents': [{'id': folderId}]})
            file_drive.SetContentString(file.read()) 
            file_drive.Upload()

    def read_file(self, fileName, folderId):
        fileList = self.list_files()
        metadata = dict( id = folderId )
    
        google_file = self.drive.CreateFile( metadata = metadata )

        google_file.GetContentFile( filename = fileList[0]['id'] )

        content_bytes = google_file.content ; # BytesIO

        string_data = content_bytes.read().decode( 'utf-8' )

        return string_data


if __name__ == "__main__":
    os.chdir("app/")
    dr = Google_Drive()
    folder_id = dr.create_folder("Data")
    dr.upload_file("garenta_sube.json", folder_id)