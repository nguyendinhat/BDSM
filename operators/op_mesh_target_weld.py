import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class BDSM_Mesh_TargetWeld(Operator):
    bl_idname = 'view3d.bdsm_targetweld'
    bl_label = 'BDSM Target Weld'
    bl_description = 'Toggles snap to vertex and automerge editing on and off'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    toggle: BoolProperty(
        name='Toggle',
        default=False
    )

    def toggle_target_weld_on(self, context):
        context.scene.tool_settings.snap_elements = {'VERTEX'}
        context.scene.tool_settings.snap_target = 'CLOSEST'
        context.scene.tool_settings.use_mesh_automerge = True
        bpy.context.scene.tool_settings.use_snap = True

    def toggle_target_weld_off(self, context):
        context.scene.tool_settings.use_mesh_automerge = False
        bpy.context.scene.tool_settings.use_snap = False

    def toggle_target_weld(self, context):
        props = context.window_manager.BDSM_Context

        if context.scene.tool_settings.use_mesh_automerge and bpy.context.scene.tool_settings.use_snap:
            props.tg_target_weld = False
        else:
            # space = [space for area in bpy.context.screen.areas if area.type == 'VIEW_3D' for space in area.spaces  if space.type == 'VIEW_3D']
            #space[0].show_region_ui = True
            props.topbar_enums = 'EDIT_TAB'
            props.selection_enums = 'SELECT_VERT'
            props.tg_target_weld = True


    def execute(self, context):
        if self.toggle:
            self.toggle_target_weld(context)
            return{'FINISHED'}

        props = context.window_manager.BDSM_Context
        if props.tg_target_weld:
            self.toggle_target_weld_on(context)
        else:
            self.toggle_target_weld_off(context)
        return{'FINISHED'}
