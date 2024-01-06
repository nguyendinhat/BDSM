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
                # bpy.ops.mesh.extrude_edges_move('INVOKE_DEFAULT')
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



    # MESH_OT_extrude_edges_indiv={"use_normal_flip":False, "mirror":False}, 
    # TRANSFORM_OT_translate={"value":(0, 0, 0.673377), 
    # "orient_type":'GLOBAL', 
    # "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
    # "orient_matrix_type":'GLOBAL', 
    # "constraint_axis":(False, False, True), 
    # "mirror":False, "use_proportional_edit":False, 
    # "proportional_edit_falloff":'SMOOTH', "proportional_size":1, 
    # "use_proportional_connected":False, 
    # "use_proportional_projected":False, 
    # "snap":False, "snap_elements":{'INCREMENT'}, 
    # "use_snap_project":False, "snap_target":'CLOSEST', 
    # "use_snap_self":True, 
    # "use_snap_edit":True, 
    # "use_snap_nonedit":True, 
    # "use_snap_selectable":False, 
    # "snap_point":(0, 0, 0), 
    # "snap_align":False, 
    # "snap_normal":(0, 0, 0), "gpencil_strokes":False, 
    # "cursor_transform":False, "texture_space":False, 
    # "remove_on_cancel":False, 
    # "use_duplicated_keyframes":False, 
    # "view2d_edge_pan":False, 
    # "release_confirm":False, 
    # "use_accurate":False, 
    # "alt_navigation":False, 
    # "use_automerge_and_split":False})

# bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={
#     "use_normal_flip":False, 
#     "use_dissolve_ortho_edges":False, 
#     "mirror":False}, 
#     TRANSFORM_OT_translate={
#         "value":(0, 0, 4.06618), 
#         "orient_type":'NORMAL', 
#         "orient_matrix":((0, 0, -1), (1, 0, 0), (0, -1, 0)), 
#         "orient_matrix_type":'NORMAL', 
#         "constraint_axis":(False, False, True), 
#         "mirror":False, "use_proportional_edit":False, 
#         "proportional_edit_falloff":'SMOOTH', 
#         "proportional_size":1, 
#         "use_proportional_connected":False, 
#         "use_proportional_projected":False, "snap":False, 
#         "snap_elements":{'INCREMENT'}, 
#         "use_snap_project":False, 
#         "snap_target":'CLOSEST', 
#         "use_snap_self":True, "use_snap_edit":True, 
#         "use_snap_nonedit":True, 
#         "use_snap_selectable":False, 
#         "snap_point":(0, 0, 0), 
#         "snap_align":False, 
#         "snap_normal":(0, 0, 0), 
#         "gpencil_strokes":False, 
#         "cursor_transform":False, 
#         "texture_space":False, 
#         "remove_on_cancel":False, 
#         "use_duplicated_keyframes":False, 
#         "view2d_edge_pan":False, 
#         "release_confirm":False, 
#         "use_accurate":False, 
#         "alt_navigation":True, 
#         "use_automerge_and_split":False})

