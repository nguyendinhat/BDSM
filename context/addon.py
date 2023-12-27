import bpy, tempfile, os
from bpy.props import (IntProperty, FloatProperty,StringProperty, BoolProperty,EnumProperty,BoolVectorProperty, FloatVectorProperty)
from bpy.types import AddonPreferences
from .. context import items
from .. interface.preferences import prefs_ui
class BDSM_AddonPreferences(AddonPreferences):
    bl_idname = 'BDSM'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    gpencil_modeset_previous: StringProperty(
        name = 'object_modeset_previous',
        default='OBJECT',
        description='object_modeset_previous',
    )

    object_modeset_previous: StringProperty(
        name = 'object_modeset_previous',
        default='OBJECT',
        description='object_modeset_previous',
    )

    object_modeset_edit: BoolProperty(
        name = 'object_modeset_edit',
        description='Object  (Editmode) = T/F',
        default=False,
    )
    mesh_modeset_vert: BoolProperty(
        name = 'mesh_modeset_vert',
        description='Object modeset (Vertex) = T/F',
        default=False,
    )
    mesh_modeset_edge: BoolProperty(
        name = 'mesh_modeset_vert',
        description='Object modeset (Edge) = T/F',
        default=False,
    )
    mesh_modeset_face: BoolProperty(
        name = 'mesh_modeset_vert',
        description='Object modeset (Face) = T/F',
        default=False,
    )



    enable_sticky_selection: BoolProperty(
        name='Selection Sticky Mode',
        description='Enables Sticky Selection when using Quick Select Modes and Selection Cycle',
        default=False
    )


    tg_edit_geometry: BoolProperty(
        name='Edit Geometry',
        default=True,
        description='Edit Geometry'
    )
    tg_edit_geometry_merg: BoolProperty(
        name='Edit Geometry Merg',
        default=True,
        description='Edit Geometry Merg'
    )

    tg_edit_geometry_flow: BoolProperty(
        name='Edit Geometry flow',
        default=True,
        description='Edit Geometry flow'
    )

    snap_mode_enums:EnumProperty(
        items=(items.get_snap_mode),
        name='Snap mode',
    )

    tg_modifier_list: BoolProperty(
        name='Modifier list',
        default=True,
        description='Modifier list'
    )

    tg_modifier_subdiv: BoolProperty(
        name='Toggle Modify Subdivision',
        default=True,
        description='Toggle Modify Subdivision'
    )

    tg_origin_snap: BoolProperty(
        name='Snap Toogle',
        default=True,
        description='Edit Geometry Merg'
    )

    tg_display_shading: BoolProperty(
        name='Toggle Dipsplay Shading',
        default=False,
    )
    tg_display_overlay: BoolProperty(
        name='Toggle Dipsplay Overlay',
        default=False,
    )

    tg_display_gizmo: BoolProperty(
        name='Toggle Dipsplay Gizmo',
        default=False,
    )
    tg_display_overlay_edit_mesh: BoolProperty(
        name='Toggle Dipsplay Overlay Edit Mesh',
        default=False,
    )
    tg_display_view: BoolProperty(
        name='Edit Object View',
        default=False,
        description='Edit Object View Area'
    )

    tg_display_view_area: BoolProperty(
        name='Edit Object View Area',
        default=False,
        description='Edit Object View Area'
    )

    tg_relative: BoolProperty(
        name='View Axis Relative',
        default=False,
        description='View Axis Relative'
    )


    tg_ulitily_cleanup: BoolProperty(
        name='Cleanup Tool',
        default=True,
    )

    tg_ulitily_ruv: BoolProperty(
        name='RizomUV Tool',
        default=True,
    )

    snap_1_elements: StringProperty(default='VERTEX')
    snap_1_target: StringProperty(default='CLOSEST')
    snap_1_options: BoolVectorProperty(description="Snapping Bools Combo 1", size=11,default=(False, False, True, True, True, True, False, True, True, False, False))
    snap_2_elements: StringProperty(default='EDGE,EDGE_PERPENDICULAR,VERTEX,EDGE_MIDPOINT')
    snap_2_target: StringProperty(default='CENTER')
    snap_2_options: BoolVectorProperty(description="Snapping Bools Combo 1",size=11,default=(False, False, True, True, True, True, False, True, True, False, False))
    snap_3_elements: StringProperty(default='VERTEX,FACE,FACE_PROJECT')
    snap_3_target: StringProperty(default='MEDIAN')
    snap_3_options: BoolVectorProperty(description="Snapping Bools Combo 1",size=11,default=(False, False, True, True, True, True, False, True, True, False, False))
    snap_4_elements: StringProperty(default='VERTEX')
    snap_4_target: StringProperty(default='CLOSEST')
    snap_4_options: BoolVectorProperty(description="Snapping Bools Combo 1", size=11,default=(False, False, True, True, True, True, False, True, True, False, False))
    snap_5_elements: StringProperty(default='VERTEX')
    snap_5_target: StringProperty(default='CLOSEST')
    snap_5_options: BoolVectorProperty(description="Snapping Bools Combo 1", size=11,default=(False, False, True, True, True, True, False, True, True, False, False))
    snap_6_elements: StringProperty(default='VERTEX')
    snap_6_target: StringProperty(default='CLOSEST')
    snap_6_options: BoolVectorProperty(description="Snapping Bools Combo 1", size=11,default=(False, False, True, True, True, True, False, True, True, False, False))

