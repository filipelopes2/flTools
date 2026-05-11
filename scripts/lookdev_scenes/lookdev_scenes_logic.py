import os
import maya.cmds as cmds
import maya.utils

from startup.ui_functions import UiFunctions


class LookDevScenesLogic:

    def __init__(self):
        self.new_nodes = None

    def import_file(self, path=None, textures_folder=None, newscene=False):
        """
        Import selected Maya scenes from resource folder, copy used textures to the current project, and relink them.
        """
        cmds.file(f=True, new=newscene)
        self.new_nodes = cmds.file(path, i=True, returnNewNodes=True)
        self._link_new_textures(textures_folder=textures_folder)

        # wait until Maya finish all import process
        for i in range(10000):
            if maya.utils.processIdleEvents():
                break

        if newscene:
            message = 'LookDev scene imported to new file'
        else:
            message = 'LookDev scene imported to existing file'

        cmds.confirmDialog(title='LookDev', message=message)

    def _link_new_textures(self, textures_folder=None):
        """
        For each texture file node, copy texture from resource to the current project folder and relink them.
        """
        textures_folder = os.path.join(textures_folder, 'LookDev_Scenes')
        file_nodes = [n for n in self.new_nodes if cmds.nodeType(n) == 'file']
        wrong_file_nodes = []

        for node in file_nodes:
            tex_original_path = cmds.getAttr(node + '.fileTextureName')
            filename = os.path.basename(tex_original_path)

            if not os.path.exists(tex_original_path):
                wrong_file_nodes.append(node)
            else:
                tex_project_path = os.path.join(textures_folder, filename).replace('/', '\\')
                UiFunctions.create_dir(tex_project_path)
                UiFunctions.copy_file(tex_original_path, tex_project_path)
                cmds.setAttr(node + '.fileTextureName', tex_project_path, type='string')

        if wrong_file_nodes:
            print(' _link_new_textures '.center(100, '—'))
            print('wrong_file_nodes = ')
            for file_node in wrong_file_nodes:
                print(file_node)
            print(''.center(100, '—'))
            cmds.confirmDialog(title='Create Lookdev Scene',
                               message="There are file nodes without valid files.\nPlease, contact the R&D team.",
                               button=['Ok'],
                               icon='warning')