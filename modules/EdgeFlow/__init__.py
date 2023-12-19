#"https://github.com/BenjaminSauder/EdgeFlow" ,
import bpy
from . import (
        op_set_edge_flow,
        op_set_edge_linear,
        op_set_edge_curve,
        op_set_vertex_curve,
    )
# stuff which needs to be registered in blender
classes = [
    op_set_edge_flow.BDSM_Mesh_Edge_Flow,
    op_set_edge_linear.BDSM_Mesh_Edge_Linear,
    op_set_edge_curve.BDSM_Mesh_Edge_Curver,
    op_set_vertex_curve.BDSM_Mesh_Vertex_Curve,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)


