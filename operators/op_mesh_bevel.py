import bpy
from bpy.types import Operator

class BDSM_Mesh_Bevel(Operator):
    bl_idname = 'mesh.bdsm_mesh_bevel'
    bl_label = 'BDSM Mesh Bevel'
    bl_description = 'BDSM Mesh Bevel'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        toolSettings = bpy.context.tool_settings
        if toolSettings.mesh_select_mode[0]:
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')
        else:
            bpy.ops.mesh.bevel('INVOKE_DEFAULT')
        return {'FINISHED'}