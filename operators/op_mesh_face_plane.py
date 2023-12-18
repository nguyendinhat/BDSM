import bpy,bmesh
from bpy.types import Operator
from ..utils.ngons import *


class BDSM_Mesh_Face_Plane(Operator):
    bl_idname = 'mesh.bdsm_mesh_face_plane'
    bl_label = 'BDSM Mesh Face Plane'
    bl_description = 'BDSM Mesh Face Plane \nStraighten faces by projecting all the vertices on the plane created by the 3 selected verts OR straighten using the normal of the selected face if using faces for straightening'
    bl_options = {'REGISTER', 'UNDO'}

    straighten_active_face: bpy.props.BoolProperty(
        name='Also straighten active face',
        description='Only has an effect when straightening using multiple faces',
        default=True
    )

    straighten_mode: bpy.props.EnumProperty(
        name='Straighten mode',
        description='Straighten mode for use when straightening faces',
        items=[
            ('simple', 'Simple', 'Just project the vertices on the plane'),
            ('edges', 'Along edges', 'Move the vertices along edges to straighten faces')
        ],
        default='simple'
    )

    merge_faces: bpy.props.BoolProperty(
        name='Merge faces after straightening',
        description='Only has an effect when straightening using multiple faces: dissolve inner edges',
        default=False
    )

    edge_distance_treshold: bpy.props.FloatProperty(
        name='Edge choosing distance treshold',
        description='The maximum distance difference between offset verts along edges from their original position: if below treshold then more than all relevant edges will be used as combined offsetting dir (only applicable when moving along edges)',
        subtype='DISTANCE',
        default=0.1,
        min=0
    )
    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        obj = context.active_object
        return (obj and obj.type == 'MESH' and
                obj.mode == 'EDIT')
    # TODO: make it so that result is not insane when selecting two perpendicular planes and moving along edges
    def execute(self, context):
        obj = bpy.context.object

        bm = get_bmesh(obj, True, True, True)
        selected_verts = [v for v in bm.verts if v.select]
        selected_faces = [f for f in bm.faces if f.select]

        if len(selected_faces) > 1:
            ref_face = bm.faces.active
            verts_to_straighten = selected_verts if self.straighten_active_face else [v for v in selected_verts if v not in ref_face.verts]
            plane_origin = ref_face.calc_center_median()
            plane_normal = ref_face.normal
            for v in verts_to_straighten:
                v.co = calculate_straightened_point(v, plane_origin, plane_normal, self.straighten_mode, selected_verts, self.edge_distance_treshold)

        elif len(selected_faces) == 1 and len(selected_verts) > 3:  # no need to straighten triangles
            ref_face = selected_faces[0]
            plane_origin = ref_face.calc_center_median()
            plane_normal = ref_face.normal
            for v in selected_verts:
                v.co = calculate_straightened_point(v, plane_origin, plane_normal, self.straighten_mode, selected_verts, self.edge_distance_treshold)

        elif len(selected_verts) == 3:
            if collinear_three_points(selected_verts[0].co, selected_verts[1].co, selected_verts[2].co):
                show_message('Invalid selection. Selected collinear points.')
                free_bmesh(obj, bm)
                return {'CANCELLED'}

            ref_face = None
            for f in bm.faces:
                if all([v in f.verts for v in selected_verts]):
                    ref_face = f
                    break

            if ref_face is None:
                show_message('Invalid selection!')
                free_bmesh(obj, bm)
                return {'CANCELLED'}

            selected_faces = [ref_face]
            median_point = (selected_verts[0].co + selected_verts[1].co + selected_verts[2].co) / 3
            normal = get_selection_normal([x.co for x in selected_verts], [x.co for x in selected_verts])
            for v in ref_face.verts:
                v.co = calculate_straightened_point(v, median_point, normal, self.straighten_mode, ref_face.verts, self.edge_distance_treshold)

        else:
            show_message('Invalid selection!')
            free_bmesh(obj, bm)
            return {'CANCELLED'}

        for f in selected_faces:
            f.normal_update()

        if self.merge_faces and len(selected_faces) > 1:
            new_face = bmesh.ops.contextual_create(bm, geom=list(set(flattened([f.verts for f in selected_faces]))))['faces'][0]
            new_face.select = True
            new_face.normal_update()
            bmesh.ops.delete(bm, geom=selected_faces, context='FACES')

        update_bmesh(obj, bm)
        free_bmesh(obj, bm)

        return {'FINISHED'}
