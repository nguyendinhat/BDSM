import bpy
from . import (
        primitive_box_add
    )
classes = [
    primitive_box_add.BDSM_Mesh_PrimitiveBoxAdd
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)


