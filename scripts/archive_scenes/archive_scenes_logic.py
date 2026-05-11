import os
import shutil
import maya.cmds as cmds
import maya.app.general.zipScene


class ArchiveScenesLogic:

    def __init__(self):
        self.export_folder = None

    def bulk_archive(self, file_list=None) -> None:
        for file in file_list:
            cmds.file(newFile=True, force=True)
            file_path = cmds.file(file, open=True, prompt=False, ignoreVersion=True, force=True)
            self.archive_scene()
            self.move_zip(file_path)

        cmds.file(newFile=True, force=True)

    def archive_scene(self) -> None:
        maya.app.general.zipScene.zipScene(0)

    def move_zip(self, from_path=None) -> None:
        print('\n')
        print(' Moving zip file '.center(100, '-'))
        zip_path = f'{from_path}.zip'
        file_name = '_'.join(zip_path.split('/')[-2:])
        to_path = os.path.join(self.export_folder, file_name)

        try:
            print(f'zip_path = {zip_path}')
            print(f'to_path = {to_path}')
            shutil.move(zip_path, to_path)
        except Exception as e:
            print('Error while moving zip file')
            print(e)