import maya.cmds as cmds
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from functools import partial

from camera_keyframer.camera_keyframer_logic import CamKeyframer_Logic
from startup.ui_functions import UiFunctions


__tool_name__ = 'Camera Keyframer'
__tool_class__ = 'CamKeyframerUI'
__tool_function__ = 'open_ui'
__tool_submenu__ = 'Animation'


class CamKeyframerWindow(QDialog):

    def __init__(self):
        super(CamKeyframerWindow, self).__init__()

        self.camera_text = None

        UiFunctions.create_window(self, __tool_name__, 500, 200)

        self.show()

    def draw_ui(self) -> None:
        # layouts
        main_layout = QVBoxLayout(self)
        camera_layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout(self)

        selected_frame = QFrame()
        selected_frame.setFrameShape(QFrame.StyledPanel)
        selected_frame.setFrameShadow(QFrame.Plain)
        selected_frame.setFixedHeight(80)
        selected_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        buttons_frame = QFrame()
        buttons_frame.setFrameShape(QFrame.StyledPanel)
        buttons_frame.setFrameShadow(QFrame.Plain)
        buttons_frame.setFixedHeight(80)
        buttons_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # objects
        camera_label = UiFunctions.label('camera: ', width=70, height=40, h_align=Qt.AlignRight)
        self.camera_text = UiFunctions.text_field('txt_camera', 200)
        self.camera_text.setDisabled(True)
        select_camera_button = UiFunctions.button('select', 100, 30,
                                                  partial(self.select_camera_clicked, self.camera_text))
        # buttons
        set_key_button = UiFunctions.button(text='set key', width=150, height=40,
                                            clicked=partial(self.button_clicked, 'set_keys'))
        focal_length_button = UiFunctions.button(text='focal length curve', width=150, height=40,
                                                 clicked=partial(self.button_clicked, 'focal_length'))

        # adding to layouts
        empty_widget, horizontal_layout = UiFunctions.horizontal_line(60)
        UiFunctions.add_widgets(horizontal_layout,
                                [camera_label, self.camera_text, select_camera_button, UiFunctions.spacer(20)])

        camera_layout.addWidget(empty_widget)
        selected_frame.setLayout(camera_layout)

        buttons_layout.addWidget(set_key_button)
        buttons_layout.addWidget(focal_length_button)
        buttons_frame.setLayout(buttons_layout)

        main_layout.addWidget(selected_frame)
        main_layout.addWidget(buttons_frame)

    def select_camera_clicked(self, *args) -> None:
        if self.verification():
            self.camera_text.setText(cmds.ls(sl=True)[0])

    def verification(self) -> bool:
        selection = cmds.ls(sl=True)

        if len(selection) < 1:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select one camera!')
            return False

        if len(selection) > 1:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select only one camera!')
            return False

        selection = selection[0]
        shape = cmds.listRelatives(selection, s=True)[0]
        object_type = cmds.objectType(shape)
        if object_type != 'camera':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select one camera!')

        return True

    def button_clicked(self, button_type=None, *args) -> None:
        camera_name = self.camera_text.text()
        if camera_name == '':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select one camera!')
        else:
            if button_type == 'set_keys':
                CamKeyframer_Logic.set_keys(camera_name=camera_name)
            else:
                CamKeyframer_Logic.focal_length_curve(camera_name=camera_name)


class CamKeyframerUI:

    def open_ui(self) -> None:
        CamKeyframerWindow().draw_ui()