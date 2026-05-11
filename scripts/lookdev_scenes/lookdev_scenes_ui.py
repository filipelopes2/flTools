import os
import maya.cmds as cmds
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from lookdev_scenes.lookdev_scenes_logic import LookDevScenesLogic
from startup.ui_functions import UiFunctions


__tool_name__ = 'LookDev Scenes'
__tool_class__ = 'OpenLookDevScenes'
__tool_function__ = 'open_ui'
__tool_submenu__ = 'Look and Render'


class LookDevUI(QWidget):
    """
    Creates button for the interface
    """
    def __init__(self, plugin=None):
        super(LookDevUI, self).__init__()
        self.plugin = plugin

    def open_window(self):
        if UiFunctions.check_plugin(self.plugin):
            selection_ui = SelectionUI()
            selection_ui.plugin = self.plugin
            selection_ui._start()


class SelectionUI(QDialog):
    """
    builds and populates a UI that holds a list
    of possible scenes to import
    """
    def __init__(self, parent=None):
        super(SelectionUI, self).__init__(parent)
        self.plugin = None
        self.resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__ + '/../../')), 'resources')
        self.scenes_folder = os.path.join(self.resource_path, 'scenes')

    def _start(self) -> None:
        self.LookDevSceneLogic = LookDevScenesLogic()
        UiFunctions.create_window(self, __tool_name__, 800, 500)
        self.draw_ui()
        self._populate()
        self.show()

    def draw_ui(self):

        # layouts
        layout = QVBoxLayout(self)  # vertical

        # frames
        description_frame = QFrame()
        description_frame.setFrameShape(QFrame.StyledPanel)
        description_frame.setFrameShadow(QFrame.Plain)
        description_frame.setFixedHeight(120)
        description_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # objects
        textures_folder = UiFunctions.label('textures folder: ', width=120, height=35, h_align=Qt.AlignRight)
        self.textures_folder_text = UiFunctions.text_field('txt_textures_folder', 600)
        self.textures_folder_text.setDisabled(True)
        textures_folder_button = UiFunctions.button('...', 40, 35, self.folder_button_clicked)
        empty_widget, horizontal_layout = UiFunctions.horizontal_line(30)
        UiFunctions.add_widgets(horizontal_layout, [textures_folder, self.textures_folder_text,
                                                    textures_folder_button, UiFunctions.spacer(20)])


        # Size of the items of the list grid
        size = 240
        buffer = 24

        self.list_widget = QListWidget(parent=self)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.list_widget.setIconSize(QSize(size, size))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setGridSize(QSize(size + buffer, size + buffer))
        self.list_widget.itemClicked.connect(self.item_clicked)

        # adding to layouts
        template_widget = QWidget()
        main_layout = QVBoxLayout(template_widget)
        layout.addWidget(template_widget)
        main_layout.addWidget(empty_widget)
        main_layout.addWidget(self.list_widget)

    def item_clicked(self) -> None:
        if self._verification():
            self.load_scene()

    def _verification(self) -> bool:
        textures_folder = self.textures_folder_text.text()
        if textures_folder == '':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select a folder to copy textures!')
            return False

        if not os.path.exists(textures_folder):
            UiFunctions.error_message(title=__tool_name__,
                                      message='Textures folder does not exist!')
            return False
        return True

    def folder_button_clicked(self):
        selected_folder = str(QFileDialog.getExistingDirectory(self, 'Select Folder'))
        self.textures_folder_text.setText(selected_folder)

    def load_scene(self):
        """
        Function that is called when an item is clicked is pressed
        """
        result = cmds.confirmDialog(title=__tool_name__, message='Import into current scene?',
                                    button=['New', 'Current'], defaultButton='New', cancelButton='Current',
                                    dismissString='No')
        selected = self.list_widget.currentItem().text()
        file_path = os.path.join(self.scenes_folder, f'{selected}.ma')

        if result == 'New':
            self.LookDevSceneLogic.import_file(path=file_path, textures_folder=self.textures_folder_text.text(),
                                               newscene=True)
        elif result == 'Current':
            self.LookDevSceneLogic.import_file(path=file_path, textures_folder=self.textures_folder_text.text())
        else:
            return

        self.deleteLater()

    def _populate(self):
        """
        Populates the list grid with smaller version of the imgs (thumbs)
        """
        self.list_widget.clear()
        imgs = os.listdir(self.scenes_folder)

        # Get only files with 'thumb' and plugin name
        for img in imgs:
            if ('thumb' in img) and (self.plugin in img):
                item = QListWidgetItem(img[:img.find('-')])
                self.list_widget.addItem(item)
                icon = QIcon(os.path.join(self.scenes_folder, img))
                item.setIcon(icon)


class OpenLookDevScenes:

    def __init__(self):
        pass

    def open_ui(self):
        LookDevUI('arnold').open_window()