import bpy
from .operators import punnchit, op_test
from .interface import draw
from .interface.menus import extrude_menu, menu_func

classes = [
    draw.BDSM_Draw_Labels_PunchIt,
    punnchit.BDSM_Mesh_Extrude_PunchIt,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
