import bpy
from math import radians

def get_topbar(self, context):
    return [
    ('CREATE_TAB', 'Create tab', 'Create tab', 'PLUS', 0),
    ('EDIT_TAB', 'Edit tab', 'edit tab', 'EDITMODE_HLT', 1),
    ('MODIFY_TAB', 'Modify tab', 'Modify tab', 'MODIFIER', 2),
    ('ORIGIN_TAB', 'Origin tab', 'Origin tab', 'OBJECT_ORIGIN', 3),
    ('DIPSPLAY_TAB', 'Display tab', 'Display tab', 'WORKSPACE', 4),
    ('UTILITIES_TAB', 'Utilities tab', 'Utilities tab', 'TOOL_SETTINGS', 5),
    ]

def get_alignbar(self, context):
    return [
    ('ORIGIN_TAB', 'Origin tab', '', 'OBJECT_ORIGIN', 0),
    ('CURSOR_TAB', 'Cursor tab', '', 'PIVOT_CURSOR', 1),
    ('OBJECT_TAB', 'Object tab', '', 'OUTLINER_OB_MESH', 2),
    ]

def control_panel(self, context):
    bpy.ops.wm.bdsm_control_panel()

def update_toggle_targetweld(self, context):
    bpy.ops.view3d.bdsm_targetweld()

def update_toggle_modifier_apply(self, context):
    bpy.ops.view3d.bdsm_modifier_apply()

def update_pivot(self, context):
     bpy.ops.view3d.bdsm_pivot_set()
def update_oriental(self, context):
     bpy.ops.view3d.bdsm_oriental_set()
def update_show_origin(self, context):
     bpy.ops.view3d.bdsm_origin_set()
     return {'FINISHED'}

def get_selection(self, context):
    return [
    ('SELECT_VERT', 'Vertex', 'Vertex', 'VERTEXSEL', 0),
    ('SELECT_EDGE', 'Edge', 'Edge', 'EDGESEL', 1),
    ('SELECT_FACE', 'Face', 'Face', 'FACESEL', 2),
    ('SELECT_OBJECT', 'Object', 'Object', 'SNAP_VOLUME', 3),
    ('SELECT_ELEMEMT', 'Element', 'Element', 'MOD_EXPLODE', 4),
    ('SELECT_BORDER', 'Border', 'Border', 'SHAPEKEY_DATA', 5),
    ]


def get_selection_action(self, context):
    return [
    ('DISABLE', 'Disable', 'Disable', 'FAKE_USER_OFF', 0),
    ('ENABLE', 'Enable', 'Enable', 'FAKE_USER_ON', 1),
    ('TOGGLE', 'Toggle', 'Toggle', 'PROPERTIES', 2),
    ]


def get_selection_mode(self, context):
    return [
    ('SELECT_MODE_EXTEND', 'Extend', 'Select mode extend', 'TRACKER', 0),
    ('SELECT_MODE_EXPAND', 'Expand', 'Select mode expand', 'CON_OBJECTSOLVER', 1)
    ]
def get_selection_type(self, context):
    return [
    ('SELECT_TYPE_TWEAK', 'Tweak', 'Select type tweak', 'RESTRICT_SELECT_OFF', 0),
    ('SELECT_TYPE_BOX', 'Box', 'Select type box', 'OBJECT_DATAMODE', 1),
    ('SELECT_TYPE_CIRCLE', 'Circle', 'Select type circle', 'PHYSICS', 2),
    ('SELECT_TYPE_LASSO', 'Lasso', 'Select type Lasso', 'MOD_DISPLACE', 3),
    ]

def get_select_loop_step(self, context):
    return [
    ('LOOP', 'Loop', 'Select by loop', 'MOD_SCREW', 0),
    ('RING', 'Ring', 'Select by ring', 'MOD_INSTANCE', 1)
    ]


