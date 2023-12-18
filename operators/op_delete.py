import bpy , bmesh
from bpy.types import Operator
from bpy.props import BoolProperty

class BDSM_Delete(Operator):
    bl_idname = "view3d.bdsm_delete"
    bl_label = "BDSM Delete"
    bl_description = "BDSM Delete \nDeletes selection by selection mode (VERTEX, EDGE, FACE or OBJECT)"

    hierarchy: BoolProperty(
        name="Hierarchy",
        default= False,
    )

    expand: BoolProperty(
        name="Expand",
        default= False,
    )

    smart: BoolProperty(
        name="Smart",
        default= False,
    )

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH': return True
        if len(context.selected_objects) == 0: return False
        return context.object is not None

    def execute(self, context):
        if context.mode == "EDIT_MESH":
            if self.smart:
                b_mesh= bmesh.from_edit_mesh(context.object.data)
                floaters = [i for i in b_mesh.verts if i.select and not i.link_faces]
                if floaters:
                    for v in floaters:
                        b_mesh.verts.remove(v)
                    bmesh.update_edit_mesh(context.object.data)
            select_mode = context.tool_settings.mesh_select_mode
            if select_mode[0]:
                if self.smart:
                    bpy.ops.mesh.bdsm_dissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='VERT')
            elif select_mode[1]:
                if self.smart:
                    bpy.ops.mesh.bdsm_dissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='EDGE')
            elif select_mode[2]:
                if self.expand:
                    bpy.ops.view3d.bdsm_copy('INVOKE_DEFAULT', True, mode="CUT")
                else:
                    bpy.ops.mesh.delete(type='FACE')

        elif context.mode == "OBJECT":
            object_selected = context.selected_objects[:]
            if self.hierarchy:
                for object in object_selected:
                    for child in object.children:
                        object_selected.append(child)
            object_selected = list(set(object_selected))

            if self.expand:
                for item in object_selected:
                    item.select_set(True)
                bpy.ops.view3d.bdsm_copy('INVOKE_DEFAULT', True, mode="CUT")
            else:
                for item in object_selected:
                    bpy.data.objects.remove(item, do_unlink=True)

        elif context.object.type == "GPENCIL" and context.mode != "OBJECT":
            bpy.ops.gpencil.delete(type='POINTS')

        elif context.object.type == "CURVE" and context.mode != "OBJECT":
            bpy.ops.curve.delete(type='VERT')

        return {'FINISHED'}


class BDSM_Dissolve(Operator):
    bl_idname = "mesh.bdsm_dissolve"
    bl_label = "BDSM Dissolve"
    bl_description = "Dissolves selection by selection mode (VERTEX, EDGE or POLY)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH': return True
        if len(context.selected_objects) == 0: return False
        return context.object is not None

    def execute(self, context):
        if context.object.type == 'MESH':
            select_mode = context.tool_settings.mesh_select_mode[:]
            if select_mode[0]:
                bpy.ops.mesh.dissolve_verts('INVOKE_DEFAULT', True)
            elif select_mode[1]:
                bpy.ops.mesh.dissolve_edges('INVOKE_DEFAULT', True)
            elif select_mode[2]:
                bpy.ops.mesh.dissolve_faces('INVOKE_DEFAULT', True)

        elif context.object.type == 'GPENCIL':
            bpy.ops.gpencil.dissolve(type='POINTS')

        elif context.object.type == 'CURVE':
            bpy.ops.curve.dissolve_verts()

        return {'FINISHED'}
