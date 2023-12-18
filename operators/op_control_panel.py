import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
from ..context import items
from ..utils import dict, tools

class BDSM_ControlPanel(Operator):
    bl_idname = 'wm.bdsm_control_panel'
    bl_label = 'BDSM Control Panel'
    bl_description = 'BDSM Control Panel'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        props = context.window_manager.BDSM_Context
        #Topbar
        if props.topbar_enums == 'CREATE_TAB':
            # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            return {'FINISHED'}
        if props.topbar_enums == 'EDIT_TAB':
            #Select
            if props.selection_enums == 'SELECT_VERT':
                if context.mode == 'OBJECT':
                    bpy.ops.object.mode_set_with_submode(mode='EDIT',toggle=False, mesh_select_mode={'VERT'})
                else:
                    bpy.ops.mesh.select_mode(
                        type='VERT',
                        action=props.selection_mode_action,
                        use_extend=props.selection_mode_extend,
                        use_expand=props.selection_mode_expand
                    )
                return {'FINISHED'}
            if props.selection_enums == 'SELECT_EDGE':
                if context.mode == 'OBJECT':
                    bpy.ops.object.mode_set_with_submode(mode='EDIT',toggle=False, mesh_select_mode={'EDGE'})
                else:
                    bpy.ops.mesh.select_mode(
                        type='EDGE',
                        action=props.selection_mode_action,
                        use_extend=props.selection_mode_extend,
                        use_expand=props.selection_mode_expand
                    )
                return {'FINISHED'}
            if props.selection_enums == 'SELECT_FACE':
                if context.mode == 'OBJECT':
                    bpy.ops.object.mode_set_with_submode(mode='EDIT',toggle=False, mesh_select_mode={'FACE'})
                else:
                    bpy.ops.mesh.select_mode(
                        type='FACE',
                        action=props.selection_mode_action,
                        use_extend=props.selection_mode_extend,
                        use_expand=props.selection_mode_expand
                    )
                return {'FINISHED'}
            if props.selection_enums == 'SELECT_OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                return {'FINISHED'}
            if props.selection_enums == 'SELECT_ELEMEMT':
                if context.mode == 'OBJECT':
                    bpy.ops.object.mode_set_with_submode(mode='EDIT',toggle=False, mesh_select_mode={'FACE'})
                else:
                    bpy.ops.mesh.select_linked(delimit={'NORMAL'})
                    bpy.ops.mesh.select_mode(
                        type='FACE',
                        action=props.selection_mode_action,
                        use_extend=props.selection_mode_extend,
                        use_expand=props.selection_mode_expand
                    )
                return {'FINISHED'}
            if props.selection_enums == 'SELECT_BORDER':
                if context.mode == 'OBJECT':
                    bpy.ops.object.mode_set_with_submode(mode='EDIT',toggle=False, mesh_select_mode={'EDGE'})
                else:
                    if tools.get_mode() == 'FACE':
                        bpy.ops.mesh.select_mode(type='VERT')
                    bpy.ops.mesh.bdsm_select_border_edges()
                return {'FINISHED'}

        if props.topbar_enums == 'MODIFY_TAB':
            return {'FINISHED'}
        if props.topbar_enums == 'ORIGIN_TAB':
            return {'FINISHED'}
        if props.topbar_enums == 'DIPSPLAY_TAB':
            return {'FINISHED'}
        if props.topbar_enums == 'UTILITIES_TAB':
            return {'FINISHED'}

        return {'FINISHED'}

class BDSM_ControlObjectModeSet(Operator):
    bl_idname = 'object.bdsm_control_object_modeset'
    bl_label = 'BDSM Control Object modeset'
    bl_description = 'BDSM Control Object modeset'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = bpy.context.preferences.addons['BDSM'].preferences
        props = context.window_manager.BDSM_Context
        current_object = bpy.context.object
        if current_object != None:
            mode_edit = ['EDIT_MESH','EDIT_CURVE','EDIT_SURFACE','EDIT_METABALL','EDIT_TEXT','EDIT_ARMATURE','EDIT_LATTICE']
            mode_none = ['EMPTY','CAMERA','LIGHT','LIGHT_PROBE','SPEAKER']
            if current_object.type in mode_none:
                prefs.object_modeset_edit = False
                return {'FINISHED'}
            elif current_object.type == 'GPENCIL':
                if context.mode == 'EDIT_GPENCIL':
                    prefs.object_modeset_edit = tools.back_mode(prefs.object_modeset_previous)
                    return {'FINISHED'}
                else:
                    prefs.object_modeset_previous = context.mode
                    prefs.object_modeset_edit = tools.target_mode('EDIT_GPENCIL')
                    return {'FINISHED'}

            else:
                if context.mode in mode_edit:
                    prefs.object_modeset_edit = tools.back_mode(prefs.object_modeset_previous)
                    return {'FINISHED'}
                else:
                    if prefs.object_modeset_previous == context.mode:
                        bpy.ops.object.mode_set(mode='EDIT')
                    else:
                        prefs.object_modeset_previous = context.mode
                        prefs.object_modeset_edit = tools.target_mode('EDIT')
                    props.topbar_enums = 'EDIT_TAB'
                    return {'FINISHED'}
        return {'FINISHED'}

class BDSM_ControlMeshModeSet(Operator):
    bl_idname = 'wm.bdsm_control_mesh_modeset'
    bl_label = 'BDSM Control Mesh modeset'
    bl_description = 'BDSM Control Mesh modeset'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    type: EnumProperty(
        items=(items.get_selection),
        name='Type',
        description='Type select mode',
    )
    action: EnumProperty(
        items=(items.get_selection_action),
        name='Action',
        description='Action select mode',
    )
    use_extend: BoolProperty(
        name='Extend',
        description='Extend select mode',
        default= False,
    )
    use_expand: BoolProperty(
        name='Expand',
        description='Expand select mode',
        default= False,
    )

    def execute(self, context):
        prefs = bpy.context.preferences.addons['BDSM'].preferences
        props = context.window_manager.BDSM_Context
        selection_mode = (tuple(bpy.context.scene.tool_settings.mesh_select_mode))

        props.selection_mode_action = self.action
        props.selection_mode_extend = self.use_extend
        props.selection_mode_expand = self.use_expand
        props.topbar_enums = 'EDIT_TAB'
        # [1]
        if self.type == 'SELECT_VERT':
            prefs.mesh_modeset_vert = selection_mode[0]
            props.selection_enums = 'SELECT_VERT'
        #[2]
        if self.type == 'SELECT_EDGE':
            prefs.mesh_modeset_edge = selection_mode[1]
            props.selection_enums = 'SELECT_EDGE'
        #[3]
        if self.type == 'SELECT_FACE':
            prefs.mesh_modeset_face = selection_mode[2]
            props.selection_enums = 'SELECT_FACE'
        #[4]
        if self.type == 'SELECT_OBJECT':
            props.selection_enums = 'SELECT_OBJECT'
        #[5]
        if self.type == 'SELECT_ELEMEMT':
            prefs.mesh_modeset_face = selection_mode[2]
            props.selection_enums = 'SELECT_ELEMEMT'
        #[6]
        if self.type == 'SELECT_BORDER':
            prefs.mesh_modeset_edge = selection_mode[1]
            props.selection_enums = 'SELECT_BORDER'
        return {'FINISHED'}