def get_display_shading(self, context):
    return [
    ('SHADE_SOLID', 'Solid', 'Shading Solid', 'SHADING_SOLID', 0),
    ('SHADE_MATERIAL', 'Material', 'Shading Material', 'SHADING_TEXTURE', 1),
    ('SHADE_RENDERED', 'Circle', 'Shading Rendered', 'SHADING_RENDERED', 2)
    ]
def get_display_shading_color(self, context):
    return [
    ('SHADE_COLOR_MATERIAL', 'Material', 'Shading Color Material', '', 0),
    ('SHADE_COLOR_SINGLE', 'Single', 'Shading Color Single', '', 1),
    ('SHADE_COLOR_OBJECT', 'Objcect', 'Shading Color Objcect', '', 2),
    ('SHADE_COLOR_RANDOM', 'Random', 'Shading Color', '', 3),
    ('SHADE_COLOR_VERTEX', 'Attibute', 'Shading Color Vertex', '', 4),
    ('SHADE_COLOR_TEXTURE', 'Texture', 'Shading Color Texture', '', 5)
    ]
def get_display_shading_light(self, context):
    return [
    ('SHADE_LIGHT_STUDIO', 'Studio', 'Shading light studio Material', '', 0),
    ('SHADE_LIGHT_MATCAP', 'Matcap', 'Shading light matcap', '', 1),
    ('SHADE_LIGHT_FLAT', 'Flat', 'Shading light flat', '', 2),
    ]

def get_pivot(self, context):
    return [
    ('PIVOT_BOUNDING_BOX_CENTER', 'Bounding Box Center', 'Shading light studio Material', 'PIVOT_BOUNDBOX', 0),
    ('PIVOT_CURSOR', '3D Cursor', 'Shading light matcap', 'PIVOT_CURSOR', 1),
    ('PIVOT_INDIVIDUAL_ORIGINS', 'Individual origin','Individual origin', 'PIVOT_INDIVIDUAL', 3),
    ('PIVOT_MEDIAN_POINT', 'Median Pont','Median Pont', 'PIVOT_MEDIAN', 4),
    ('PIVOT_ACTIVE_ELEMENT', 'Active Element', 'Active Element','PIVOT_ACTIVE', 5),
    ]

# end def
def get_oriental(self, context):
    return [
    ('ORIENT_CURSOR', 'Cursor', 'Orientation Cursor','ORIENTATION_CURSOR', 0),
    ('ORIENT_GLOBAL', 'Global', 'Orientation Global', 'ORIENTATION_GLOBAL', 1),
    ('ORIENT_LOCAL', 'Local', 'Orientation Local', 'ORIENTATION_LOCAL', 2),
    ('ORIENT_NORMAL', 'Normal','Orientation Normal', 'ORIENTATION_NORMAL', 3),
    ('ORIENT_GIMBAL', 'Gimbal','Orientation Gimbal', 'ORIENTATION_GIMBAL', 4),
    ('ORIENT_VIEW', 'View', 'Orientation View','ORIENTATION_VIEW', 5),
    ('ORIENT_PARENT', 'Parent', 'Orientation Parent','ORIENTATION_PARENT', 6),
    ]


def get_rotate_step(self, context):
    return [
    ('ROTATE_STEP_5', '5°', 'Step Rotate 5°', '', 1),
    ('ROTATE_STEP_30', '30°', 'Step Rotate 30°', '', 2),
    ('ROTATE_STEP_45', '45°', 'Step Rotate 45°', '', 3),
    ('ROTATE_STEP_90', '90°', 'Step Rotate 90°', '', 4),
    ]
def set_rotate_step(self, context):
    props = context.window_manager.BDSM_Context
    step =  radians(float(props.rotate_step_enums.replace('ROTATE_STEP_', '')))
    props.rotate_rad_step = step

def get_snap_mode(self, context):
    return [
    ('SNAP_1', 'Snap 1', 'Snap mode 1', 'EVENT_F1', 0),
    ('SNAP_2', 'Snap 2', 'Snap mode 2', 'EVENT_F2', 1),
    ('SNAP_3', 'Snap 3', 'Snap mode 3', 'EVENT_F3', 2),
    ('SNAP_4', 'Snap 4', 'Snap mode 4', 'EVENT_F4', 3),
    ]

