import os

import maya.cmds as cmds
import maya.utils as utils
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from startup.startup_tools import StartupTools


class LoadTools:

    def __init__(self):
        self.menu_name = None

    def get_menu(self):
        menu_bar = None
        menu_item = None
        menu_name = 'flTools'

        main_window_ptr = omui.MQtUtil.mainWindow()
        main_window = wrapInstance(int(main_window_ptr), QWidget)
        for child in main_window.children():
            if isinstance(child, QMenuBar):
                menu_bar = child
        for top_menu in menu_bar.actions():
            if top_menu.isVisible():
                if top_menu.text() == menu_name:
                    menu_item = top_menu.text()
                    break
        return menu_item

    # def search_tools(self):
    #     """
    #     Look for tools inside directories
    #     """
    #     include_tools = ['archive_scenes', 'camera_keyframer']
    #     ignore_dirs = ['_images', '_tests', '__pycache__']
    #     self.message_box('Startup :: search_tools')
    #     # script_dir = Path(__file__).resolve().parent
    #     # print(f'script_dir >> {script_dir}')
    #     # dirname = os.path.dirname(__file__)
    #     # print(f'dirname >> {dirname}')
    #     path = os.path.dirname(os.path.abspath(__file__))
    #     print(f'path >> {path}')
    #     # parent_path = os.path.abspath(os.path.join(path, os.pardir))
    #     for root, dirs, filenames in os.walk(path):
    #         for dir in dirs:
    #             if dir in ignore_dirs:
    #                 continue
    #             else:
    #                 if dir in include_tools:
    #                     module_path = os.path.join(root, dir, f'{dir}_ui.py')
    #                     self.import_module(module_path)

    # def import_module(self, module_path):
    #     """
    #     Import modules and additional data from a given directory
    #     """
    #     print(module_path)
    #     spec = importlib.util.spec_from_file_location('', module_path)
    #     module = importlib.util.module_from_spec(spec)
    #     sys.modules[spec.name] = module 
    #     spec.loader.exec_module(module)
    #     tool_class = eval(f'module.__tool_class__')
    #     self.tools[tool_class] = {'name': eval(f'module.__tool_name__'),
    #                               'function_name': eval(f'module.__tool_function__'),
    #                               'module': module}

    # def menu(self):
    #     """
    #     Creates menu items using data collected from directories
    #     """
    #     for tool in self.tools:
    #         cmds.menuItem(parent=self.menu_name, label=self.tools[tool]['name'],
    #                       command=eval(f'self.tools[tool]["module"].{tool}.{self.tools[tool]["function_name"]}'))
    #     # cmds.setParent('..', menu=True)
    #     cmds.menuItem(parent=self.menu_name, divider=True)
    #     cmds.menuItem(parent=self.menu_name, label='About', command=self.about)

    def load_menu(self):

        self.menu_name = self.get_menu()
        if not self.menu_name:
            self.menu_name = cmds.menu('flTools', parent='MayaWindow', tearOff=True)

        startup_tools = StartupTools(self.menu_name)
        startup_tools.menu_items()
        # startup_tools.search_tools()
        # startup_tools.import_modules()
        # self.search_tools()
        # self.menu()

    def message_box(self, text_message=None):
        box_size = 100
        message_title = f'|{ " flTools ".center(box_size, "-") }|\n'
        message_footer = f'|{ "".center(box_size, "-") }|\n'
        message_text = f'| {text_message.ljust(box_size-2, " ")} |\n'
        print(message_title + message_text + message_footer)
        


if __name__ == '__main__':
    LoadTools = LoadTools()
    LoadTools.message_box('loading...')
    utils.executeDeferred(LoadTools.load_menu)
