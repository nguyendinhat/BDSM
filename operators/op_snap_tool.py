import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

class BDSM_Snap_Tool(Operator):
    bl_idname = 'view3d.bdsm_snap_tool'
    bl_label = 'BDSM Snap Tool'
    bl_description = 'BDSM Snap Tool'
    bl_options = {'REGISTER'}

    mode: StringProperty(options={'HIDDEN'})

    def save_snap_mode(self, context):
        tool_props = context.scene.tool_settings
        elements = ''
        for i in tool_props.snap_elements:
            elements = elements + str(i) + ','
        elements = elements[:-1]
        target = str(tool_props.snap_target)
        options = [bool(tool_props.use_snap_grid_absolute),
            bool(tool_props.use_snap_backface_culling),
            bool(tool_props.use_snap_align_rotation),
            bool(tool_props.use_snap_peel_object),
            bool(tool_props.use_snap_self),
            bool(tool_props.use_snap_edit),
            bool(tool_props.use_snap_nonedit),
            bool(tool_props.use_snap_selectable),
            bool(tool_props.use_snap_translate),
            bool(tool_props.use_snap_rotate),
            bool(tool_props.use_snap_scale),
            ]
        return elements, target, options

    def load_snap_mode(self, context, elements, target, options):
        tool_props = context.scene.tool_settings
        tool_props.snap_elements = elements
        tool_props.snap_target = target
        tool_props.use_snap_grid_absolute = options[0]
        tool_props.use_snap_backface_culling = options[1]
        tool_props.use_snap_align_rotation = options[2]
        tool_props.use_snap_peel_object = options[3]
        tool_props.use_snap_self = options[4]
        tool_props.use_snap_edit = options[5]
        tool_props.use_snap_nonedit = options[6]
        tool_props.use_snap_selectable = options[7]
        tool_props.use_snap_translate = options[8]
        tool_props.use_snap_rotate = options[9]
        tool_props.use_snap_scale = options[10]

    @classmethod
    def description(cls, context, properties):
        if 'LOAD' in properties.mode:
            return 'Recall stored snapping settings from slot' + properties.mode[-1]
        else:
            return 'Store current snapping settings in slot %s' % properties.mode[-1]

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'
    def execute(self, context):
        tool_props = context.scene.tool_settings
        props = context.window_manager.BDSM_Context
        prefs = context.preferences.addons['BDSM'].preferences
        mode = self.mode[:4]
        num = self.mode[5:]
        if mode == 'SAVE':
            exec('elements, target, options = self.save_snap_mode(context)')
            exec('prefs.snap_'+num+'_elements = elements')
            exec('prefs.snap_'+num+'_target = target')
            exec('prefs.snap_'+num+'_options = options')
            return {'FINISHED'}
        elif mode == 'LOAD':
            exec('elements = set(prefs.snap_'+num+'_elements.split(","))')
            exec('target = prefs.snap_'+num+'_target')
            exec('options = prefs.snap_'+num+'_options')
            exec('self.load_snap_mode(context, elements, target, options)')
            return {'FINISHED'}
        else:
            if tool_props.use_snap:
                tool_props.use_snap = False
                props.topbar_enums = 'ORIGIN_TAB'
            else:
                tool_props.use_snap = True
                props.topbar_enums = 'ORIGIN_TAB'
                prefs.tg_edit_geometry_snap = True
        return {'FINISHED'}