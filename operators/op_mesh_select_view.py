import bpy, mathutils
from bpy.types import Operator
from ..utils.ngons import *


class BDSM_Mesh_Select_View(Operator):
    bl_idname = 'mesh.bdsm_mesh_select_view'
    bl_label = 'BDSM Mesh Select View'
    bl_description = 'BDSM Mesh Select View \nAligns view to the current selection - much better than the alternatives in vanilla blender. Prevents any roll'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        obj = context.active_object
        return (obj and obj.type == 'MESH' and
                obj.mode == 'EDIT')
    def execute(self, context):
        obj = bpy.context.object
        bm = get_bmesh(obj)

        # calculate xyz vectors for our perpendicular view
        try:
            verts = [v for v in bm.verts if v.select]
            z_vector = get_selection_normal([v.co for v in verts], [v.normal for v in verts])
        except:
            show_message('Select 3+ vertices to align to...')
            free_bmesh(obj, bm)
            return {'CANCELLED'}

        free_bmesh(obj, bm)
        up_vector = mathutils.Vector((0, 0, 1))
        forward_vector = mathutils.Vector((0, -1, 0))

        # avoid cross product of the same vectors
        if abs(z_vector.dot(up_vector) + 1) <= 0.0001: # if dot product is -1 (facing downwards) use negative forward so no div by 0 and no upside-down
            x_vector = z_vector.cross(-forward_vector)
        elif abs(z_vector.dot(up_vector) - 1) <= 0.0001: # if dot product is 1 (facing upwards) use positive forward so no div by 0 and no upside-down
            x_vector = z_vector.cross(forward_vector)
        else: # vectors are different, we're fine
            x_vector = up_vector.cross(z_vector)

        y_vector = z_vector.cross(x_vector)

        x_vector.normalize()
        y_vector.normalize()
        z_vector.normalize()

        # # ALIGN VIEW TO SELECTED
        view_matrix = mathutils.Matrix(((x_vector[0], x_vector[1], x_vector[2], 0),
                                        (y_vector[0], y_vector[1], y_vector[2], 0),
                                        (z_vector[0], z_vector[1], z_vector[2], 0),
                                        (0,                     0,           0, 1)))

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                rv3d = area.spaces[0].region_3d
                if rv3d is not None:
                    rv3d.view_matrix = view_matrix
                    bpy.ops.view3d.view_selected()

        return {'FINISHED'}