def get_snap_type(self, context):
    return [
    ('SNAP_INCREMENT', 'Increment', 'Snap Increment', 'SNAP_INCREMENT', 0),
    ('SNAP_VERTEX', 'Vertex', 'Snap Vertex', 'SNAP_VERTEX', 1),
    ('SNAP_EDGE', 'Snap 3', 'Snap edge', 'SNAP_EDGE', 2),
    ('SNAP_FACE', 'Face', 'Snap face', 'SNAP_FACE', 3),
    ('SNAP_FACE_NEAREST', 'Face Nearest', 'Snap face', 'SNAP_FACE_NEAREST', 4),
    ('SNAP_VOLUME', 'Volume', 'Snap Volume', 'SNAP_VOLUME', 5),
    ('SNAP_MIDPOINT', 'Edge Center', 'Snap Mid Point', 'SNAP_MIDPOINT', 6),
    ('SNAP_PERPENDICULAR', 'Edge Perpendicular', 'Snap Perpendicular', 'SNAP_PERPENDICULAR', 7),
    ]
def get_snap_target(self, context):
    return [
    ('CLOSEST', 'Closest', 'Snap with Closest', 'FORCE_LENNARDJONES', 0),
    ('CENTER', 'Center', 'Snap with Center', 'PROP_ON', 1),
    ('MEDIAN', 'Median', 'Snap with Median', 'PIVOT_MEDIAN', 2),
    ('ACTIVE', 'Active', 'Snap with Active', 'PIVOT_ACTIVE', 3),
    ]
def update_snap_target(self, context):
    bpy.ops.wm.bdsm_snap_target()

def get_block_type(self, context):
    return [('MESH', 'Mesh', '', 1),
    ('CURVE', 'Materials', '', 2),
    ('TEXTURE', 'Textures', '', 3),
    ('IMAGE', 'Images', '', 4)
    ]

def get_object_type(self, context):
    return [
    ('builtin.primitive_cube_add', 'Box', '', 'CUBE', 1),
    ('builtin.primitive_cylinder_add', 'Cylinder', '', 'MESH_CYLINDER', 2),
    ('builtin.primitive_cone_add', 'Cone', '', 'MESH_CONE', 3),
    ('builtin.primitive_uv_sphere_add', 'Sphere', '', 'MESH_UVSPHERE', 4),
]


def get_extrude_mode(self, context):
    return [
    ('EXTRUDE_REGION', 'Extrude Region', '', 'FACESEL', 0),
    ('EXTRUDE_ALONG_NORMAL', 'Extrude Along normal', '', 'MOD_SOLIDIFY', 1),
    ('EXTRUDE_INDIVIDUAL', 'Extrude Individual', '', 'UV_FACESEL', 2),
    ('EXTRUDE_MANIFOLD', 'Extrude Manifold', '', 'SHAPEKEY_DATA', 3),
]

def get_mode_props(self, context):
    return [
    ('DEFAULT', 'Default', '', 'AUTO', 0),
    ('SET', 'Set', '', 'PLUGIN', 1),
    ('TOGGLE', 'Toggle', '', 'PROPERTIES', 2),
    ('CYCLE', 'Cycle', '', 'FILE_REFRESH', 3),
    ('TYPE_1', 'Type 1', '', 'EVENT_F1', 4),
    ('TYPE_2', 'Type 2', '', 'EVENT_F2', 5),
    ('TYPE_3', 'Type 3', '', 'EVENT_F3', 6),
    ('TYPE_4', 'Type 4', '', 'EVENT_F4', 7),
    ('TYPE_5', 'Type 5', '', 'EVENT_F5', 8),
    ('TYPE_6', 'Type 6', '', 'EVENT_F6', 9),
    ('TYPE_8', 'Type 7', '', 'EVENT_F7', 10),
    ('TYPE_9', 'Type 8', '', 'EVENT_F8', 11),
    ('TYPE_0', 'Type 9', '', 'EVENT_F9', 12),
]