#============[Extend]=============
#vps_smoothing
    smooth_mask:StringProperty(name='Mask Vertex Group', description = 'Vertex Group to mask smoothing', default='')
    invert_mask: BoolProperty(name='Invert Mask', description = 'Invert Mask', default=False)
#vps_smoothing
#============[Extend]=============
#============[QuickMeasure]=============
    quickmeasure: BoolProperty(default=True)
    quickmeasure_running: BoolProperty(default=False)
    # MODAL COLORS
    modal_color_header: FloatVectorProperty(
        name="Header Color",
        subtype='COLOR',
        size=4, default=[0.8, 0.8, 0.8, 1.0]
    )
    modal_color_text: FloatVectorProperty(
        name="Text Color", subtype='COLOR',
        size=4, default=[0.8, 0.8, 0.8, 1.0]
    )
    modal_color_subtext: FloatVectorProperty(
        name="SubText Color",
        subtype='COLOR',
        size=4,
        default=[0.5, 0.5, 0.5, 1.0]
    )
#============[QuickMeasure]=============
#============[Prefs UI]=============
    show_shortcuts: BoolProperty(
        name="Show Assigned Shortcuts",
        default=False
    )
    show_conflicts: BoolProperty(
        name="Show Possible Shortcut Conflicts",
        default=False
    )
#============[Mesh F2]=============
    f2_adjustuv : bpy.props.BoolProperty(
        name="Adjust UV",
        description="Automatically update UV unwrapping",
        default=False)
    f2_autograb : bpy.props.BoolProperty(
        name="Auto Grab",
        description="Automatically puts a newly created vertex in grab mode",
        default=True)
    f2_extendvert : bpy.props.BoolProperty(
        name="Enable Extend Vert",
        description="Enables a way to build tris and quads by adding verts",
        default=False)
    f2_quad_from_e_mat : bpy.props.BoolProperty(
        name="Quad From Edge",
        description="Use active material for created face instead of close one",
        default=True)
    f2_quad_from_v_mat : bpy.props.BoolProperty(
        name="Quad From Vert",
        description="Use active material for created face instead of close one",
        default=True)
    f2_tris_from_v_mat : bpy.props.BoolProperty(
        name="Tris From Vert",
        description="Use active material for created face instead of close one",
        default=True)
    f2_ngons_v_mat : bpy.props.BoolProperty(
        name="Ngons",
        description="Use active material for created face instead of close one",
        default=True)
