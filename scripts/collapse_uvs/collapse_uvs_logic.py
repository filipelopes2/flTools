import maya.cmds as cmds
import maya.mel as mel

from startup.ui_functions import UiFunctions

__tool_name__ = 'Collapse UVs'
__tool_class__ = 'CollapseUvsLogic'
__tool_function__ = 'collapse_uv_sets'
__tool_submenu__ = 'Modeling'


class CollapseUvsLogic:

    def __init__(self):
        pass

    def collapse_uv_sets(self) -> None:
        """
        Combines UVs from different UV Sets into one UV Set called map1
        """

        selection = cmds.ls(sl=True)
        if not selection:
            UiFunctions.error_message(title=__tool_name__,
                                      message='No geometry selected.')
            return

        for geometry in selection:
            uvs = cmds.polyUVSet(geometry, query=True, allUVSetsIndices=True)
            for uv in uvs:
                set_name = cmds.getAttr(f'{geometry}.uvSet[{uv}].uvSetName')
                if set_name != 'map1':
                    cmds.polyUVSet(geometry, uvs=set_name,currentUVSet=True, edit=True)
                    cmds.selectMode(co=True)
                    cmds.selectType(puv=True)
                    mel.eval('SelectAll;')
                    vertex_selection = cmds.ls(sl=True)
                    cmds.polyCopyUV(vertex_selection, uvi=set_name, uvs='map1')
                    cmds.polyUVSet(geometry, uvs=set_name,currentUVSet=True, edit=True)
                    cmds.polyUVSet(d=True)