import bpy
from . ui import draw
from . operators import extrude
from .ui.menus import extrude_menu

classes = [
    draw.BDSM_Draw_Labels_PunchIt,
    extrude.BDSM_Mesh_Extrude_PunchIt,
]

def register():
    bpy.types.VIEW3D_MT_edit_mesh_extrude.append(extrude_menu)
    for c in classes:
        bpy.utils.register_class(c)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_edit_mesh_extrude.remove(extrude_menu)
