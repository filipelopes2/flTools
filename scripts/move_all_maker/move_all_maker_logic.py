import maya.cmds as cmds
from startup.ui_functions import UiFunctions


class MoveAllMakerLogic:
    def __init__(self):
        self.selection = None
        self.obj_joint = None

    def create_move_all(self, moveall_type=None):
        self.selection = cmds.ls(sl=True)

        data_group_name = 'CTRLS'
        data_group = cmds.group(name=data_group_name, empty=True)
        try:
            ctrl_dict = {'moveall_0': {'size': 3, 'color': 6},
                         'moveall_1': {'size': 2.5, 'color': 13},
                         'moveall_2': {'size': 2, 'color': 17}}
            for ctrl in ctrl_dict:
                ctrl_circle = cmds.circle(name=ctrl, radius=ctrl_dict[ctrl]['size'], nr=(0, 1, 0), c=(0, 0, 0))
                ctrl_shape = cmds.listRelatives(ctrl_circle, shapes=True, fullPath=True)[0]
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f'{ctrl_shape}.overrideColor', ctrl_dict[ctrl]['color'])

            # creating joint ( already child of the last control )
            self.obj_joint = cmds.joint(p=(0, 0, 0))
            cmds.hide(self.obj_joint)

            keys_list = list(ctrl_dict)
            keys_list.reverse()
            keys_list.append(data_group)
            for i in range(0, len(keys_list)):
                child_name = keys_list[i]
                i += 1
                if i > len(keys_list) - 1: break
                parent_name = keys_list[i]
                cmds.parent(f'|{child_name}', f'|{parent_name}')

            print(f'moveall_type > {moveall_type}')
            if moveall_type == 1:
                self.set_constraints()
            elif moveall_type == 2:
                self.bind_skin()

            self.create_display_layers(data_group=data_group)

        except Exception as err:
            UiFunctions.error_message(title='ERROR',
                                      message=f'Error while creating controls!\n {err}',
                                      message_type='error')
            return False

        return True

    def create_display_layers(self, data_group=None) -> None:
        layers_dict = {'CTRL_lr': {'displayType': 0, 'color': 17},
                       'MESH_lr': {'displayType': 2, 'color': 6}
                       }
        for layer in layers_dict:
            if not cmds.objExists(layer):
                display_layer = cmds.createDisplayLayer(name=layer, empty=True)

                if layer == 'CTRL_lr':
                    cmds.editDisplayLayerMembers(display_layer, data_group, noRecurse=True)
                else:
                    cmds.editDisplayLayerMembers(display_layer, self.selection, noRecurse=True)

                for attr in layers_dict[layer]:
                    cmds.setAttr(f'{layer}.{attr}', layers_dict[layer][attr])

    def set_constraints(self) -> None:
        for obj in self.selection:
            cmds.parentConstraint(self.obj_joint, obj, maintainOffset=1, decompRotationToChild=1, weight=1)
            cmds.scaleConstraint(self.obj_joint, obj, maintainOffset=1, weight=1)

    def bind_skin(self) -> None:
        cmds.select(cl=True)
        for obj in self.selection:
            cmds.skinCluster(obj, self.obj_joint)