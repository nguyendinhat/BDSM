import bpy
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector

from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix, Vector
from math import radians, degrees


def mouse_2d_to_3d(context, event):
    x, y = event.mouse_region_x, event.mouse_region_y
    location = region_2d_to_location_3d(context.region, context.space_data.region_3d, (x, y), (0, 0, 0))
    return Vector(location)

class BDSM_Transform_Move(Operator):
    bl_idname = 'mesh.bdsm_transform_move'
    bl_label = 'BDSM Transform Move'
    bl_description = 'BDSM Transform Move'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        areas = bpy.context.workspace.screens[0].areas
        for area in areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Make sure active tool is set to select
                    bpy.ops.wm.tool_set_by_id( name='builtin.select_box')
        # bpy.ops.transform.translate(
        #     'INVOKE_DEFAULT',
        #     orient_type = 'NORMAL',
        #     orient_matrix_type = 'NORMAL',
        #     constraint_axis = (False, False, True),
        #     alt_navigation = True
        # )
        # if space.show_gizmo_object_translate:
        #     bpy.ops.transform.translate('INVOKE_DEFAULT')
        # else:
                    space.show_gizmo_object_translate = True
                    space.show_gizmo_object_rotate = False
                    space.show_gizmo_object_scale = False
        return{'FINISHED'}

class BDSM_Transform_Rotate(Operator):
    bl_idname = 'mesh.bdsm_transform_rotate'
    bl_label = 'BDSM Transform Rotate'
    bl_description = 'BDSM Transform Rotate'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        areas = bpy.context.workspace.screens[0].areas
        for area in areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Make sure active tool is set to select
        # bpy.ops.wm.tool_set_by_id( name='builtin.select_box')
        # bpy.ops.transform.rotate(
        #     'INVOKE_DEFAULT',
        #     orient_axis='Z',
        #     orient_type='VIEW',
        #     orient_matrix_type='VIEW',
        # )
        # if space.show_gizmo_object_rotate:
        #     bpy.ops.transform.rotate('INVOKE_DEFAULT')
        # else:
                    space.show_gizmo_object_translate = False
                    space.show_gizmo_object_rotate = True
                    space.show_gizmo_object_scale = False
        return{'FINISHED'}

class BDSM_Transform_Scale(Operator):
    bl_idname = 'mesh.bdsm_transform_scale'
    bl_label = 'BDSM Transform Sacle'
    bl_description = 'BDSM Transform Sacle'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # areas = bpy.context.workspace.screens[0].areas
        # for area in areas:
        #     for space in area.spaces:
                # if space.type == 'VIEW_3D':
                    # Make sure active tool is set to select
        bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
        bpy.ops.transform.resize(
            'INVOKE_DEFAULT',
            orient_type = 'NORMAL',
            orient_matrix_type = 'NORMAL',
            constraint_axis = (True, True, False),
            alt_navigation = True
        )
        # if space.show_gizmo_object_scale:
        #     bpy.ops.transform.resize('INVOKE_DEFAULT')
        # else:
        #     space.show_gizmo_object_translate = False
        #     space.show_gizmo_object_rotate = False
        #     space.show_gizmo_object_scale = True
        return{'FINISHED'}

class BDSM_Transform_Rotate_Step(Operator):
    bl_idname = 'view3d.bdsm_transform_rotate_step'
    bl_label = 'BDSM Transform Rotate Step'
    bl_description = 'BDSM Transform Rotate Step'\
                    'Rotate object or selected elements given angle, based on viewport relative to the object.\n' \
                    'Local, Cursor & View - else Global orientation.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    rad: FloatProperty(
        name= 'Rotate by step',
        description='Rotate by step',
        default=0.00,
        soft_max= radians(360),
        soft_min= radians(-360.0),
        step=100,
        subtype='ANGLE',
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.space_data.type == "VIEW_3D"

    def execute(self, context):
        obj = context.object
        deg = degrees(self.rad)
        orient_slot = bpy.context.scene.transform_orientation_slots[0].type

        rm = context.space_data.region_3d.view_matrix
        orient_type = "GLOBAL"
        type_matrix = Matrix().to_3x3()

        if orient_slot == "LOCAL":
            orient_type = "LOCAL"
            type_matrix = obj.matrix_world.to_3x3().normalized()
        elif orient_slot == "VIEW":
            orient_type = "VIEW"
            type_matrix = context.space_data.region_3d.view_matrix.inverted().to_3x3()
        elif orient_slot == "CURSOR":
            orient_type = "CURSOR"
            type_matrix = context.scene.cursor.matrix.to_3x3()
        # else defaults to Global for now

        v = type_matrix.inverted() @ Vector(rm[2]).to_3d()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
        nx, ny, nz = v[0], v[1], v[2]

        if x > y and x > z:
            axis = True, False, False
            orient_axis = "X"
            flip = nx
        elif y > x and y > z:
            axis = False, True, False
            orient_axis = "Y"
            flip = ny
        else:
            axis = False, False, True
            orient_axis = "Z"
            flip = nz

        # check for axis inverse (to work with directions in pie menu (view) )
        if flip > 0:
            deg *= -1

        bpy.ops.transform.rotate(value=radians(deg), orient_axis=orient_axis, orient_type=orient_type, orient_matrix_type=orient_type,
                                 constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False)

        return {"FINISHED"}



# bpy.ops.transform.resize(
#     value=(1.19012, 1.19012, 1),

#     mirror=False,
#     use_proportional_edit=False,
#     proportional_edit_falloff='SMOOTH',
#     proportional_size=1,
#     use_proportional_connected=False,
#     use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'},
#     use_snap_project=False, snap_target='CLOSEST',
#     use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

# bpy.ops.transform.rotate(
#     value=4.14682,
    
    
#     orient_matrix=((-0.475625, -0.879648, 4.47035e-07), 
#                    (0.434495, -0.23493, 0.869495), (-0.76485, 0.413554, 0.493941)), 
#     mirror=False, use_proportional_edit=False, 
#     proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, 
#     use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, 
#     snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, 
#     release_confirm=True)
