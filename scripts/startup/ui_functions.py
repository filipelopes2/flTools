import os
import shutil
from typing import Tuple

import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from shiboken6 import wrapInstance


class UiFunctions:

    def __init__(self):
        pass

    @staticmethod
    def horizontal_line(height=0, alignment='', spacing=0, color='') -> Tuple[QWidget, QHBoxLayout]:
        obj_widget = QWidget()
        if height != 0: obj_widget.setFixedHeight(height)
        if color != '': obj_widget.setStyleSheet(f'background-color: {color};')
        obj_widget.setContentsMargins(0, 0, 0, 0)
        obj_layout = QHBoxLayout(obj_widget)
        if alignment != '':
            obj_layout.setAlignment(alignment)
        obj_layout.setContentsMargins(0, 0, 0, 0)
        obj_layout.setSpacing(spacing)
        obj_layout.addStretch()
        return obj_widget, obj_layout

    @staticmethod
    def add_widgets(layout, objs=''):
        if type(objs) is list:
            for obj in objs:
                if type(obj) == QSpacerItem:
                    layout.addItem(obj)
                else:
                    layout.addWidget(obj)
        else:
            layout.addWidget(objs)
        return layout

    @staticmethod
    def spacer(width=1, height=1) -> QSpacerItem:
        obj_spacer = QSpacerItem(width, height, QSizePolicy.Policy.Expanding)
        return obj_spacer

    @staticmethod
    def text_field(name, width=None, height=None, alignment=None, color=None) -> QLineEdit:
        obj_field = QLineEdit()
        obj_field.setObjectName(name)
        if alignment: obj_field.setAlignment(alignment)
        if width: obj_field.setFixedWidth(width)
        if height: obj_field.setFixedHeight(height)
        if color: obj_field.setStyleSheet('background-color: ' + color)
        obj_field.clear()
        return obj_field

    @staticmethod
    def create_window(class_obj=None, window_title=None, width=None, height=None) -> None:
        class_obj.setAttribute(Qt.WA_DeleteOnClose)
        if cmds.window(window_title, q=True, exists=True):
            cmds.deleteUI(window_title)
        class_obj.setObjectName(window_title)

        # remove minimize button
        class_obj.setWindowFlags(class_obj.windowFlags() & Qt.CustomizeWindowHint)
        class_obj.setWindowFlags(class_obj.windowFlags() & ~Qt.WindowMinMaxButtonsHint)

        class_obj.maya_main_ptr = omui.MQtUtil.mainWindow()
        class_obj.maya_main_window = wrapInstance(int(class_obj.maya_main_ptr), QWidget)
        class_obj.setParent(class_obj.maya_main_window)
        class_obj.setWindowFlags(Qt.Window)
        class_obj.setWindowTitle(window_title)
        class_obj.setFixedSize(width, height)

    @staticmethod
    def label(text=None, width=None, height=None, h_align=None, v_align=None, color=None) -> QLabel:
        obj_label = QLabel(text)
        if not h_align: h_align = Qt.AlignLeft
        if not v_align: v_align = Qt.AlignVCenter
        obj_label.setAlignment(h_align | v_align)
        if width: obj_label.setFixedWidth(width)
        if height: obj_label.setFixedHeight(height)
        else: obj_label.setFixedHeight(30)
        if color: obj_label.setStyleSheet('background-color: ' + color)
        return obj_label

    @staticmethod
    def button(text, width=None, height=25, clicked=None, color=None) -> QPushButton:
        obj_button = QPushButton(text)
        if width: obj_button.setFixedSize(width, height)
        if color: obj_button.setStyleSheet('background-color: ' + color)
        if clicked: obj_button.clicked.connect(clicked)
        return obj_button

    @staticmethod
    def error_message(title=None, message=None, message_type='error') -> None:
        # QMessageBox.critical(None, title, message, QMessageBox.StandardButton.Ok)
        error_message = QMessageBox()
        error_message.setWindowTitle(title)
        error_message.setText(message)
        if message_type != '':
            if message_type == 'error':
                error_message.setIcon(QMessageBox.Critical)
            if message_type == 'info':
                error_message.setIcon(QMessageBox.Information)
        error_message.exec_()

    @staticmethod
    def frame(width=0, height=0):
        obj_frame = QFrame()
        obj_frame.setFrameShape(QFrame.StyledPanel)
        obj_frame.setFrameShadow(QFrame.Plain)
        if height > 0:
            obj_frame.setFixedHeight(height)
        if width > 0:
            obj_frame.setFixedWidth(width)
        obj_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        return obj_frame

    @staticmethod
    def check_plugin(plugin=None, force_load=False) -> bool:
        """
        Checks whether the plug-in is loaded.

        If the plug-in is not loaded, a window will appear with the warning. This window will have a button to open the
        Plug-ins window. If the user chooses to open using this button, the window will already be loaded with the
        plugin's name as filter.

        Return:
            bool:
                True if plugin is loaded, False if not.
        """

        plugin_dict = {'vray': {'description': 'V-Ray',
                                'filename': 'vrayformaya.mll'},
                       'yeti': {'description': 'Yeti',
                                'filename': 'pgYetiMaya.mll'},
                       'arnold': {'description': 'Arnold',
                                  'filename': 'mtoa.mll'},
                       'abc_import': {'description': 'Alembic import',
                                      'filename': 'AbcImport.mll'},
                       'abc_export': {'description': 'Alembic export',
                                      'filename': 'AbcExport.mll'},
                       'usd': {'description': 'Maya Usd',
                               'filename': 'mayaUsdPlugin.mll'}
                       }

        # check plugin
        if cmds.pluginInfo(plugin_dict[plugin]['filename'], q=True, loaded=True):
            return True

        else:
            if force_load:
                cmds.loadPlugin(plugin_dict[plugin]['filename'])
                return True
            else:
                # Create mel command to open Plug-in Manager window and filter for selected plugin
                mel_cmd = '''
                          global string $gPluginSearchField;
                          if (`exists PluginManager`)
                          {
                            PluginManager;
                            if(`textField -exists $gPluginSearchField`)
                            {
                                textField -edit -text ''' + plugin_dict[plugin]['filename'] + ''' $gPluginSearchField;
                            }
                          } else
                          {
                            confirmDialog -title "404 ( 8P )" -message "Window \"PluginManager\" not found" -icon "warning";
                          }
                          '''
                result = cmds.confirmDialog(title='Warning',
                                            message=f'Load {plugin_dict[plugin]["description"]} plugin.\n'
                                                    f'Windows > Settings/Preferences > Plug-in Manager',
                                            button=['Ok', 'Open Plug-in Manager'])
                if result == 'Open Plug-in Manager':
                    mel.eval(mel_cmd)
                return False

    @staticmethod
    def copy_file(from_path=None, to_path=None) -> bool:
        try:
            shutil.copy(from_path, to_path)
            return True
        except IOError as error:
            print(' ERROR '.center(100, '='))
            print('Unable to copy file.')
            print(error)
            print(''.center(100, '='))
            return False

    @staticmethod
    def create_dir(file_path=None) -> bool:
        """
        if path doesn't exist, tries to create all directories on the full_path
        :param file_path: path to be created
        :return: True if successful
        """
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as error:
                UiFunctions.error_message(title='ERROR',
                                          message='Could not create directories.\n'
                                          'Contact the system administrator.')
                print(' ERROR '.center(100, '='))
                print('Could not create directories.')
                print(error)
                print(''.center(100, '='))
                return False
        return True