import os
from functools import partial

import maya.cmds as cmds
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from archive_scenes.archive_scenes_logic import ArchiveScenesLogic
from startup.ui_functions import UiFunctions


__tool_name__ = 'Archive Scenes'
__tool_class__ = 'ArchiveScenesUi'
__tool_function__ = 'open_ui'
__tool_submenu__ = 'Archive'


class FilesList(QListWidget):
    def __init__(self, parent=None, start_dir=None):
        super(FilesList, self).__init__(parent=parent)
        self.start_dir = start_dir
        self.maya_files
        self.show()

    def maya_files(self):
        def iterate(current_dir):
            if current_dir == '':
                return

            for item in os.listdir(current_dir):
                path = os.path.join(current_dir, item)
                if '.mayaSwatches' in path:
                    continue

                if os.path.isdir(path):
                    filenames = os.listdir(path)
                    if filenames:
                        files_list = list(filter(lambda filename: filename.endswith('.ma') 
                                                 or filename.endswith('.mb'), filenames))
                        fullpath_files = [os.path.join(path, filename).replace('\\', '/')
                                          for filename in files_list]
                        self.addItems(fullpath_files)
                    iterate(path)

        iterate(self.start_dir)


class Dialog(QDialog):

    started = Signal()
    finished = Signal()

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.base_path = cmds.workspace(q=True, rd=True)
        self.root_folder_text = None
        self.save_folder_text = None
        self.list_widget  = None
        self.selected_label = None

        UiFunctions.create_window(self, __tool_name__, 800, 1200)

        # generating zip message
        self._message_box = QMessageBox()
        self._message_box.setText(str('Generating zip files... Please Wait...'))
        self._message_box.setStandardButtons(QMessageBox.NoButton)
        self.started.connect(self._message_box.show)
        self.finished.connect(self._message_box.accept)

        self.draw_ui()
        self.show()

    def draw_ui(self) -> None:
        # layouts
        main_layout = QVBoxLayout(self)
        folder_layout = QVBoxLayout(self)
        selected_layout = QHBoxLayout(self)
        buttons_layout = QHBoxLayout(self)

        # frames
        folder_frame = QFrame()
        folder_frame.setFrameShape(QFrame.StyledPanel)
        folder_frame.setFrameShadow(QFrame.Plain)
        folder_frame.setFixedHeight(120)
        folder_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        selected_frame = QFrame()
        selected_frame.setFrameShape(QFrame.StyledPanel)
        selected_frame.setFrameShadow(QFrame.Plain)
        selected_frame.setFixedHeight(40)
        selected_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        buttons_frame = QFrame()
        buttons_frame.setFrameShape(QFrame.StyledPanel)
        buttons_frame.setFrameShadow(QFrame.Plain)
        buttons_frame.setFixedHeight(80)
        buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # objects
        root_folder_label = UiFunctions.label('root folder: ', width=100, height=35, h_align=Qt.AlignRight)
        self.root_folder_text = UiFunctions.text_field('txt_root_folder', 500)
        self.root_folder_text.setDisabled(True)
        root_folder_button = UiFunctions.button('...', 40, 35, partial(self.select_folder_clicked, self.root_folder_text, True))

        save_folder_label = UiFunctions.label('save folder: ', width=100, height=35, h_align=Qt.AlignRight)
        self.save_folder_text = UiFunctions.text_field('txt_save_folder', 500)
        self.save_folder_text.setDisabled(True)
        save_folder_button = UiFunctions.button('...', 40, 35, partial(self.select_folder_clicked, self.save_folder_text))

        self.list_widget = FilesList()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.itemSelectionChanged.connect(self.list_changed)

        selected_text = '0 files selected'
        self.selected_label = UiFunctions.label(text=selected_text, h_align=Qt.AlignCenter)

        # buttons
        cancel_button = UiFunctions.button(text='cancel', width=150, height=30, clicked=self.close)
        archive_button = UiFunctions.button(text='archive', width=150, height=30, clicked=self.archive_clicked)

        # adding to layouts
        empty_widget, horizontal_layout = UiFunctions.horizontal_line(30)
        UiFunctions.add_widgets(horizontal_layout,
                                [root_folder_label, self.root_folder_text,
                                 root_folder_button, UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)

        empty_widget, horizontal_layout = UiFunctions.horizontal_line(30)
        UiFunctions.add_widgets(horizontal_layout,
                                [save_folder_label, self.save_folder_text,
                                 save_folder_button, UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)

        folder_frame.setLayout(folder_layout)

        selected_layout.addWidget(self.selected_label)
        selected_frame.setLayout(selected_layout)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(archive_button)
        buttons_frame.setLayout(buttons_layout)

        main_layout.addWidget(folder_frame)
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(selected_frame)
        main_layout.addWidget(buttons_frame)
        
    def list_changed(self) -> None:
        selected_rows = [self.list_widget.row(item) for item in self.list_widget.selectedItems()]
        if len(selected_rows) == 1:
            text = '1 file selected'
        else:
            text = f'{len(selected_rows)} files selected'
        self.selected_label.setText(text)

    def select_folder_clicked(self, text_field=None, refresh_list=False) -> None:
        selected_folder = str(QFileDialog.getExistingDirectory(self, 'Select Folder'))
        text_field.setText(selected_folder)
        if refresh_list:
            self.list_widget.start_dir = selected_folder
            self.list_widget.maya_files()

    def archive_clicked(self) -> None:
        if self.verification():
            self.run_archive()

    def verification(self) -> bool:
        file_list = [item.text() for item in self.list_widget.selectedItems()]
        save_folder = self.save_folder_text.text()
        
        if save_folder == '':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select a "Save Folder" to place the zip files!')
            return False
        
        if not os.path.exists(save_folder):
            UiFunctions.error_message(title=__tool_name__,
                                      message='"Save Folder" does not exists!')
            return False

        if len(file_list) == 0:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select at least one file to archive!')
            return False

        return True

    @Slot()
    def run_archive(self) -> None:
        file_list = [item.text() for item in self.list_widget.selectedItems()]

        self.started.emit()
        archive_logic = ArchiveScenesLogic()
        archive_logic.export_folder = self.save_folder_text.text()
        archive_logic.bulk_archive(file_list)
        self.finished.emit()

        UiFunctions.error_message(title=__tool_name__,
                                  message='All scenes have been archived!',
                                  message_type='info')

        self.close()


class ArchiveScenesUi:

    def open_ui(self) -> None:
        Dialog()