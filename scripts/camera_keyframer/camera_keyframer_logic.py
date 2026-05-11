import maya.cmds as cmds


class CamKeyframer_Logic:

    def __init__(self):
        pass

    @staticmethod
    def focal_length_curve(camera_name=None) -> None:
        camera_shape = cmds.listRelatives(camera_name, shapes=True)[0]
        cmds.keyTangent(f'{camera_shape}.focalLength', inTangentType='stepnext')

    @staticmethod
    def set_keys(camera_name=None) -> None:
        camera_shape = cmds.listRelatives(camera_name, shapes=True)[0]
        camera_aim = f'{camera_name}_aim' if cmds.objExists(f'{camera_name}_aim') else None
        translates = ['translateX', 'translateY', 'translateZ']
        for attribute in translates:
            cmds.setKeyframe(camera_name, at=attribute)
            if camera_aim:
                cmds.setKeyframe(camera_aim, at=attribute)
        cmds.setKeyframe(camera_shape, at='focalLength')
