import bpy
from .operators import punnchit, normals
from .interface import draw

classes = [
    draw.BDSM_Draw_Labels_PunchIt,
    punnchit.BDSM_Mesh_Extrude_PunchIt,

    normals.BDSM_Mesh_Face_Normal_Clear,
    normals.BDSM_Mesh_Face_Normal_Flatten,
    normals.BDSM_Mesh_Face_Normal_Straighten,
    normals.BDSM_Mesh_Face_Normal_Transfer,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
