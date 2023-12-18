from bpy.types import Operator
from bpy.props import EnumProperty


class BDSM_Object_Select_Lock(Operator):
    bl_idname = 'view3d.bdsm_object_select_lock'
    bl_label = 'BDSM Object Select Lock'
    bl_description = 'BDSM Object Select Lock \n Lock & Unlock object selected'
    bl_options = {'REGISTER', 'UNDO'}
    mode : EnumProperty(
        items=[('LOCK', 'Lock', 'LOCKED', 1),
               ('LOCK_UNSELECTED', 'Lock Unselected', 'RESTRICT_SELECT_ON', 2),
               ('UNLOCK', 'Unlock', 'UNLOCKED', 3)
               ],
        name='Lock & Unlock',
        options={'HIDDEN'},
        default='LOCK')

    @classmethod
    def description(cls, context, properties):
        if properties.mode == 'LOCK':
            return 'Lock: Disable Selection for selected object(s)\nSee selection status in Outliner'
        if properties.mode == 'LOCK_UNSELECTED':
            return 'Lock Unselected: Disable Selection for all unselected object(s)\nSee selection status in Outliner'
        else:
            return 'Unlock: Enables Selection for -all- objects'

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def execute(self, context):

        if self.mode == 'LOCK':
            for obj in context.selected_objects:
                obj.hide_select = True

        elif self.mode == 'LOCK_UNSELECTED':
            sel = context.selected_objects[:]
            for obj in context.scene.objects:
                if obj not in sel:
                    obj.hide_select = True

        elif self.mode == 'UNLOCK':
            for obj in context.scene.objects:
                obj.hide_select = False

        return {'FINISHED'}
