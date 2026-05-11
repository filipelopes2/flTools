import os
from functools import partial

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from zip_render.zip_render_logic import ZipRenderLogic
from startup.ui_functions import UiFunctions


__tool_name__ = 'Zip Render'
__tool_class__ = 'OpenZipRender'
__tool_function__ = 'open_ui'
__tool_submenu__ = 'Archive'


class ZipRenderUi(QDialog):

    started = Signal()
    finished = Signal()

    def __init__(self):
        super().__init__()

        self.project_data = ''
        self.base_path = ''
        self.archive_folder = ''

        UiFunctions.create_window(self, __tool_name__, 600, 900)

        # generating zip message
        self._message_box = QMessageBox()
        self._message_box.setText(str('Generating zip file... Please Wait...'))
        self._message_box.setStandardButtons(QMessageBox.NoButton)
        self.started.connect(self._message_box.show)
        self.finished.connect(self._message_box.accept)

    def draw_ui(self) -> None:
        # layouts
        main_layout = QVBoxLayout(self)
        description_layout = QHBoxLayout(self)
        path_layout = QHBoxLayout(self)
        selected_layout = QHBoxLayout(self)
        buttons_layout = QHBoxLayout(self)

        # frames
        description_frame = QFrame()
        description_frame.setFrameShape(QFrame.StyledPanel)
        description_frame.setFrameShadow(QFrame.Plain)
        description_frame.setFixedHeight(100)
        description_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        zip_frame = QFrame()
        zip_frame.setFrameShape(QFrame.StyledPanel)
        zip_frame.setFrameShadow(QFrame.Plain)
        zip_frame.setFixedHeight(60)
        zip_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        base_frame = QFrame()
        base_frame.setFrameShape(QFrame.StyledPanel)
        base_frame.setFrameShadow(QFrame.Plain)
        base_frame.setFixedHeight(60)
        base_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

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
        description_text = ('Select the folders you want to archive.\n'
                            'To select multiple folders, hold ctrl and select the folder.\n'
                            'The resulting file will be saved on the folder below')
        description_label = UiFunctions.label(text=description_text, height=80)

        zip_folder_label = UiFunctions.label('zip folder: ', width=85, height=35, h_align=Qt.AlignRight)
        self.zip_folder = UiFunctions.text_field('txt_zip_folder', 400)
        self.zip_folder.setDisabled(True)
        zip_folder_button = UiFunctions.button('...', 40, 35, partial(self.select_folder_clicked, self.zip_folder))
        zip_widget, zip_layout = UiFunctions.horizontal_line(30)
        UiFunctions.add_widgets(zip_layout, [zip_folder_label, self.zip_folder,
                                             zip_folder_button, UiFunctions.spacer(20)])

        base_folder_label = UiFunctions.label('base folder: ', width=85, height=35, h_align=Qt.AlignRight)
        self.base_folder = UiFunctions.text_field('txt_base_folder', 400)
        self.base_folder.setDisabled(True)
        base_folder_button = UiFunctions.button('...', 40, 35, partial(self.select_folder_clicked, self.base_folder))
        base_widget, base_layout = UiFunctions.horizontal_line(30)
        UiFunctions.add_widgets(base_layout, [base_folder_label, self.base_folder,
                                              base_folder_button, UiFunctions.spacer(20)])

        # list
        self.treeview = QTreeView()
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(QDir.rootPath())
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.treeview.setModel(self.dir_model)
        self.treeview.setRootIndex(self.dir_model.index(self.base_path))
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)
        self.treeview.setHeaderHidden(1)
        self.treeview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeview.selectionModel().selectionChanged.connect(self.treeview_on_clicked)

        # selected items
        self.selected_label = UiFunctions.label(text='0 folders selected', height=15, h_align=Qt.AlignCenter)

        # buttons
        cancel_button = UiFunctions.button(text='cancel', width=150, height=30, clicked=self.close)
        zip_button = UiFunctions.button(text='zip files', width=150, height=30, clicked=self.run_zip)

        # adding to layouts
        description_layout.addWidget(description_label)
        description_frame.setLayout(description_layout)

        path_layout.addWidget(zip_widget)
        zip_frame.setLayout(zip_layout)
        path_layout.addWidget(base_widget)
        base_frame.setLayout(base_layout)

        selected_layout.addWidget(self.selected_label)
        selected_frame.setLayout(selected_layout)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(zip_button)
        buttons_frame.setLayout(buttons_layout)

        main_layout.addWidget(description_frame)
        main_layout.addWidget(zip_frame)
        main_layout.addWidget(base_frame)
        main_layout.addWidget(self.treeview)
        main_layout.addWidget(selected_frame)
        main_layout.addWidget(buttons_frame)

        self.show()

    def select_folder_clicked(self, text_field=None) -> None:
        selected_folder = str(QFileDialog.getExistingDirectory(self, 'Select Folder'))
        text_field.setText(selected_folder)

    def treeview_on_clicked(self) -> None:
        indexes = self.treeview.selectionModel().selectedRows()
        if len(indexes) == 1:
            text = '1 folder selected'
        else:
            text = f'{len(indexes)} folders selected'
        self.selected_label.setText(text)

    def verification(self) -> bool:
        if self.zip_folder.text() == '':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select a folder to copy the zip file!')
            return False

        if self.base_folder.text() == '':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select a base folder!')
            return False

        if not os.path.exists(self.zip_folder.text()):
            UiFunctions.error_message(title=__tool_name__,
                                      message='Zip folder does not exist!')
            return False
        return True

    @Slot()
    def run_zip(self) -> None:
        if self.verification():
            self.started.emit()
            zip_logic = ZipRenderLogic()
            zip_logic.archive_folder = self.zip_folder.text()
            zip_logic.base_folder = self.base_folder.text()
            indexes = self.treeview.selectionModel().selectedRows()
            zip_logic.folder_list = [self.dir_model.filePath(i).replace(f'{self.base_folder.text()}/', '')
                                     for i in indexes]

            if not zip_logic.zip_files():
                UiFunctions.error_message(title=__tool_name__,
                                          message='Zip folder does not exist!')
            else:
                UiFunctions.error_message(title=__tool_name__,
                                          message='Zip file generated.\nCheck the Script Editor for the file path.',
                                          message_type='info')
            self.finished.emit()
            self.close()


class OpenZipRender:

    def __init__(self):
        pass

    def open_ui(self):
        ZipRenderUi().draw_ui()