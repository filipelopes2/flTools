import maya.cmds as cmds

from startup.ui_functions import UiFunctions


__tool_name__ = 'Duplicate Camera'
__tool_class__ = 'DuplicateCameraRun'
__tool_function__ = 'duplicate_camera_run'
__tool_submenu__ = 'Animation'


class DuplicateCameraLogic:

    def __init__(self):
        self.selection = None

    def _evaluate_selection(self) -> bool:
        """
        Check if there's a camera selected
        """
        self.selection = cmds.ls(sl=True)
        error_message = None
        if not self.selection:
            error_message = 'Select a camera object!'
        else:
            if len(self.selection) > 1:
                error_message = 'Select only ONE camera object!'
            else:
                self.selection = self.selection[0]
                selection_shape = cmds.listRelatives(self.selection, shapes=True)[0]
                if cmds.objectType(selection_shape) != 'camera':
                    error_message = 'Selected object is not a camera!'

        if error_message:
            UiFunctions.error_message(title=__tool_name__,
                                      message=error_message)
            return False
        else:
            return True

    def duplicate_camera(self) -> None:
        """
        Creates a new camera with data from the selected camera
        """

        if not self._evaluate_selection():
            return

        self.new_camera = cmds.camera()
        self.new_camera_shape = self.new_camera[1]
        new_scale = 2

        # matching tranformations
        cmds.matchTransform(self.new_camera[0], self.selection, position=True, rotation=True)
        cmds.parentConstraint(self.selection, self.new_camera[0], weight=1)

        old_camera_attrs = cmds.listAttr(self.selection)
        new_camera_attrs = cmds.listAttr(self.selection)

        old_camera_shape = cmds.listRelatives(self.selection, shapes=True)[0]
        old_camera_shape_attrs = cmds.listAttr(old_camera_shape)
        new_camera_shape_attrs = cmds.listAttr(self.new_camera_shape)

        attr_ignore = ['locatorScale', 'displayCameraFrustum', 'scale', 'scaleX', 'scaleY', 'scaleZ']

        # connecting transform attributes
        for attr in old_camera_attrs:
            try:
                if attr not in attr_ignore:
                    cmds.connectAttr(self.selection + '.' + attr, self.new_camera[0] + '.' + attr)
            except:
                continue

        # connecting shape attributes
        for attr in old_camera_shape_attrs:
            if attr not in attr_ignore:
                try:
                    cmds.connectAttr(old_camera_shape + '.' + attr, self.new_camera[1] + '.' + attr)
                except:
                    continue

        # forcing attribute values
        cmds.setAttr(self.new_camera[0] + '.displayCameraFrustum', 1)
        cmds.setAttr(self.new_camera[0] + '.locatorScale', new_scale)

        timeline_start = cmds.playbackOptions(q=True, min=True)
        timeline_end = cmds.playbackOptions(q=True, max=True)

        # start baking
        cmds.bakeResults(self.new_camera[0], t=(timeline_start, timeline_end), simulation=True, sampleBy=1
                         , oversamplingRate=1
                         , disableImplicitControl=True
                         , preserveOutsideKeys=True
                         , sparseAnimCurveBake=False
                         , removeBakedAttributeFromLayer=False
                         , removeBakedAnimFromLayer=False
                         , bakeOnOverrideLayer=False
                         , minimizeRotation=True
                         , controlPoints=True
                         , shape=True)

        # deleting parent constraint from new camera
        cmds.delete(self.new_camera[0] + '_parentConstraint1')

        # to disconnect all attributes
        for attribute in new_camera_attrs:
            full_attr = self.new_camera[0] + '.' + attribute
            try:
                connection = None
                connection = cmds.listConnections(full_attr, c=True, p=True)
                if connection and "animCurve" not in cmds.nodeType(connection[1], inherited=True):
                    cmds.disconnectAttr(connection[1], connection[0])
            except:
                pass

        for attribute in new_camera_shape_attrs:
            full_attr = self.new_camera_shape + '.' + attribute
            try:
                connection = None
                connection = cmds.listConnections(full_attr, c=True, p=True)
                if connection and "animCurve" not in cmds.nodeType(connection[1], inherited=True):
                    cmds.disconnectAttr(connection[1], connection[0])
            except:
                pass

        # locking camera attributes
        self._lock_camera()

    def _lock_camera(self) -> None:
        cmds.setAttr(f'{self.new_camera_shape}.displayGateMask', 1)
        cmds.setAttr(f'{self.new_camera_shape}.displayResolution', 1)
        cmds.setAttr(f'{self.new_camera_shape}.displayGateMaskOpacity', 1)
        cmds.setAttr(f'{self.new_camera_shape}.displayGateMaskColor', 0, 0, 0)

        cmds.setAttr(f'{self.new_camera[0]}.overrideEnabled', 1)
        cmds.setAttr(f'{self.new_camera[0]}.overrideColor', 17)

        attrs_transform = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        attrs_shape = ['hfa', 'vfa', 'fl', 'lsr', 'fs', 'fd', 'sa', 'coi', 'cs',
                       'ff', 'ff', 'ffo', 'horizontalFilmOffset', 'verticalFilmOffset',
                       'se', 'soe', 'psc', 'filmTranslateH', 'filmTranslateV', 'horizontalRollPivot',
                       'verticalRollPivot', 'frv', 'fro', 'ptsc', 'dof']

        for attr in attrs_transform:
            cmds.setAttr(f'{self.new_camera[0]}.{attr}', lock=True)

        for attr in attrs_shape:
            cmds.setAttr(f'{self.new_camera_shape}.{attr}', lock=True)


class DuplicateCameraRun:

    def __init__(self):
        pass

    def duplicate_camera_run(self):
        DuplicateCameraLogic().duplicate_camera()