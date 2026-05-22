import os
from functools import partial

import maya.cmds as cmds
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from startup.ui_functions import UiFunctions
from usd_tools.usd_tools_logic import UsdToolsLogic

__tool_name__ = 'USD Tools'
__tool_class__ = 'UsdToolsUi'
__tool_function__ = ''
__tool_submenu__ = {'USD Tools':
                        {'Export Asset': 'export_asset_ui'
                         }
                    }

class UsdExportUi(QDialog):
    def __init__(self, parent=None):
        super(UsdExportUi, self).__init__(parent)
        UiFunctions.create_window(self, f'{__tool_name__} - Export Asset', 700, 400)

        self.draw_ui()
        self.populate_ui()
        self.show()

    def draw_ui(self) -> None:
        # layouts
        main_layout = QVBoxLayout(self)
        folder_layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout(self)

        # frames
        folder_frame = QFrame()
        folder_frame.setFrameShape(QFrame.StyledPanel)
        folder_frame.setFrameShadow(QFrame.Plain)
        folder_frame.setFixedHeight(280)
        folder_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        buttons_frame = QFrame()
        buttons_frame.setFrameShape(QFrame.StyledPanel)
        buttons_frame.setFrameShadow(QFrame.Plain)
        buttons_frame.setFixedHeight(80)
        buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # objects
        asset_name_label = UiFunctions.label('asset name: ', width=120, height=40, h_align=Qt.AlignRight)
        self.asset_name_text = UiFunctions.text_field('txt_asset_name', 500, 40)
        self.asset_name_text.setDisabled(True)

        asset_variants_label = UiFunctions.label('asset variants: ', width=120, height=40, h_align=Qt.AlignRight)
        self.variant_list_widget = QListWidget()
        self.variant_list_widget.setDisabled(True)
        self.variant_list_widget.setFixedWidth(500)
        self.variant_list_widget.setFixedHeight(100)

        base_folder_label = UiFunctions.label('base folder: ', width=120, height=40, h_align=Qt.AlignRight)
        self.base_folder_text = UiFunctions.text_field('txt_base_folder', 460)
        self.base_folder_text.setDisabled(True)
        base_folder_button = UiFunctions.button('...', 40, 35, self._base_folder_clicked)

        variants_folder_label = UiFunctions.label('variants folder: ', width=120, height=40, h_align=Qt.AlignRight)
        self.variants_folder_text = UiFunctions.text_field('txt_variants_folder', 500)
        self.variants_folder_text.setDisabled(True)

        # buttons
        cancel_button = UiFunctions.button(text='cancel', width=150, height=40, clicked=self.close)
        export_button = UiFunctions.button(text='export', width=150, height=40, clicked=self.export_clicked)

        # adding to layouts
        empty_widget, horizontal_layout = UiFunctions.horizontal_line(40)
        UiFunctions.add_widgets(horizontal_layout, [asset_name_label, self.asset_name_text, UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)
        folder_frame.setLayout(folder_layout)

        empty_widget, horizontal_layout = UiFunctions.horizontal_line(120)
        UiFunctions.add_widgets(horizontal_layout, [asset_variants_label, self.variant_list_widget, UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)
        folder_frame.setLayout(folder_layout)

        empty_widget, horizontal_layout = UiFunctions.horizontal_line(40)
        UiFunctions.add_widgets(horizontal_layout, [base_folder_label, self.base_folder_text,
                                base_folder_button, UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)
        folder_frame.setLayout(folder_layout)

        empty_widget, horizontal_layout = UiFunctions.horizontal_line(40)
        UiFunctions.add_widgets(horizontal_layout, [variants_folder_label, self.variants_folder_text,
                                                    UiFunctions.spacer(20)])
        folder_layout.addWidget(empty_widget)
        folder_frame.setLayout(folder_layout)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(export_button)
        buttons_frame.setLayout(buttons_layout)

        main_layout.addWidget(folder_frame)
        main_layout.addWidget(buttons_frame)

    def populate_ui(self) -> None:
        self._fetch_asset_data()
        self.asset_name_text.setText(self.asset_name)
        self.variant_list_widget.clear()
        variants_list = list(self.variants_dict.keys())
        self.variant_list_widget.addItems(variants_list)

    def _fetch_asset_data(self) -> None:
        selection = cmds.ls(selection=True, long=True)[0]
        self.asset_name = selection.replace('|', '')
        all_relatives = cmds.listRelatives(selection, allDescendents=True, fullPath=True)
        all_relatives.sort(key=len, reverse=False)
        self.variants_dict = {}
        for obj in all_relatives:
            node_list = obj.split('|')[1:]
            if len(node_list) == 4:
                variant_name = obj.split('|')[-2].replace('_var_', '')
                variant_root = obj
                self.variants_dict[variant_name] = variant_root

    def _base_folder_clicked(self, *args) -> None:
        selected_folder = str(QFileDialog.getExistingDirectory(self, 'Select Folder'))
        self.base_folder_text.setText(selected_folder)
        variants_folder = os.path.join(selected_folder, self.asset_name, 'variants').replace('\\', '/')
        self.variants_folder_text.setText(variants_folder)

    def export_clicked(self) -> None:
        print(f'{self.variants_dict = }')
        logic = UsdToolsLogic()
        logic.variants_dict = self.variants_dict
        logic.asset_name = self.asset_name
        logic.base_folder = self.base_folder_text.text()
        logic.export_asset()


class UsdToolsUi:

    def __init__(self):
        pass

    def _validate_export(self) -> bool:
        selection = cmds.ls(selection=True)
        if not selection:
            UiFunctions.error_message(title=__tool_name__, message='Select ONE asset')
            return False

        if len(selection) > 1:
            UiFunctions.error_message(title=__tool_name__, message='Select only ONE asset')
            return False

        hierarchy_check = self._check_hierarchy()
        if hierarchy_check != '':
            UiFunctions.error_message(title=__tool_name__, message=hierarchy_check)
            return False

        return True

    def _check_hierarchy(self) -> str:
        error_message = ''
        selection = cmds.ls(selection=True, long=True)[0]
        asset = selection.split('|')[-1]
        children_list = cmds.listRelatives(selection, allDescendents=True, fullPath=True)
        children_list.sort(key=len, reverse=True)
        max_hierarchy = children_list[0]
        asset_level = max_hierarchy.split(asset)[-1]
        first_level = asset_level.split('|')[1]
        second_level = asset_level.split('|')[2]
        third_level = asset_level.split('|')[3]

        if first_level != 'MESH':
            error_message = 'Error on the hierarchy.\nThe second group must be "MESH"!'
            return error_message

        if not second_level.startswith('_var_'):
            error_message = 'Variant groups must start with "_var_"!'
            return error_message

        if third_level != 'geo':
            error_message = 'Error on the hierarchy.\nThe third group must be "geo"!'
            return error_message

        return error_message

    def export_asset_ui(self, *args) -> None:
        if self._validate_export():
            UsdExportUi()
