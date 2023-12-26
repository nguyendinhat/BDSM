import bpy
from .operators import punnchit, op_test
from .interface import draw
from .interface.menus import extrude_menu, menu_func

classes = [
    op_test.BDSM_DrawTest,
    draw.BDSM_Draw_Labels_PunchIt,
    punnchit.BDSM_Mesh_Extrude_PunchIt,
]

def register():
    bpy.types.VIEW3D_MT_edit_mesh_extrude.append(extrude_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_edit_mesh_extrude.remove(extrude_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
