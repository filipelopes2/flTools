import maya.cmds as cmds
from maya.api import OpenMaya as om
from pxr import Usd, UsdGeom, Vt, Sdf
import os

from startup.ui_functions import UiFunctions


class OutlinerNode:

    def __init__(self, node_name: str = None, prim_path: str = None, prim_type: str = None,
                 scene_path: str = None) -> None:
        self.node_name = node_name
        self.prim_path = prim_path
        self.prim_type = prim_type
        self.scene_path = scene_path


class UsdToolsLogic:

    def __init__(self):
        self.variants_dict = None
        self.asset_name = None
        self.base_folder = None
        self.stage = None

    def export_asset(self) -> None:
        # save each variant
        for variant in self.variants_dict:
            self._create_stage()
            self._create_all_prims(nodes_list=self._fetch_objs(variant_root=self.variants_dict[variant],
                                                               variant_name=variant))
            self._save_stage(usd_name=variant)

        # create usd to reference
        self._create_stage()
        mesh_root  = OutlinerNode(node_name='MESH', prim_path=f'/MESH', prim_type='xform')
        self._create_all_prims(nodes_list=[mesh_root])
        mesh_prim = self.stage.GetPrimAtPath(f'/MESH')
        self.stage.SetDefaultPrim(mesh_prim)

        # create variant sets
        variant_set_name = 'resolutionSet'
        variant_set = mesh_prim.GetVariantSets().AddVariantSet(variant_set_name)

        # referencing each variant
        for variant in self.variants_dict:
            usd_filename = f'{variant}.usda'
            root_path = os.path.join(self.base_folder, self.asset_name, 'variants', usd_filename)
            variant_set.AddVariant(variant)
            variant_set.SetVariantSelection(variant)
            with variant_set.GetVariantEditContext():
                geo_path = f'/MESH/geo'
                geo_prim = OutlinerNode(node_name='geo', prim_path=geo_path, prim_type='scope')
                self._create_all_prims(nodes_list=[geo_prim])
                geo_prim = self.stage.GetPrimAtPath(geo_path)
                geo_prim.GetReferences().AddReference(root_path, '/MESH/geo')

        self._save_stage(usd_name=self.asset_name, variant_usd=False)

        UiFunctions.error_message(title='USD Export',
                                  message='Asset exported successfully!',
                                  message_type='info')

    def _fetch_objs(self, variant_root: str = None, variant_name: str = None) -> list:
        all_objects = cmds.listRelatives(variant_root, allDescendents=True, fullPath=True,
                                         type='transform', noIntermediate=True)
        all_objects.sort(key=len, reverse=False)
        all_objects.insert(0, variant_root)
        nodes_list = []
        for obj in all_objects:
            node_name = obj.split('|')[-1]
            prim_path = obj.replace('|', '/')
            prim_path = prim_path.replace(f'/_var_{variant_name}', '').replace(f'/{self.asset_name}', '')
            prim_type = self._get_prim_type(obj)
            node = OutlinerNode(node_name=node_name, prim_path=prim_path, prim_type=prim_type, scene_path=obj)
            nodes_list.append(node)

        return nodes_list

    def _get_prim_type(self, obj: str = None) -> str:
        obj_shape = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not obj_shape:
            if obj == '|MESH':
                prim_type = 'xform'
            else:
                prim_type = 'scope'
            return prim_type
        else:
            obj_type = cmds.objectType(obj_shape[0])
            if obj_type == 'locator':
                prim_type = 'scope'
            else:
                prim_type = 'mesh'
            return prim_type

    def _create_stage(self) -> None:
        self.stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageMetersPerUnit(self.stage, UsdGeom.LinearUnits.centimeters)
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y)

    def _save_stage(self, usd_name: str = None, variant_usd: bool = True) -> None:
        root_path = os.path.join(self.base_folder, self.asset_name)
        if variant_usd:
            root_path = os.path.join(root_path, 'variants')

        usd_filename = f'{usd_name}.usda'
        usd_path = os.path.join(root_path, usd_filename)

        print(f'{self.stage.GetRootLayer().ExportToString()}')
        self.stage.GetRootLayer().Export(usd_path)
        print(f'{usd_path = }')

    def _create_all_prims(self, nodes_list: list) -> None:
        for node in nodes_list:
            self._create_prim(prim_type=node.prim_type, prim_path=node.prim_path, scene_path=node.scene_path)

    def _create_prim(self, prim_type: str = None, prim_path: str = None, scene_path: str = None) -> None:
        if prim_type == 'xform':
            UsdGeom.Xform.Define(self.stage, prim_path)
        elif prim_type == 'scope':
            UsdGeom.Scope.Define(self.stage, prim_path)
        elif prim_type == 'mesh':
            prim = UsdGeom.Mesh.Define(self.stage, prim_path)
            self._fill_geometry(prim=prim, scene_path=scene_path)

    def _fill_geometry(self, prim: UsdGeom.Mesh = None, scene_path: str = None) -> None:

        om_selection = om.MSelectionList()
        om_selection.add(scene_path)
        dag_path = om_selection.getDagPath(0)

        # mesh points
        mesh_fn = om.MFnMesh(dag_path)
        mesh_points = mesh_fn.getPoints(om.MSpace.kWorld)
        usd_points = Vt.Vec3fArray([(point.x, point.y, point.z) for point in mesh_points])

        # mesh faces
        face_vertex_counts, face_vertex_indices = [], []
        for face_id in range(mesh_fn.numPolygons):
            vertex_ids = mesh_fn.getPolygonVertices(face_id)
            face_vertex_counts.append(len(vertex_ids))
            face_vertex_indices.extend(vertex_ids)

        # convert to USD array
        face_vertex_counts = Vt.IntArray(face_vertex_counts)
        face_vertex_indices = Vt.IntArray(face_vertex_indices)

        # assign to USD prim
        prim.GetPointsAttr().Set(usd_points)
        prim.GetFaceVertexCountsAttr().Set(face_vertex_counts)
        prim.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

        # add UV Sets
        uv_sets = mesh_fn.getUVSetNames()
        for uv_set in uv_sets:
            u_array, v_array = mesh_fn.getUVs(uv_set)

            # to match the absolute face-vertex topology
            # loop over every vertex of every face and query the uv
            usd_uv_indices = []
            poly_iter = om.MItMeshPolygon(dag_path)
            while not poly_iter.isDone():
                for local_idx in range(poly_iter.polygonVertexCount()):
                    try:
                        uv_idx = poly_iter.getUVIndex(local_idx, uv_set)
                        usd_uv_indices.append(uv_idx)
                    except RuntimeError:
                        usd_uv_indices.append(0)
                poly_iter.next()

            usd_uv_values = [(u, v) for u, v in zip(u_array, v_array)]

            prim_var = UsdGeom.PrimvarsAPI(prim)
            st_primvar = prim_var.CreatePrimvar(uv_set, Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
            st_primvar.Set(Vt.Vec2dArray(usd_uv_values))
            st_primvar.SetIndices(Vt.IntArray(usd_uv_indices))
