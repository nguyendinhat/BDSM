import bpy, bmesh
from bpy.types import Operator


class BDSM_SelectBorderEdges(Operator):
    bl_idname = 'mesh.bdsm_select_border_edges'
    bl_label = 'BDSM Select Border Edges'
    bl_description = 'Select Boundary edges border edges'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        active_obj = bpy.context.active_object
        if active_obj is None:
            active_obj = context.object
        b_mesh = bmesh.from_edit_mesh(active_obj.data)

        obj_verts = b_mesh.verts
        obj_edges = b_mesh.edges
        obj_faces = b_mesh.faces

        selected_verts = [vert for vert in obj_verts if vert.select]
        selected_edges = [edge for edge in obj_edges if edge.select]
        selected_faces = [face for face in obj_faces if face.select]
        b_mesh.select_history.clear()
        b_mesh.free()




        if len(obj_faces) == len(selected_faces) or len(obj_edges) == len(selected_edges) or len(obj_verts) == len(selected_verts) or len(selected_verts) == 0:
            bpy.ops.mesh.select_all(action='SELECT')
        elif len(selected_verts) == 1 or len(selected_edges) == 0:
            bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        else:
            bpy.ops.mesh.loop_to_region(select_bigger=False)
        #border select
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.select_mode(type='EDGE')
        return {'FINISHED'}