import maya.cmds as cmds
from functools import partial

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from move_all_maker.move_all_maker_logic import MoveAllMakerLogic
from startup.ui_functions import UiFunctions


__tool_name__ = 'Move All Maker'
__tool_class__ = 'OpenUi'
__tool_function__ = 'open_ui'
__tool_submenu__ = 'Animation'


class MoveAllMakerUi(QDialog):
    def __init__(self):
        super().__init__()

        self.moveall_type = None
        UiFunctions.create_window(self, __tool_name__, 450, 150)
        self.draw_ui()

    def draw_ui(self):
        # layouts
        main_layout = QVBoxLayout()
        inside_layout = QGridLayout()
        inside_layout.setAlignment(Qt.AlignTop)
        frame = UiFunctions.frame()

        parent_label = UiFunctions.label('parent type:  ', h_align=Qt.AlignCenter)
        radio_constraint = QRadioButton('constraint')
        radio_constraint.toggled.connect(partial(self.set_type, 1))
        radio_skin = QRadioButton('skin')
        radio_skin.toggled.connect(partial(self.set_type, 2))
        radio_skin.setChecked(True)
        button = UiFunctions.button('create move all', width=300, height=35, clicked=self.create_moveall_clicked)

        empty_widget, horizontal_layout = UiFunctions.horizontal_line(50)
        UiFunctions.add_widgets(horizontal_layout,
                                [parent_label, radio_constraint,
                                 radio_skin, UiFunctions.spacer(20)])
        inside_layout.addWidget(empty_widget)
        inside_layout.addWidget(button, 2, 0, 0, 3, Qt.AlignCenter | Qt.AlignBottom)
        frame.setLayout(inside_layout)
        main_layout.addWidget(frame)

        self.setLayout(main_layout)

        self.show()

    def set_type(self, type_set, *args) -> None:
        self.moveall_type = type_set

    def create_moveall_clicked(self) -> None:
        selection = cmds.ls(sl=True)
        if not selection:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select at least one object.')
        else:
            if MoveAllMakerLogic().create_move_all(moveall_type=self.moveall_type):
                self.close()

class OpenUi:
    def open_ui(self):
        MoveAllMakerUi()