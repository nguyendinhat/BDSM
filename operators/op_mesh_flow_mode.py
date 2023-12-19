import bpy
from bpy.types import Operator
class BDSM_Mesh_Flow_Mode(Operator):
    bl_idname = 'mesh.bdsm_mesh_flow_mode'
    bl_label = 'BDSM Mesh Flow Mode'
    bl_description = 'BDSM Mesh Flow Mode'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        select_mode = bpy.context.tool_settings.mesh_select_mode
        if select_mode[0]:
            # bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.bdsm_mesh_smooth_laplacian()
            self.report({'INFO'}, 'Set Flow: VERTEX +1')
        if select_mode[1] and not select_mode[2]:
            # bpy.ops.mesh.edge_split(type='EDGE')
            bpy.ops.mesh.bdsm_mesh_edge_flow()
            self.report({'INFO'}, 'Set Flow: EDGE +1')
        if select_mode[2] and not select_mode[1]:
            # bpy.ops.mesh.split()
            bpy.ops.mesh.bdsm_mesh_edge_flow()
            self.report({'INFO'}, 'Set Flow: FACE +1')
        return {'FINISHED'}
