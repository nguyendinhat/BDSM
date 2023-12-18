import bpy
from bpy.types import Operator

class OP_NONE(Operator):
    bl_idname = "object.op_none"
    bl_label = "OP_NONE"

    def execute(self, context):
        return {"FINISHED"}