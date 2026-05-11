import os
from datetime import datetime
import tempfile
import subprocess


class ZipRenderLogic:

    def __init__(self):
        self.archive_folder = None
        self.base_folder = None
        self.folder_list = None
        self.temp_path = tempfile.gettempdir()
        self.path_zip_program = 'C:\\Program Files\\7-Zip\\7z.exe'

    def zip_files(self) -> bool:
        list_filepath = self.write_list()
        if not self.check_zip_program():
            return False
        elif not list_filepath:
            return False
        else:
            zip_filename = f'render_{datetime.today().strftime("%Y-%m-%d_%Hh%Mm%Ss")}.zip'
            fullpath = os.path.join(self.archive_folder, zip_filename).replace('/','\\')
            cmd_line = f'"{self.path_zip_program}" a {fullpath} -spf2 @{list_filepath}'
            process = subprocess.Popen(cmd_line, cwd=self.base_folder, stdout=subprocess.PIPE, shell=True,
                                       stderr=subprocess.PIPE)
            process._internal_poll(_deadstate='dead')  # mandatory, or else the poll() will be always None
            process.wait()
            process.stdout.close()
            return True

    def check_zip_program(self) -> bool:
        if not os.path.exists(self.path_zip_program):
            print('zip program not exist')
            return False
        else:
            return True

    def write_list(self) -> bool:
        ziplist_filename = f'ziplist_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        ziplist_path = os.path.join(self.temp_path, ziplist_filename)
        ziplist_text = '\n'.join(self.folder_list)
        try:
            with open(ziplist_path, 'w') as f:
                f.write(ziplist_text)
            return ziplist_path
        except Exception as e:
            print(' Error while writing zip list file '.center(100, '—'))
            print(e)
            print(''.center(100, '—'))
            return False
