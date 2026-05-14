import maya.cmds as cmds
import maya.mel as mel


from startup.ui_functions import UiFunctions


__tool_name__ = 'Yeti Tools'
__tool_class__ = 'YetiToolsLogic'
__tool_function__ = ''
__tool_submenu__ = {'Yeti Tools':
                        {'Initial Graph': 'initial_graph_nogroom',
                         'Initial Graph - With Groom': 'initial_graph_groom'
                         }
                    }


class YetiToolsLogic:
    def __init__(self):
        pass

    def initial_graph_groom(self, *args):
        self._yeti_initial(creation_type='with_groom')

    def initial_graph_nogroom(self, *args):
        self._yeti_initial(creation_type='')

    def _check_yeti(self) -> bool:
        """
        Checks if the plugin is loaded and if there is license available
        :return: True/False
        """
        # print(' check_yeti '.center(50, '='))
        if not UiFunctions.check_plugin('yeti', force_load=True):
            UiFunctions.error_message(title=__tool_name__, message='Yeti plugin NOT loaded.',
                                      message_type='error')
            return False
        else:
            yeti_license = mel.eval('pgYetiCommand -licenseAvailable;')
            if yeti_license != 1:
                UiFunctions.error_message(title=__tool_name__, message='No Yeti license available.',
                                          message_type='error')
                return False
        return True

    def _create_texture_references(self, selection) -> None:
        for obj in selection:
            obj_shape = cmds.listRelatives(obj, shapes=True)[0]
            reference_connection = cmds.listConnections(f'{obj_shape}.referenceObject')
            # if there's no reference connected, create one and hide it
            if not reference_connection:
                cmds.select(obj, replace=True)
                mel.eval("CreateTextureReferenceObject;")
                reference_obj = cmds.listConnections(f'{obj_shape}.referenceObject')[0]
                cmds.hide(reference_obj)

    def _create_graph(self, yeti_node_shape):
        # creating nodes
        # node name: [type, input]
        nodes_dict = {"import_objects": ["import", None],
                      "scatter": ["scatter", "import_objects"],
                      "grow": ["grow", "scatter"],
                      "width": ["width", "grow"]}
        for node_name in nodes_dict:
            node_type = nodes_dict[node_name][0]
            node_input = nodes_dict[node_name][1]

            # create node
            create_cmd = f'pgYetiGraph -create -type "{node_type}" {yeti_node_shape};'
            create_node = mel.eval(create_cmd)

            # renaming the node
            rename_node = mel.eval(f'pgYetiGraph -node {create_node} -rename "{node_name}" {yeti_node_shape};')

            # conecting the input of the node
            if node_input:
                mel.eval(f'pgYetiGraph -node "{nodes_dict[node_name][1]}" -connect "{node_name}" 0 {yeti_node_shape};')

        # set root node
        mel.eval(f'pgYetiGraph -setRootNode "{list(nodes_dict.keys())[-1]}" {yeti_node_shape};')

    def _create_yeti_node(self, obj) -> str:
        obj_shape = cmds.listRelatives(obj, shapes=True)[0]
        new_node_shape = mel.eval('pgYetiCreate();')
        cmds.connectAttr(f'{obj_shape}.worldMesh', f'{new_node_shape}.inputGeometry', nextAvailable=True)
        self._create_graph(new_node_shape)

        return new_node_shape

    def _create_groom(self, obj, yeti_node_shape):
        # create groom on mesh
        cmds.select(obj, replace=True)
        mel.eval('pgYetiCreateGroomOnMesh();')

        # adding the groom to the yeti node
        obj_shape = cmds.listRelatives(obj, shapes=True)[0]
        groom_node = cmds.listConnections(obj_shape, type='pgYetiGroom')[0]
        mel.eval(f'pgYetiAddGroom("{groom_node}", "{yeti_node_shape}");')

        self._create_groom_nodes(yeti_node_shape)

    def _create_groom_nodes(self, yeti_node_shape):
        # create nodes
        comb_node = mel.eval(f'pgYetiGraph -create -type "comb" {yeti_node_shape};')
        import_node = mel.eval(f'pgYetiGraph -create -type "import" {yeti_node_shape};')

        # renaming nodes
        mel.eval(f'pgYetiGraph -node {comb_node} -rename "comb" {yeti_node_shape};')
        mel.eval(f'pgYetiGraph -node {import_node} -rename "import_groom" {yeti_node_shape};')

        # connecting input and output
        mel.eval(f'pgYetiGraph -node "grow" -connect "comb" 0 {yeti_node_shape};')
        mel.eval(f'pgYetiGraph -node "comb" -connect "width" 0 {yeti_node_shape};')
        mel.eval(f'pgYetiGraph -node "import_groom" -connect "grow" 1 {yeti_node_shape};')
        mel.eval(f'pgYetiGraph -node "import_groom" -connect "comb" 1 {yeti_node_shape};')

        # set import node parameters
        mel.eval(f'pgYetiGraph -node "import_groom" -param "type" -setParamValueScalar 1 {yeti_node_shape};')

    def _yeti_initial(self, creation_type=None) -> None:

        selection = cmds.ls(sl=True)
        if not selection:
            UiFunctions.error_message(title=__tool_name__,
                                      message='No geometry selected.')
            return

        if self._check_yeti():
            self._create_texture_references(selection)

            # creating yeti node and initial graph
            for obj in selection:
                yeti_node = self._create_yeti_node(obj)

                # creating groom and adding nodes on the graph
                if creation_type == 'with_groom':
                    self._create_groom(obj, yeti_node)