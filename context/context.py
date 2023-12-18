import bpy
from bpy.props import (BoolProperty,EnumProperty, IntProperty, FloatProperty)
from bpy.types import PropertyGroup
from math import radians, degrees

from ..context import items

class BDSM_Context(PropertyGroup):
    prefs = bpy.context.preferences.addons['BDSM'].preferences
    topbar_enums: EnumProperty(
        items=(items.get_topbar),
        name='Top bar',
        update=items.control_panel
    )

    alignbar_enums: EnumProperty(
        items=(items.get_alignbar),
        name='Alignment bar',
    )

    selection_enums: EnumProperty(
        items=(items.get_selection),
        name='Selection',
        update=items.control_panel
    )
    selection_mode_action: EnumProperty(
        items=(items.get_selection_action),
        name='Selection mode action',
        update=items.control_panel
    )
    selection_mode_extend: BoolProperty(
        name='Extend',
        description='Selection mode extend',
        default=False,
    )
    selection_mode_expand: BoolProperty(
        name='Expand',
        description='Selection mode expand',
        default=False,
    )
    selection_type_enums: EnumProperty(
        items=(items.get_selection_type),
        name='Selection type',
    )
    display_shading_enums: EnumProperty(
        items=(items.get_display_shading),
        name='Display Shade Mode',
    )
    display_shading_color_enums: EnumProperty(
        items=(items.get_display_shading_color),
        name='Display Shade Color Mode',
    )
    display_shading_light_enums: EnumProperty(
        items=(items.get_display_shading_light),
        name='Display Shade Light Mode',
    )

    pivot_enums:EnumProperty(
        items=(items.get_pivot),
        name='Pivot ',
        update=items.update_pivot
    )
    oriental_enums:EnumProperty(
        items=[
            ('ORIENT_CURSOR', 'Cursor', 'Orientation Cursor','ORIENTATION_CURSOR', 0),
            ('ORIENT_GLOBAL', 'Global', 'Orientation Global', 'ORIENTATION_GLOBAL', 1),
            ('ORIENT_LOCAL', 'Local', 'Orientation Local', 'ORIENTATION_LOCAL', 2),
            ('ORIENT_NORMAL', 'Normal','Orientation Normal', 'ORIENTATION_NORMAL', 3),
            ('ORIENT_GIMBAL', 'Gimbal','Orientation Gimbal', 'ORIENTATION_GIMBAL', 4),
            ('ORIENT_VIEW', 'View', 'Orientation View','ORIENTATION_VIEW', 5),
            ('ORIENT_PARENT', 'Parent', 'Orientation Parent','ORIENTATION_PARENT', 6),
        ],
        name='Orientations ',
        default='ORIENT_GLOBAL',
        update=items.update_oriental
    )
    rotate_step_enums:EnumProperty(
        items=(items.get_rotate_step),
        name='Rotate Step',
        update=items.set_rotate_step
    )

    rotate_rad_step: FloatProperty(
        name= 'Rotate by step',
        description='Rotate by step',
        default=0.00,
        soft_max= radians(360),
        soft_min= radians(-360.0),
        subtype='ANGLE',
    )


    block_type_enums:EnumProperty(
        items=(items.get_block_type),
        name='Purge Data',
        # default='MATERIAL',
    )
    record_snap: BoolProperty(
        name='Record Snapping tool',
        default=False,
    )



    dotgap: BoolProperty(
        name='Dot Gap',
        default=False,
        description='Dot Gap'
    )
    step: IntProperty(
        name='Step',
        default=1,
        min=1,
        max=1000,
        description='Step loop',
    )

    # unselected_lock: BoolProperty(
    #     name='Lock Unselected',
    #     default=False,
    #     description='Lock Unselected'
    # )
    # unselected_hide: BoolProperty(
    #     name='Hide Unselected',
    #     default=False,
    #     description='Hide Unselected'
    # )


    vp_level: IntProperty(
        min=0,
        max=64,
        description='Viewport Levels to be used',
        default=2
    )

    render_level: IntProperty(
        min=0,
        max=64,
        description='Render Levels to be used',
        default=2
    )
    boundary_smooth: EnumProperty(
        items=[
            ('PRESERVE_CORNERS', 'Preserve Corners', ''),
            ('ALL', 'All', '')
            ],

        description='Controls how open boundaries are smoothed',
        default='PRESERVE_CORNERS'
    )
    optimal_display : BoolProperty(
        description='Use Optimal Display',
        default=True
    )
    limit_surface: BoolProperty(
        description='Use Limit Surface',
        default=True
    )
    on_cage: BoolProperty(
        description='Show On Edit Cage',
        default=True
    )
    flat_edit: BoolProperty(
        description='Set Flat Shading when Subd is Level 0',
        default=True
    )
    subd_autosmooth: BoolProperty(
        description='ON:Autosmooth is turned off by toggle when subd is on - and vice versa\n''OFF:Autosmooth is not changed by toggle',
        name='Autosmooth Toggle',
        default=True
    )

    clean_doubles: BoolProperty(
        name='Double Geo',
        default=True,
        description='Vertices occupying the same location (within 0.0001)'
    )
    clean_doubles_val: FloatProperty(
        name='Double Geo Distance',
        default=0.0001,
        precision=4
    )
    clean_loose: BoolProperty(
        name='Loose Verts/Edges',
        default=True,
        description='Verts/Edges not attached to faces')
    clean_interior: BoolProperty(
        name='Interior Faces',
        default=True,
        description='Faces where all edges have more than 2 face users'
    )
    clean_degenerate: BoolProperty(
        name='Degenerate Geo',
        default=True,
        description='Non-Manifold geo: Edges with no length & Faces with no area')
    clean_tinyedge: BoolProperty(
        name='Tiny Edges',
        default=True,
        description='Edges that are shorter than the Tiny-Edge Value set\n' 'Selection only - will select also in Clean Mode'
    )
    clean_tinyedge_val: FloatProperty(
        name='Tiny Edge Limit',
        default=0.002,
        precision=4,
        description='Shortest allowed Edge length for Tiny Edge Selection'
    )
    clean_collinear: BoolProperty(
        name='Collinear Verts',
        default=True,
        description='Additional(Superfluous) verts in a straight line on an edge'
    )

    clean_collinear_val: IntProperty(
        name="Collinear Tolerance",
        min=0,
        max=100,
        default=0,
        subtype="PERCENTAGE",
        description="Increase to catch larger angle differences\n"
        "Note: There is a very small tolerance even at 0"
    )

    object_type: EnumProperty(
        items=(items.get_object_type),
        name='bdsm_prop_object_type')

    extrude_mode: EnumProperty(
        items=(items.get_extrude_mode),
        name='bdsm_prop_extrude_mode'
    )

    tg_target_weld: BoolProperty(
        name='Target weld',
        default=False,
        description='Target weld',
        update= items.update_toggle_targetweld
    )
    tg_modifier_apply: BoolProperty(
        name='Modifier apply',
        default=True,
        description='Modifier apply',
        update=items.update_toggle_modifier_apply
    )

    tg_show_origin: BoolProperty(
        name='Show Origin',
        default=False,
        description='Show Origin',
        update= items.update_show_origin
    )
