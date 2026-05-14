import os
import sys
import importlib.util
import maya.cmds as cmds
from functools import partial
from PySide6.QtWidgets import *

from startup.ui_functions import UiFunctions
from pprint import pp


class StartupTools:

    def __init__(self, menu_name):
        self.menu_name = menu_name
        self.tools = {}

    def _delete_menus(self) -> None:
        cmds.menu(self.menu_name, edit=True, deleteAllItems=True)

    def _search_tools(self) -> None:
        """
        Look for tools inside directories
        """
        ignore_dirs = ['startup', '__pycache__', '_images']
        path = os.path.dirname(os.path.abspath(__file__ + '/../'))

        for root, dirs, filenames in os.walk(path):
            for directory in dirs:
                if directory in ignore_dirs:
                    continue
                else:
                    module_path = os.path.join(root, directory, f'{directory}_ui.py')
                    if not os.path.isfile(module_path):
                        module_path = os.path.join(root, directory, f'{directory}_logic.py')
                    self._import_module(module_path)

    def _import_module(self, module_path=None) -> None:
        """
        Import modules and additional data from a given directory
        """
        spec = importlib.util.spec_from_file_location('', module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module 
        spec.loader.exec_module(module)
        tool_class = eval(f'module.__tool_class__')
        self.tools[tool_class] = {'name': eval(f'module.__tool_name__'),
                                  'function_name': eval(f'module.__tool_function__'),
                                  'module': module,
                                  'submenu': eval(f'module.__tool_submenu__')}
        
    def menu_items(self) -> None:
        """
        Creates menu items using data collected from directories
        """
        self._search_tools()
        self._delete_menus()

        # creating submenus
        submenus_list = []
        for tool in self.tools:
            if isinstance(self.tools[tool]['submenu'], str):
                submenus_list.append(self.tools[tool]['submenu'])
            if isinstance(self.tools[tool]['submenu'], dict):
                submenus_list.append(list(self.tools[tool]['submenu'].keys())[0])

        submenus_list = list(set(submenus_list))
        submenus_list.sort()
        submenus_dict = {}
        for submenu in submenus_list:
            if submenu != '_':
                submenus_dict[submenu] = cmds.menuItem(parent=self.menu_name, tearOff=True, label=submenu, subMenu=True)

        for tool in self.tools:
            if self.tools[tool]['submenu'] == '_':
                parent_menu = self.menu_name
            elif isinstance(self.tools[tool]['submenu'], dict):
                parent_menu = list(self.tools[tool]['submenu'].keys())[0]
            else:
                parent_menu = self.tools[tool]['submenu']

            if not isinstance(self.tools[tool]['submenu'], dict):
                cmds.menuItem(parent=submenus_dict[parent_menu], label=self.tools[tool]['name'],
                              command=eval(f'self.tools[tool]["module"].{tool}.{self.tools[tool]["function_name"]}'))
            else:
                for item in self.tools[tool]['submenu'][parent_menu]:
                    cmds.menuItem(parent=submenus_dict[parent_menu], label=item,
                                  command=eval(f'self.tools[tool]["module"].{tool}().{self.tools[tool]["submenu"][parent_menu][item]}'))

        cmds.menuItem(parent=self.menu_name, divider=True)
        cmds.menuItem(parent=self.menu_name, label='About', command=self._about_clicked)

    def _about_clicked(self, *args) -> None:
        window_dialog = QDialog()
        UiFunctions.create_window(window_dialog, 'flTools', 400, 400)

        # layouts
        main_layout = QVBoxLayout()
        description_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        # frames
        description_frame = QFrame()
        description_frame.setFrameShape(QFrame.StyledPanel)
        description_frame.setFrameShadow(QFrame.Plain)
        description_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        buttons_frame = QFrame()
        buttons_frame.setFrameShape(QFrame.StyledPanel)
        buttons_frame.setFrameShadow(QFrame.Plain)
        buttons_frame.setFixedHeight(80)
        buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # text
        text_label = QTextEdit()
        markdown_content = ('# flTools\n'
                            '---\n'
                            'version 0.1 - 2026/05\n\n'
                            'developed by **Filipe Lopes**\n'
                            'filipelopes.brz@gmail.com\n')
        text_label.setDisabled(True)
        qstyle = """QTextEdit:disabled {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #545357, stop:1 #9a989d);
            padding: 10px;
            color: white;
            font-size: 14px;
            border: 2px solid #333;
            border-radius: 5px;
        }"""
        text_label.setStyleSheet(qstyle)
        text_label.setMarkdown(markdown_content)

        # button
        close_button = UiFunctions.button('close', 200, 40, partial(self._about_close, window_dialog))

        # adding to frames and layouts
        description_layout.addWidget(text_label)
        description_frame.setLayout(description_layout)

        buttons_layout.addWidget(close_button)
        buttons_frame.setLayout(buttons_layout)

        main_layout.addWidget(description_frame)
        main_layout.addWidget(buttons_frame)

        window_dialog.setLayout(main_layout)
        window_dialog.show()

    def _about_close(self, window_dialog) -> None:
        window_dialog.close()
