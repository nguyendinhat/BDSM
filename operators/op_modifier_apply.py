import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from .. utils import tools


class BDSM_Modifier_Apply(Operator):
    bl_idname = 'view3d.bdsm_modifier_apply'
    bl_label = 'BDSM Modifier Apply'
    bl_description = 'BDSM Modifier Apply\n'\
                    'Toggles the modifiers on and off for selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    toggle: BoolProperty(
        name='Toggle',
        default=False
    )

    def modifier_toggle_on(self, object):
        for modifier in object.modifiers:
                    modifier.show_in_editmode = True
                    modifier.show_viewport = True

    def modifier_toggle_off(self, object):
        for modifier in object.modifiers:
                    modifier.show_in_editmode = False
                    modifier.show_viewport = False

    def modifier_toggle(self, context):
        mode = tools.get_mode()
        if mode in ['VERT', 'EDGE', 'FACE']:
            tools.set_mode('OBJECT')
        selected = tools.get_selected()
        for obj in selected:
            if all(modifier.show_in_editmode and modifier.show_viewport for modifier in obj.modifiers):
                self.modifier_toggle_on(obj)
            else:
                self.modifier_toggle_off(obj)
        if mode in ['VERT', 'EDGE', 'FACE']:
            tools.set_mode(mode)

    def execute(self, context):
        if self.toggle:
            self.modifier_toggle(context)
            return{'FINISHED'}

        props = context.window_manager.BDSM_Context
        if props.tg_modifier_apply:
            mode = tools.get_mode()
            if mode in ['VERT', 'EDGE', 'FACE']:
                tools.set_mode('OBJECT')
            selected = tools.get_selected()
            for obj in selected:
                self.modifier_toggle_on(obj)
        else:
            mode = tools.get_mode()
            if mode in ['VERT', 'EDGE', 'FACE']:
                tools.set_mode('OBJECT')
            selected = tools.get_selected()
            for obj in selected:
                self.modifier_toggle_off(obj)

        if mode in ['VERT', 'EDGE', 'FACE']:
            tools.set_mode(mode)
        return{'FINISHED'}

