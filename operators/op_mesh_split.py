import bpy
from bpy.types import Operator

class BDSM_Mesh_Split(Operator):
    bl_idname = 'mesh.bdsm_mesh_split'
    bl_label = 'BDSM Mesh Split'
    bl_description = 'BDSM Mesh Split/Break'
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)
    def execute(self, context):
        select_mode = bpy.context.tool_settings.mesh_select_mode
        if select_mode[0]:
            bpy.ops.mesh.edge_split(type='VERT')
            self.report({'INFO'}, 'An element was splited by VERTEX')
        if select_mode[1] and not select_mode[2]:
            bpy.ops.mesh.edge_split(type='EDGE')
            self.report({'INFO'}, 'An element was splited by EDGE')
        if select_mode[2] and not select_mode[1]:
            bpy.ops.mesh.split()
            self.report({'INFO'}, 'An element was splited by FACE')
        return {'FINISHED'}