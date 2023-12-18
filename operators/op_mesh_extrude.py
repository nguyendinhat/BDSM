import bpy
from bpy.types import Operator

class BDSM_Mesh_Extrude(Operator):
    bl_idname = 'mesh.bdsm_mesh_extrude'
    bl_label = 'BDSM Mesh Extrude'
    bl_description = 'BDSM Mesh Extrude'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.bdsm_extrude(context)
        return self.execute(context)

    def bdsm_extrude(self, context):
        props = context.window_manager.BDSM_Context
        if context.mode == 'OBJECT':
            if len(context.selected_objects) == 0:
                self.report({'ERROR_INVALID_CONTEXT'},'Extrude: Nothing object selected')
                return {'FINISHED'}
            else:
                props.topbar_enums = 'EDIT_TAB'
                props.selection_enums = 'SELECT_FACE'
        elif context.mode == 'EDIT_MESH':
            context.object.update_from_editmode()
            object_selected = [object for object in context.selected_objects if object.type == 'MESH']
            if not object_selected:
                object_selected.append(context.object)

            verts_selected = []
            for object in object_selected:
                verts_selected.extend([vert for vert in object.data.vertices if vert.select])

            if len(verts_selected)<1:
                self.report({'ERROR_INVALID_CONTEXT'},'Extrude: Nothing selected')
                return {'FINISHED'}
            props.topbar_enums = 'EDIT_TAB'
            sel_mode = context.tool_settings.mesh_select_mode[:]
            if sel_mode[0]:
                bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT', True)
            elif sel_mode[1]:
                bpy.ops.mesh.extrude_edges_move('INVOKE_DEFAULT')
            elif sel_mode[2]:
                self.extrude_mode(props.extrude_mode)
        elif context.object.type == 'CURVE':
            bpy.ops.curve.extrude_move('INVOKE_DEFAULT')
        elif context.object.type == 'GPENCIL':
            bpy.ops.gpencil.extrude_move('INVOKE_DEFAULT')

    def extrude_mode(self,mode):
        #todo: EXTRUDE_ALONG_NORMAL
        if mode == 'EXTRUDE_ALONG_NORMAL':
            return bpy.ops.view3d.edit_mesh_extrude_move_shrink_fatten()

        #todo: EXTRUDE_INDIVIDUAL
        elif mode == 'EXTRUDE_INDIVIDUAL':
            return bpy.ops.view3d.edit_mesh_extrude_individual_move()

        #todo: EXTRUDE_MANIFOLD
        elif mode == 'EXTRUDE_MANIFOLD':
            return bpy.ops.view3d.edit_mesh_extrude_manifold_normal()

        #todo: EXTRUDE_REGION
        elif mode == 'EXTRUDE_REGION':
            return bpy.ops.view3d.edit_mesh_extrude_move_normal()
        return {'FINISHED'}




