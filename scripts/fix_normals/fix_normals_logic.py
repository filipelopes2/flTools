import maya.cmds as cmds
import maya.OpenMaya as om

from startup.ui_functions import UiFunctions


__tool_name__ = 'Fix Normals'
__tool_class__ = 'FixNormals'
__tool_function__ = 'check_normals_direction'
__tool_submenu__ = 'Modeling'


class FixNormals:

    def __init__(self):
        pass

    @staticmethod
    def _check_selection(selection=None) -> bool:
        if len(selection) < 1:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select one polygonal object!')
            return False

        if len(selection) > 1:
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select only one polygonal object!')
            return False

        selection = selection[0]
        shape = cmds.listRelatives(selection, s=True)[0]
        object_type = cmds.objectType(shape)
        if object_type != 'mesh':
            UiFunctions.error_message(title=__tool_name__,
                                      message='Select one polygonal object!')
            return False

        return True

    def check_normals_direction(self) -> None:
        """
        Checks the direction of each face on a given polygonal object and corrects reverted normals
        """

        selection = cmds.ls(sl=True)
        if not FixNormals._check_selection(selection=selection):
            return
        else:
            obj = selection[0]

        # get DAG path
        sel = om.MSelectionList()
        sel.add(obj)
        dagPath = om.MDagPath()
        sel.getDagPath(0, dagPath)
        fnMesh = om.MFnMesh(dagPath)

        # get bounding box center
        fnDag = om.MFnDagNode(dagPath)
        bbox = fnDag.boundingBox()
        center = bbox.center()

        inward_count = 0
        inward_list = []
        outward_count = 0
        outward_list = []

        # checking each face
        for i in range(fnMesh.numPolygons()):
            vertex_ids = om.MIntArray()
            fnMesh.getPolygonVertices(i, vertex_ids)

            # compute face center
            face_center = om.MPoint(0.0, 0.0, 0.0)
            for vid in vertex_ids:
                p = om.MPoint()
                fnMesh.getPoint(vid, p, om.MSpace.kWorld)
                face_center.x += p.x
                face_center.y += p.y
                face_center.z += p.z

            if vertex_ids.length() > 0:
                face_center.x /= vertex_ids.length()
                face_center.y /= vertex_ids.length()
                face_center.z /= vertex_ids.length()

            # vector from object center to face center
            dir_vec = om.MVector(face_center - center).normal()

            # face normal
            normal = om.MVector()
            fnMesh.getPolygonNormal(i, normal, om.MSpace.kWorld)
            normal.normalize()

            # dot product
            dot = normal * dir_vec
            if dot < 0:
                inward_count += 1
                inward_list.append(i)
            else:
                outward_count += 1
                outward_list.append(i)

        if outward_count > inward_count:
            for face in inward_list:
                cmds.polyNormal(f'{obj}.f[{face}]', nm=0, unm=0)
        else:
            for i in range(fnMesh.numPolygons()):
                if i not in outward_list:
                    cmds.polyNormal(f'{obj}.f[{i}]', nm=0, unm=0)

        cmds.polyAverageNormal(prenormalize=1, allowZeroNormal=0, postnormalize=0, distance=0.1)

