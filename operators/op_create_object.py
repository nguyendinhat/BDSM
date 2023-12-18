import bpy
from bpy.types import Operator
from bpy.props import EnumProperty
from ..context import items
from ..utils import tools

class BDSM_Create_Object(Operator):
    bl_idname = "wm.bdsm_create_object"
    bl_label = "BDSM Create Object"
    bl_description = "BDSM Create Object"
    bl_options = {'REGISTER', 'UNDO'}

    object_type: EnumProperty(
        items=(items.get_object_type),
        name="bdsm_prop_object_type")


    def execute(self, context):
        if 'builtin' in self.object_type:
            tools.set_active_tool(self.object_type)
            return {'FINISHED'}
        else:
            exec(self.object_type)

        return {'FINISHED'}
