import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator

from .. context import items
from .. utils.tools import cycle_mode_array, cycle_mode_list

class BDSM_Pivot_Set(Operator):
    bl_idname = 'view3d.bdsm_pivot_set'
    bl_label = 'BDSM Pivot Set'
    bl_description = 'BDSM Pivot Set\nQuick change pivot point'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    type: EnumProperty(
        items=items.get_pivot,
    )
    mode: EnumProperty(
        items=items.get_mode_props,
    )
    def execute(self, context):
        props = context.window_manager.BDSM_Context
        if self.mode == 'SET':
            props.pivot_enums = self.type
            return {'FINISHED'}
        if self.mode == 'CYCLE':
            cycle = items.get_pivot(self, context)
            value = 'PIVOT_' + context.scene.tool_settings.transform_pivot_point
            props.pivot_enums = cycle_mode_list(cycle,value)
            return {'FINISHED'}
        if self.mode == 'TYPE_1':
            cycle = ['PIVOT_BOUNDING_BOX_CENTER','PIVOT_INDIVIDUAL_ORIGINS','PIVOT_ACTIVE_ELEMENT','PIVOT_CURSOR']
            value = 'PIVOT_' + context.scene.tool_settings.transform_pivot_point
            props.pivot_enums = cycle_mode_array(cycle,value)
            return {'FINISHED'}
        if self.mode == 'TYPE_2':
            cycle = ['PIVOT_MEDIAN_POINT','PIVOT_INDIVIDUAL_ORIGINS','PIVOT_ACTIVE_ELEMENT','PIVOT_CURSOR']
            value = 'PIVOT_' + context.scene.tool_settings.transform_pivot_point
            props.pivot_enums = cycle_mode_array(cycle,value)
            return {'FINISHED'}
        if self.mode == 'TYPE_3':
            cycle = ['PIVOT_MEDIAN_POINT','PIVOT_INDIVIDUAL_ORIGINS','PIVOT_ACTIVE_ELEMENT']
            value = 'PIVOT_' + context.scene.tool_settings.transform_pivot_point
            props.pivot_enums = cycle_mode_array(cycle,value)
            return {'FINISHED'}
        context.scene.tool_settings.transform_pivot_point = props.pivot_enums.replace('PIVOT_','')
        return {'FINISHED'}

class BDSM_Oriental_Set(Operator):
    bl_idname = 'view3d.bdsm_oriental_set'
    bl_label = 'BDSM Oriental Set'
    bl_description = 'BDSM Oriental Set\nQuick change orientation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    type: EnumProperty(
        items=items.get_oriental,
    )
    mode: EnumProperty(
        items=items.get_mode_props,
    )
    def execute(self, context):
        props = context.window_manager.BDSM_Context
        if self.mode == 'SET':
            props.oriental_enums = self.type.replace
            return {'FINISHED'}
        if self.mode == 'CYCLE':
            cycle = items.get_oriental(self, context)
            value = 'ORIENT_' + context.scene.transform_orientation_slots[0].type
            props.oriental_enums = cycle_mode_list(cycle,value)
            return {'FINISHED'}
        if self.mode == 'TYPE_1':
            cycle = ['ORIENT_GLOBAL','ORIENT_NORMAL','ORIENT_LOCAL']
            value = 'ORIENT_' + context.scene.transform_orientation_slots[0].type
            props.oriental_enums = cycle_mode_array(cycle,value)
        context.scene.transform_orientation_slots[0].type = props.oriental_enums.replace('ORIENT_','')
        return {'FINISHED'}

class BDSM_Origin_Set(Operator):
    bl_idname = 'view3d.bdsm_origin_set'
    bl_label = 'BDSM Origin Set'
    bl_description = 'BDSM Origin Set\nSet location origin'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    toggle: BoolProperty(
        name='Toggle',
        default=False
    )
    set: BoolProperty(
        name='Set',
        default=False
    )
    def set_origin(self, context):
        if context.mode == 'OBJECT':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        elif context.mode == 'EDIT_MESH':
            cl = context.scene.cursor.location
            pos2 = (cl[0], cl[1], cl[2])
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.editmode_toggle()
            context.scene.cursor.location = (pos2[0], pos2[1], pos2[2])
        return {'FINISHED'}

    def execute(self, context):
        props = context.window_manager.BDSM_Context
        if self.set:
            self.set_origin(context)
            return {'FINISHED'}
        if self.toggle:
            if context.mode != 'OBJECT':
                self.report({'ERROR_INVALID_CONTEXT'},'Origin Set: Only show origin in Object mode!')
                return {'FINISHED'}
            if context.scene.tool_settings.use_transform_data_origin:
                props.tg_show_origin = False
            else:
                props.tg_show_origin = True
            return {'FINISHED'}
        context.scene.tool_settings.use_transform_data_origin = props.tg_show_origin
        return {'FINISHED'}