import maya.cmds as cmds
import random as random
import colorsys

from startup.ui_functions import UiFunctions


__tool_name__ = 'Random Color Shaders'
__tool_class__ = 'RandomShadersLogic'
__tool_function__ = 'set_random_shaders'
__tool_submenu__ = 'Look and Render'


class RandomShadersLogic:

    @staticmethod
    def set_random_shaders(*args) -> None:
        selection = cmds.ls(sl=True)
        if not selection:
            UiFunctions.error_message(title=__tool_name__,
                                      message='No geometry selected.')
            return

        if UiFunctions.check_plugin(plugin='arnold'):
            for obj in selection:
                h = random.uniform(50, 360)
                s = random.uniform(0.6, 0.8)
                v = random.uniform(0.3, 0.5)
                r, g, b = colorsys.hsv_to_rgb(h, s, v)

                object_name = obj.split(':')[-1]
                material_name = f'{object_name}_MAT'
                shading_group_name = f'{object_name}_SG'

                material = cmds.shadingNode('aiStandardSurface', name=material_name, asShader=True)
                shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shading_group_name)

                cmds.setAttr(f'{material}.baseColor', r, g, b, type='double3')
                cmds.connectAttr(f'{material}.outColor', f'{shading_group}.surfaceShader')
                cmds.sets(obj, edit=True, forceElement=shading_group)