#==============[HUD]================
    modal_hud_color: FloatVectorProperty(
        name="HUD Font Color",
        subtype='COLOR',
        default=[1, 1, 1],
        size=3,
        min=0,
        max=1
    )
    modal_hud_scale: FloatProperty(
        name="HUD Scale",
        default=1,
        min=0.5,
        max=10
    )
    modal_hud_hints: BoolProperty(
        name="Show Hints",
        default=True
    )
    modal_hud_follow_mouse: BoolProperty(
        name="Follow Mouse",
        default=True
    )
#==================[MACHIN3.PUNCHit]=================
    machin3_punchit_push_default: IntProperty(name="Push Default Value", description="Pushing means widening the Extrusion a tiny bit. \nThis helps with Precision Issues in Polygonal Meshes\nSet to 0 to attempt Extrusions without changing the Shape at all.", default=1, min=0)
    machin3_punchit_pull_default: IntProperty(name="Push Default Value", description="Pulling means receding the initially selected faces a tiny bit. \nThis helps with Precision Issues in Polygonal Meshes", default=1, min=0)
    machin3_punchit_non_manifold_extrude: BoolProperty(name="Support non-manifold meshes", description="Allow Extruding on non-manifold meshes", default=True)
    machin3_punchit_show_sidebar_panel: BoolProperty(name="Show Sidebar Panel", description="Show PUNCHit Panel in 3D View's Sidebar", default=True)
    machin3_punchit_modal_hud_scale: FloatProperty(name="HUD Scale", description="Scale of HUD elements", default=1, min=0.1)
    machin3_punchit_modal_hud_timeout: FloatProperty(name="HUD Timeout", description="Modulate duration of fading HUD elements", default=60, min=0.1)
#============[Kushiro.GridModeler]=============
    kushiro_gridmodeler_textsize: IntProperty(
        name='Text Size',
        default=24,
    )
    kushiro_gridmodeler_textcolor: FloatVectorProperty(
        name='Text Color',
        subtype='COLOR',
        size=4,
        default=(0.88, 0.92, 0.96, 0.8),
        description='Text Color'
        )
    kushiro_gridmodeler_text_pos_x: IntProperty(
        name='Text X position',
        default=120,
    )
    kushiro_gridmodeler_default_operation_mode : EnumProperty(
                #(identifier, name, description, icon, number)
        items = [('ngon','N-gon','','',0),
                 ('lineart','Line Art','','',1),
                 ('newface','Create Face','','',2),
                 ('boolcut','Boolean Cut','','',3),
                 ('boolslice', 'Boolean Slice','','',4),
                 ('linepipe', 'Edge Pipe','','',5),
                 ('linesplit','Line Split','','',6),
                 ('addtext','Add Object','','',7),
                 ],
        name = 'Default Operation Mode',
        default = 'boolcut')
    kushiro_gridmodeler_bool_abs: BoolProperty(
        name='Use Absolute Mode',
        description='Default grid size mode',
        default=True
    )
    kushiro_gridmodeler_bool_showkey: BoolProperty(
        name='Show pressed key on the screen',
        description='Show pressed key on the screen (for video recording)',
        default=False
    )
    kushiro_gridmodeler_line_color: FloatVectorProperty(
        name='Grid Line Color',
        subtype='COLOR',
        size=4,
        default=(1, 1, 1, 0.3),
        min=0.0, max=1.0,
        description='Grid Line Color'
        )
    kushiro_gridmodeler_line_width: IntProperty(
        name='Grid Line Width',
        min=1, max=10,
        default = 2,
        description='Grid Line Width'
        )

    kushiro_gridmodeler_shape_color: FloatVectorProperty(
        name='Shape Line Color',
        subtype='COLOR',
        size=4,
        default=(0.5, 1, 0.5, 1),
        min=0.0, max=1.0,
        description='Shape Line Color'
        )

    kushiro_gridmodeler_shape_width: IntProperty(
        name='Shape Line Width',
        min=1, max=10,
        default = 2,
        description='Shape Line Width'
        )

#============[Prefs UI]=============
    def draw(self, context):
        layout = self.layout
        prefs_ui(self, layout)