bl_info = {
    'name': 'BDSM',
    'author': 'nguyendinhat',
    'description': 'Collection of context sensitive tools',
    'blender': (4, 0, 0),
    'location': 'View3D',
    'version': (0, 0, 3),
    'doc_url': 'https://github.com/nguyendinhat/RizomUV_Bridge_for_Blender_MacOS',
    'tracker_url': 'https://github.com/nguyendinhat/bdsm/issues',
    'wiki_url': 'https://github.com/nguyendinhat/',
    'warning': '',
    'category': 'Generic'
}

import bpy
from .icons import icons
from .keymaps import shortcut
from .modules import EdgeFlow
from .context import addon, context
from .operators import(
                        op_control_panel,
                        op_create_object,
                        op_mesh_flow_mode,
                        op_select_border_edges,
                        op_select_similar,
                        op_mesh_edge_select_loop_step,
                        op_transform,
                        op_mesh_extrude,
                        op_mesh_bevel,
                        op_mesh_connect,
                        op_mesh_split,
                        op_mesh_target_weld,
                        op_mesh_mirror_flip,
                        op_mesh_merge,
                        op_mesh_smooth,
                        op_mesh_vert_random,
                        op_mesh_edge_subdivide_loops,
                        op_mesh_edge_roundifier,
                        op_mesh_edge_length,
                        op_mesh_edge_shaft,
                        op_mesh_face_inset_fillet,
                        op_mesh_face_cut,
                        op_mesh_face_split_solidify,
                        op_mesh_face_shape,
                        op_mesh_face_fix_ngons,
                        op_mesh_relax,
                        op_mesh_face_plane,
                        op_mesh_select_view,
                        op_object_select_lock,
                        op_object_collision,
                        op_object_drop_it,
                        op_mesh_cleaner,
                        op_mesh_select_error,
                        op_modifier_apply,
                        op_modifier_subdivide_tool,
                        op_view_axis,
                        op_snap_tool,
                        op_pivot,
                        op_copy,
                        op_delete,
                        op_quick_measure,
                    )

from .interface import panel

CLASSES = [
    op_create_object.BDSM_Create_Object,
    op_control_panel.BDSM_ControlPanel,
    op_control_panel.BDSM_ControlObjectModeSet,
    op_control_panel.BDSM_ControlMeshModeSet,
    op_select_border_edges.BDSM_SelectBorderEdges,
    op_select_similar.BDSM_SelectSimilar,

    op_transform.BDSM_Transform_Move,
    op_transform.BDSM_Transform_Rotate,
    op_transform.BDSM_Transform_Scale,
    op_transform.BDSM_Transform_Rotate_Step,

    op_mesh_extrude.BDSM_Mesh_Extrude,
    op_mesh_bevel.BDSM_Mesh_Bevel,
    op_mesh_connect.BDSM_Mesh_Connect,
    op_mesh_split.BDSM_Mesh_Split,
    op_mesh_target_weld.BDSM_Mesh_TargetWeld,
    op_mesh_mirror_flip.BDSM_Mesh_Mirror_Flip,

    op_mesh_merge.BDSM_Mesh_Merge_Mouse,
    op_mesh_merge.BDSM_Mesh_Merge_Active,
    op_mesh_merge.BDSM_Mesh_Merge_NearSelected,

    op_mesh_smooth.BDSM_Mesh_Smooth_Laplacian,
    op_mesh_smooth.BDSM_Mesh_Smooth_Inflate,
    op_mesh_smooth.BDSM_Mesh_Smooth_Volume,

    op_mesh_vert_random.BDSM_Mesh_Vert_Random,

    op_mesh_edge_select_loop_step.BDSM_Mesh_Edge_Select_Loop_Step,
    op_mesh_flow_mode.BDSM_Mesh_Flow_Mode,

    op_mesh_edge_roundifier.BDSM_Mesh_Edge_Roundifier,
    op_mesh_edge_length.BDSM_Mesh_Edge_Length,
    op_mesh_edge_shaft.BDSM_Mesh_Edge_Shaft,
    op_mesh_face_inset_fillet.BDSM_Mesh_Face_Inset_Fillet,
    op_mesh_face_cut.BDSM_Mesh_Deselect_Boundary,
    op_mesh_face_cut.BDSM_Mesh_Face_Cut,
    op_mesh_face_split_solidify.BDSM_Mesh_Face_Split_Solidify,
    op_mesh_face_shape.BDSM_Mesh_Face_Shape,
    op_mesh_face_plane.BDSM_Mesh_Face_Plane,
    op_mesh_relax.BDSM_Mesh_Relax,
    op_mesh_face_fix_ngons.BDSM_Mesh_Fix_Ngons,
    op_mesh_edge_subdivide_loops.BDSM_Mesh_Edge_Subdivide_Loops,

    op_mesh_cleaner.BDSM_Mesh_Clean,
    op_mesh_cleaner.BDSM_Mesh_Clean_Purge,

    op_mesh_select_view.BDSM_Mesh_Select_View,
    op_mesh_select_error.BDSM_Mesh_Select_Vert_Collinear,
    op_mesh_select_error.BDSM_Mesh_Select_Flip_Normal,
    op_mesh_select_error.BDSM_Mesh_Select_Snapping,
    op_mesh_select_error.BDSM_Mesh_Select_Vert_Occluded,
    op_mesh_select_error.BDSM_Mesh_Select_Vert_Counter,

    op_object_select_lock.BDSM_Object_Select_Lock,
    op_object_collision.BDSM_Object_Collision,
    op_object_collision.BDSM_Object_BBox_Match,
    op_object_drop_it.BDSM_Object_Drop_It,

    op_modifier_apply.BDSM_Modifier_Apply,
    op_modifier_subdivide_tool.BDSM_Modifier_Subdivide,
    op_modifier_subdivide_tool.BDSM_Modifier_Subdivide_Step,

    op_view_axis.BDSM_View_Axis,

    op_pivot.BDSM_Pivot_Set,
    op_pivot.BDSM_Oriental_Set,
    op_pivot.BDSM_Origin_Set,

    op_snap_tool.BDSM_Snap_Tool,

    op_copy.BDSM_Copy,
    op_copy.BDSM_Duplicate,
    op_copy.BDSM_Detach,

    op_delete.BDSM_Delete,
    op_delete.BDSM_Dissolve,
    op_quick_measure.BDSM_Quick_Measure,

    addon.BDSM_AddonPreferences,
    context.BDSM_Context,
    panel.VIEW3D_PT_BDSM_PANEL,
]

modules = [
    EdgeFlow,
    shortcut,
    icons,
]


Addons = [
    'add_curve_extra_objects',
    'add_mesh_extra_objects',
    'io_scene_fbx',
    'io_import_images_as_planes',
    'io_curve_svg',
    'io_mesh_uv_layout',
    'io_scene_obj',
    'space_view3d_copy_attributes',
    'mesh_f2',
    'mesh_looptools',
    'node_wrangler',
    'object_boolean_tools',
    'cycles',
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.BDSM_Context = bpy.props.PointerProperty(type=context.BDSM_Context)
    for module in modules:
        module.register()



def unregister():
    for module in reversed(modules):
        module.unregister()

    del bpy.types.WindowManager.BDSM_Context
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    bpy.utils.register()

