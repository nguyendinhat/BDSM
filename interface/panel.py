import bpy
from bpy.types import Panel, VIEW3D_PT_shading
from .. icons.icons import get_icon_id
from .. context.items import get_oriental,get_pivot
from bpy.app.translations import contexts as i18n_contexts

class VIEW3D_PT_BDSM_PANEL(Panel):
    bl_idname = 'BDSM_PT_MAIN'
    bl_label = 'BDSM'
    bl_category = 'BDSM'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):

        view = context.space_data
        tool_props = context.scene.tool_settings
        props = context.window_manager.BDSM_Context
        prefs = bpy.context.preferences.addons['BDSM'].preferences

        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        col = row.column_flow( align=True)
        col.scale_y = 1.25
        col.prop(props, 'topbar_enums', icon_only=True, expand=True, slider=True)
        #CREATE_TAB
        if props.topbar_enums == 'CREATE_TAB':
            #Add Mesh
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Mesh:', icon='OUTLINER_OB_MESH')
            row = col.row(align=True)
            row.operator('wm.bdsm_create_object', text='Box', icon='CUBE').object_type = 'builtin.primitive_cube_add'
            row.operator('mesh.primitive_plane_add', text='Plane', icon='MESH_PLANE')

            row = col.row(align=True)
            row.operator('wm.bdsm_create_object', text='Cylinder', icon='MESH_CYLINDER').object_type = 'builtin.primitive_cylinder_add'
            row.operator('mesh.primitive_circle_add', text='Circle', icon='MESH_CIRCLE')

            row = col.row(align=True)
            row.operator('mesh.primitive_round_cube_add', text='Cube', icon='META_CUBE')
            row.operator('wm.bdsm_create_object', text='Cone', icon='MESH_CONE').object_type = 'builtin.primitive_cone_add'

            row = col.row(align=True)
            row.operator('wm.bdsm_create_object', text='Sphere', icon='MESH_UVSPHERE').object_type = 'builtin.primitive_uv_sphere_add'

            row.operator('mesh.primitive_torus_add', text='Tours', icon='MESH_TORUS')
            #Add Curve
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Curve:', icon='OUTLINER_OB_CURVE')
            col = box.column(align=True)
            row = col.row(align=True)
            grid = col.grid_flow(columns=3, align=True)
            grid.operator('curve.primitive_bezier_curve_add', text='', icon='CURVE_BEZCURVE')
            grid.operator('curve.primitive_bezier_circle_add', text='', icon='CURVE_BEZCIRCLE')
            grid.operator('curve.primitive_nurbs_curve_add', text='', icon='CURVE_NCURVE')
            grid.operator('curve.primitive_nurbs_circle_add', text='', icon='CURVE_NCIRCLE')
            grid.operator('curve.primitive_nurbs_path_add', text='', icon='CURVE_PATH')
            grid.operator('curve.simple', text='', icon='SEQ_CHROMA_SCOPE')
            #Add Surface
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Surface:', icon='OUTLINER_OB_SURFACE')
            col = box.column(align=True)
            row = col.row(align=True)
            grid = col.grid_flow(columns=3, align=True)
            grid.operator('surface.primitive_nurbs_surface_curve_add', text='', icon='SURFACE_NCURVE')
            grid.operator('surface.primitive_nurbs_surface_circle_add', text='', icon='SURFACE_NCIRCLE')
            grid.operator('surface.primitive_nurbs_surface_surface_add', text='', icon='SURFACE_NSURFACE')
            grid.operator('surface.primitive_nurbs_surface_cylinder_add', text='', icon='SURFACE_NCYLINDER')
            grid.operator('surface.primitive_nurbs_surface_sphere_add', text='', icon='SURFACE_NSPHERE')
            grid.operator('surface.primitive_nurbs_surface_torus_add', text='', icon='SURFACE_NTORUS')

            #Add Grease Pencil
            box = layout.box()
            col = box.column_flow(align=True)
            row = col.row(align=True)
            row.label(text='Other:', icon='COPY_ID')
            grid = box.grid_flow(align=True, columns=2)
            grid.operator('object.empty_add', text='Empty', icon='OUTLINER_OB_EMPTY')
            grid.operator('object.gpencil_add', text='GPencil', icon='OUTLINER_OB_GREASEPENCIL')
            grid.operator('object.text_add', text='Text', icon='OUTLINER_OB_FONT')
            grid.operator('mesh.primitive_gear', text='Gear', icon='PREFERENCES')

            #Add Light
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Render:', icon='RENDER_ANIMATION')
            grid = box.grid_flow(align=True, columns=3)
            grid.operator('object.light_add', text='', icon='LIGHT_SUN')
            grid.operator('object.trilighting', text='', icon='LIGHT_HEMI')
            grid.operator('object.lightprobe_add', text='', icon='OUTLINER_OB_LIGHTPROBE')
            col = box.column(align=True)
            grid = col.grid_flow(align=True, columns=2)
            grid.operator('object.camera_add', text='Camera', icon='OUTLINER_OB_CAMERA')
            grid.operator('object.speaker_add', text='Speaker', icon='OUTLINER_OB_SPEAKER')

            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Image:', icon='FILE_IMAGE')
            col = box.column(align=True)
            col.operator('import_image.to_plane', text='Image to Plane', icon='TEXTURE')
            col.operator('object.load_reference_image', text='Reference Image', icon='IMAGE_REFERENCE')
            col.operator('object.load_background_image', text='Background', icon='IMAGE_BACKGROUND')


        #EDIT_TAB
        if props.topbar_enums == 'EDIT_TAB':
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Selection:', icon='RESTRICT_SELECT_OFF')

            row = col.row(align=True)
            row.prop(props, 'selection_enums', icon_only=True, expand=True)

            if props.selection_enums == 'SELECT_VERT':
                row.label(text='Vertex')
            if props.selection_enums == 'SELECT_EDGE':
                row.label(text='Edge')
            if props.selection_enums == 'SELECT_FACE':
                row.label(text='Face')
            if props.selection_enums == 'SELECT_OBJECT':
                row.label(text='Object')
            if props.selection_enums == 'SELECT_ELEMEMT':
                row.label(text='Element')
            if props.selection_enums == 'SELECT_BORDER':
                row.label(text='Border')

            #Select option
            if props.selection_enums != 'SELECT_OBJECT':
                col = box.column(align=True)
                row = col.row(align=True)
                row.prop(props, 'selection_mode_extend', text='Extend', icon='TRACKER',  expand=True, toggle=True)
                row.prop(props, 'selection_mode_expand', text='Expand', icon='CON_OBJECTSOLVER',  expand=True, toggle=True)

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('mesh.select_mirror', text='Mirror', icon='MOD_MIRROR').extend = True
                row.operator('mesh.bdsm_select_similar', text='Similar', icon='SYSTEM')

                row = col.row(align=True)
                row.operator('mesh.select_less', text='Less', icon='REMOVE')
                row.operator('mesh.select_more', text='More', icon='ADD')

                split = box.split(align=False)
                col = split.column(align=True)
                grid = col.grid_flow(columns=1, align=True)
                grid.operator('mesh.loop_multi_select', text='Loop', icon='MOD_SCREW').ring = False

                grid = col.grid_flow(columns=2, align=True)
                op = grid.operator('mesh.bdsm_mesh_edge_select_loop_step', text='', icon='REMOVE')
                op.type = 'LOOP'
                op.less = True
                op.step = props.step
                op.dotgap = props.dotgap

                op = grid.operator('mesh.bdsm_mesh_edge_select_loop_step', text='', icon='ADD')
                op.type = 'LOOP'
                op.less = False
                op.step = props.step
                op.dotgap = props.dotgap


                col = split.column(align=True)
                grid = col.grid_flow(columns=1, align=True)
                grid.operator('mesh.loop_multi_select', text='Ring', icon='MOD_INSTANCE').ring = True
                grid = col.grid_flow(columns=2, align=True)
                op = grid.operator('mesh.bdsm_mesh_edge_select_loop_step', text='', icon='REMOVE')
                op.type = 'RING'
                op.less = True
                op.step = props.step
                op.dotgap = props.dotgap

                op = grid.operator('mesh.bdsm_mesh_edge_select_loop_step', text='', icon='ADD')
                op.type = 'RING'
                op.less = False
                op.step = props.step
                op.dotgap = props.dotgap


                col = box.column(align=True)
                row = col.row(align=True)
                row.prop(props, 'dotgap',  icon='CENTER_ONLY',toggle=True )
                row.prop(props, 'step')


            #[1]Edit Vertex
            if props.selection_enums == 'SELECT_VERT':
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Edit Vertex:', icon='VERTEXSEL')

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_extrude', text='Extrude', icon_value=get_icon_id("Extrude"))
                row.operator('mesh.bdsm_mesh_bevel', text='Bevel', icon_value=get_icon_id("AdjustBevel"))
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_connect', text='Connect', icon_value=get_icon_id("StarConnect"))
                row.operator('mesh.bdsm_mesh_split', text='Break', icon='MOD_PHYSICS')
                row = col.row(align=True)
                row.prop(props, 'tg_target_weld',text='Target', icon_value=get_icon_id('Target'), toggle=True)
                op = row.operator('mesh.remove_doubles', text='Weld', icon='AUTOMERGE_OFF')
                op.threshold = 0.01
                row = col.row(align=True)
                row.operator('transform.vert_crease', text='Crease', icon='MOD_THICKNESS')
                op = row.operator('view3d.bdsm_delete', text='Remove' , icon='X')
                op.hierarchy = False
                op.expand = False
                op.smart = False

            #[2]Edit Edge
            if props.selection_enums in ['SELECT_EDGE','SELECT_BORDER'] :
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Edit Edge:', icon='EDGESEL')
                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_extrude', text='Extrude', icon_value=get_icon_id("Extrude"))
                row.operator('mesh.bdsm_mesh_bevel', text='Bevel', icon_value=get_icon_id("AdjustBevel"))
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_connect', text='Connect', icon_value=get_icon_id("StarConnect"))
                row.operator('mesh.bdsm_mesh_split', text='Split', icon='MOD_PHYSICS')
                row = col.row(align=True)
                row.prop(props, 'tg_target_weld',text='Target', icon_value=get_icon_id('Target'), toggle=True)
                op =row.operator('mesh.remove_doubles', text='Weld', icon='AUTOMERGE_OFF')
                op.threshold = 0.01
                row = col.row(align=True)
                row.operator('mesh.bridge_edge_loops', text='Brigde',icon_value=get_icon_id("Brigde"))
                row.operator('mesh.subdivide', text='Divide' ,icon='SNAP_MIDPOINT')
                row = col.row(align=True)
                row = col.row(align=True)
                row.operator('transform.edge_slide', text='Edge Slide',icon='MOD_EDGESPLIT')
                row.operator('mesh.offset_edge_loops_slide', text='Edge Offset' ,icon='MOD_INSTANCE')
                row = col.row(align=True)
                row.operator('transform.edge_crease', text='Crease', icon='MOD_THICKNESS')
                op = row.operator('view3d.bdsm_delete', text='Remove' , icon='X')
                op.hierarchy = False
                op.expand = False
                op.smart = False

            #[3]Edit Face
            if props.selection_enums in ['SELECT_FACE','SELECT_ELEMEMT']:
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Edit Face:', icon='FACESEL')

                row = col.row(align=True)
                split = box.split(align=True, factor=0.43)
                col = split.column(align=True)
                grid = col.grid_flow(columns=1, align=True)
                grid.operator('mesh.bdsm_mesh_extrude', text='Extrude', icon_value=get_icon_id("Extrude"))

                col = split.column(align=True)
                grid = col.grid_flow(columns=5, align=True)
                grid.operator('mesh.bdsm_mesh_extrude_punchit', text='', icon_value=get_icon_id("PUNCHit"))
                grid.prop(props, 'extrude_mode', icon_only=True, expand=True, toggle=True)

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('mesh.poke', text='Poke', icon='MOD_TRIANGULATE')
                row.operator('mesh.bdsm_mesh_bevel', text='Bevel', icon_value=get_icon_id("AdjustBevel"))
                row = col.row(align=True)
                op = row.operator('mesh.inset', text='Inset', icon='FULLSCREEN_EXIT')
                op.use_outset = False
                op = row.operator('mesh.inset', text='Outset', icon='FULLSCREEN_ENTER')
                op.use_outset = True
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_face_inset_fillet', text='Fillet', icon='META_PLANE')
                row.operator('mesh.solidify', text='Shell', icon='MOD_SKIN')
                row = col.row(align=True)
                row.operator('mesh.bdsm_mesh_face_split_solidify', text='Solidify', icon='MOD_SOLIDIFY')
                row.operator('mesh.wireframe', text='Wireframe', icon='MOD_DECIM')
                row = col.row(align=True)
                row.operator('mesh.flip_normals', text='Flip normal', icon='ORIENTATION_NORMAL')
                row.operator('mesh.bdsm_mesh_split', text='Split', icon='MOD_PHYSICS')
                row = col.row(align=True)
                row.operator('mesh.subdivide', text='Subdive', icon='MOD_MULTIRES')
                row.operator('mesh.unsubdivide', text='Unsubdivide', icon='MESH_PLANE')
                row = col.row(align=True)
                row.operator('mesh.quads_convert_to_tris', text='To Tris', icon='MESH_ICOSPHERE')
                row.operator('mesh.tris_convert_to_quads', text='To Quads', icon='MESH_GRID')
                row = col.row(align=True)
                op = row.operator('mesh.separate', text='Detach', icon_value=get_icon_id('Detach'))
                op.type ='SELECTED'
                op = row.operator('view3d.bdsm_delete', text='Remove' , icon='X')
                op.hierarchy = False
                op.expand = False
                op.smart = False

            #[4]Edit Object
            if props.selection_enums == 'SELECT_OBJECT':
                #select object
                col = box.column(align=True)
                grid = col.grid_flow(columns=3, align=True)
                op = grid.operator('object.select_hierarchy', text='', icon='PARTICLE_DATA')
                op.direction = 'PARENT'
                op.extend = False
                op = grid.operator('object.select_hierarchy', text='', icon='MOD_PARTICLES')
                op.direction = 'CHILD'
                op.extend = False
                op = grid.operator('object.select_hierarchy', text='', icon='MOD_PARTICLE_INSTANCE')
                op.direction = 'CHILD'
                op.extend = True

                grid = col.grid_flow(columns=5, align=True)
                op = grid.operator('object.select_by_type', text='', icon='CAMERA_DATA')
                op.type = 'CAMERA'
                op = grid.operator('object.select_by_type', text='', icon='LIGHT_DATA')
                op.type = 'LIGHT'
                op = grid.operator('object.select_grouped', text='', icon='OUTLINER_OB_EMPTY')
                op.type = 'TYPE'
                op = grid.operator('object.select_linked', text='', icon='MATERIAL')
                op.type = 'MATERIAL'
                op = grid.operator('object.select_grouped', text='', icon='OUTLINER_COLLECTION')
                op.type = 'COLLECTION'

                col = box.column(align=True)
                grid = col.grid_flow(columns=3, align=True)
                #bpy.ops.bject.hide_view_set(ounselected=False)


                op = grid.operator('object.hide_view_clear', text='', icon='HIDE_OFF')
                op = grid.operator('object.hide_view_set', text='', icon='HIDE_ON')
                op.unselected = False
                op = grid.operator('object.hide_view_set', text='', icon='RESTRICT_SELECT_ON')
                op.unselected = True

                grid = col.grid_flow(columns=3, align=True)
                op = grid.operator('view3d.bdsm_object_select_lock', text='', icon='LOCKED')
                op.mode = 'LOCK'
                op = grid.operator('view3d.bdsm_object_select_lock', text='', icon='UNLOCKED')
                op.mode = 'UNLOCK'
                op = grid.operator('view3d.bdsm_object_select_lock', text='', icon='RESTRICT_SELECT_ON')
                op.mode = 'LOCK_UNSELECTED'

                #Edit Object
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Edit Object:', icon='SNAP_VOLUME')

                col = box.column(align=True)
                row = col.row(align=True)
                grid = col.grid_flow(columns=4, align=True)
                op = grid.operator('object.convert', text='', icon='OUTLINER_OB_MESH')
                op.target= 'MESH'
                op = grid.operator('object.convert', text='', icon='OUTLINER_OB_CURVE')
                op.target= 'CURVE'
                op = grid.operator('object.convert', text='', icon='OUTLINER_OB_GREASEPENCIL')
                op.target= 'GPENCIL'
                op = grid.operator('object.convert', text='', icon='OUTLINER_OB_CURVES')
                op.target= 'CURVES'

                col = box.column(align=True)
                grid = col.grid_flow(columns=4, align=True)
                grid.prop(props, 'rotate_step_enums', expand=True)
                row = col.row(align=True)
                op = row.operator('view3d.bdsm_transform_rotate_step', text='Rotate', icon='DRIVER_ROTATIONAL_DIFFERENCE')
                op.rad = props.rotate_rad_step
                row.prop(props, 'rotate_rad_step', text='')

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('object.move_to_collection', text='Move Collect', icon='COLLECTION_NEW')
                row.operator('collection.objects_remove', text='Remove Collect', icon='OUTLINER')
                row = col.row(align=True)
                op = row.operator('object.parent_set', text='Set Parent', icon='TRACKING_BACKWARDS')
                op.type = 'OBJECT'
                op.keep_transform = True
                op = row.operator('object.parent_clear', text='Clear Parent', icon='TRACKING_CLEAR_BACKWARDS')
                op.type = 'CLEAR_KEEP_TRANSFORM'

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('object.shade_smooth', text='Smooth', icon='MESH_UVSPHERE')
                row.operator('object.shade_flat', text='Flat', icon='MESH_ICOSPHERE')

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('object.join', text='Attack' , icon_value=get_icon_id('Attack'))
                op = row.operator('mesh.separate', text='Detach', icon_value=get_icon_id('Detach'))
                op.type = 'SELECTED'
                row = col.row(align=True)
                op = row.operator('mesh.bdsm_mesh_mirror_flip', text='Mirror', icon='MOD_MIRROR')
                op.mode = 'MIRROR'
                op = row.operator('mesh.bdsm_mesh_mirror_flip', text='Flip', icon='CON_SAMEVOL')
                op.mode = 'FLIP'
                row = col.row(align=True)
                op = row.operator('view3d.bdsm_object_collision', text='BBox', icon='MOD_MESHDEFORM')
                op.collision_type = 'BOX'
                op = row.operator('view3d.bdsm_object_collision', text='Convex', icon='CONSTRAINT')
                op.collision_type = 'CONVEX'
                row = col.row(align=True)
                row.operator('object.bdsm_object_bbox_match', text='BBox Match' , icon='FULLSCREEN_ENTER')

                #View
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='View Object:', icon='SCENE')
                row.prop(prefs, 'tg_relative', icon_only=True, toggle=True, icon='ORIENTATION_GIMBAL')
                icon = 'ToggleOFF'
                if prefs.tg_display_view:
                    icon = 'ToggleON'
                row.prop(prefs, 'tg_display_view', text='', emboss=False, icon_value=get_icon_id(icon))
                if prefs.tg_display_view:
                    row = col.row(align=True)
                    op = row.operator('view3d.view_selected', text='Selected')
                    op.use_all_regions = False
                    op = row.operator('view3d.view_all', text='All')
                    op.center = False
                    row = col.row(align=True)
                    row.operator('view3d.localview', text='Isolate')
                    row.operator('view3d.view_camera', text='Camera')
                    col.operator('mesh.bdsm_mesh_select_view', text='3 point')

                    row = box.row(align=True)
                    # First column
                    col = row.column(align=True)
                    col.label(text='')
                    op = col.operator('view3d.view_axis', text='Left', icon='TRIA_LEFT')
                    op.type = 'LEFT'
                    op.relative = prefs.tg_relative
                    op.align_active = False
                    # Second column
                    col = row.column(align=True)
                    op = col.operator('view3d.view_axis', text='Top', icon='TRIA_UP')
                    op.type = 'TOP'
                    op.relative = prefs.tg_relative
                    op.align_active = False
                    op = col.operator('view3d.view_axis', text='Front',)
                    op.type = 'FRONT'
                    op.relative = False
                    op.align_active = False
                    op = col.operator('view3d.view_axis', text='Bottom', icon='TRIA_DOWN')
                    op.type = 'LEFT'
                    op.relative = prefs.tg_relative
                    op.align_active = False
                    # Third column
                    col = row.column(align=True)
                    col.label(text='')
                    op = col.operator('view3d.view_axis', text='Right', icon='TRIA_RIGHT')
                    op.type = 'RIGHT'
                    op.relative = prefs.tg_relative
                    op.align_active = False

                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.operator('view3d.view_persportho', text='Pers/Orth', icon='VIEW_PERSPECTIVE')
                    row.operator('view3d.bdsm_view_axis', text='Orth Axis', icon='VIEW_ORTHO').contextual = False
                    row = col.row(align=True)
                    row.operator('view3d.fly', text='Fly', icon='MOD_SOFT')
                    row.operator('view3d.walk', text='Walk', icon='MOD_DYNAMICPAINT')



           # Edit Geometry
            if props.selection_enums != 'SELECT_OBJECT':
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Edit Geometry:', icon='LATTICE_DATA')
                icon = 'ToggleOFF'
                if prefs.tg_edit_geometry:
                    icon = 'ToggleON'
                row.prop(prefs, 'tg_edit_geometry', text='', emboss=False, icon_value=get_icon_id(icon))
                if prefs.tg_edit_geometry:
                    row = col.row(align=True)
                    row.operator('mesh.loopcut_slide', text='Swift Loop', icon_value=get_icon_id('SwiftLoop'))
                    row.operator('mesh.offset_edge_loops_slide', text='Offset loop', icon_value=get_icon_id('OffsetLoop'))
                    row = col.row(align=True)
                    row.operator('mesh.knife_tool', text='Cut', icon_value=get_icon_id('Cut'))
                    row.operator('mesh.bisect', text='QSlice', icon_value=get_icon_id('QSlice'))
                    row = col.row(align=True)
                    row.operator('mesh.fill', text='Fill', icon_value=get_icon_id('Fill'))
                    row.operator('mesh.fill_grid', text='Grid fill', icon_value=get_icon_id('GridFill'))
                    row = col.row(align=True)
                    op = row.operator('mesh.bdsm_mesh_mirror_flip', text='Mirror', icon_value=get_icon_id('Mirror'))
                    op.mode = 'MIRROR'
                    op = row.operator('mesh.bdsm_mesh_mirror_flip', text='Flip', icon_value=get_icon_id('Flip'))
                    op.mode = 'FLIP'
                    if props.selection_enums in ['SELECT_EDGE','SELECT_BORDER'] :
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_edge_roundifier', text='Roundifier',icon_value=get_icon_id('EdgeRoundifier'))
                        row.operator('mesh.bdsm_mesh_edge_shaft', text='Shaft',icon_value=get_icon_id('Shaft'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_edge_subdivide_loops', text='Subd-Loops', icon_value=get_icon_id('SubEdgeLoop'))
                        row.operator('mesh.bdsm_mesh_edge_length', text='Length',icon_value=get_icon_id('Length'))
                    if props.selection_enums in ['SELECT_FACE','SELECT_ELEMEMT']:
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_face_shape', text='Shape',icon_value=get_icon_id('FaceShape'))
                        row.operator('mesh.bdsm_mesh_face_plane', text='Make Plane',icon_value=get_icon_id('MakePlane'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_face_cut', text='Cut',icon_value=get_icon_id('FaceCut'))
                        row.operator('mesh.bdsm_mesh_face_fix_ngons', text='Fix N-Gons', icon_value=get_icon_id('ShowNgonsTris'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_face_regulator', text='Regulator', icon='VIEW_ORTHO')
                        row.operator('mesh.bdsm_mesh_face_cutter', text='Cutter', icon_value=get_icon_id('FaceCutter'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_face_gridmodeler', text='Grid Modeler', icon_value=get_icon_id('GridModeler'))
                        row.operator('mesh.bdsm_mesh_face_attach_align', text='Attack Algin', icon_value=get_icon_id('AttackAlign'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_face_quick_bridge', text='Quick Brigde', icon_value=get_icon_id('QuickBrigde'))
                        row.operator('mesh.bdsm_mesh_face_safe_inset', text='Safe Inset', icon_value=get_icon_id('SafeInset'))
                        row = col.row(align=True)
                        row.operator('mesh.bdsm_mesh_surface_inflate', text='Surface Inflate', icon_value=get_icon_id('SurfaceInflate'))
                        row.operator('mesh.bdsm_mesh_face_visual_axis', text='Visual Axis', icon_value=get_icon_id('VisualAxis'))
                    row = col.row(align=True)
                    row.operator('view3d.bdsm_duplicate', text='Duplicate', icon_value=get_icon_id('Duplicate'))
                    row.operator('mesh.bdsm_detach', text='Detach', icon_value=get_icon_id('Detach'))
                    row = col.row(align=True)
                    row.operator('mesh.bdsm_mesh_deselect_boundary', text='Un-Border', icon_value=get_icon_id('Dice'))
                    row.operator('mesh.dissolve_limited', text='Dissolve Limited', icon_value=get_icon_id('Voxelize'))
                    row = col.row(align=True)
                    op = row.operator('view3d.bdsm_delete', text='Delete', icon='X')
                    op.hierarchy = True
                    op.expand = False
                    op.smart = False
                    op = row.operator('view3d.bdsm_delete', text='Dissolve', icon_value=get_icon_id('Dissolve'))
                    op.hierarchy = False
                    op.expand = False
                    op.smart = True

                #FLow
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Flow Tool:', icon='FORCE_FORCE')
                icon = 'ToggleOFF'
                if prefs.tg_edit_geometry_flow:
                    icon = 'ToggleON'
                row.prop(prefs, 'tg_edit_geometry_flow', text='', emboss=False, icon_value=get_icon_id(icon))
                if prefs.tg_edit_geometry_flow:
                    # split = col.split(align=False)
                    col = box.column(align=True)
                    col.operator('mesh.bdsm_mesh_smooth_laplacian', text='Smooth Laplacian', icon_value=get_icon_id('SmoothLaplacian'))
                    col.operator('mesh.bdsm_mesh_smooth_inflate', text='Smooth Inflate', icon_value=get_icon_id('SmoothInflate'))
                    col.operator('mesh.bdsm_mesh_smooth_volume', text='Smooth Volume', icon_value=get_icon_id('SmoothVolume'))
                    col = box.column(align=True)
                    if props.selection_enums == 'SELECT_VERT':
                        col.operator('mesh.bdsm_mesh_vert_random', text='Vertex Random', icon_value=get_icon_id('VertexRandom'))
                        col.operator('mesh.bdsm_mesh_vertex_curve', text='Vertex Curve', icon_value=get_icon_id('VertexCurve'))
                    if props.selection_enums in ['SELECT_EDGE','SELECT_BORDER'] :
                        col.operator('mesh.bdsm_mesh_edge_flow', text='Edge Flow', icon_value=get_icon_id('EdgeFlow'))
                        col.operator('mesh.bdsm_mesh_edge_linear', text='Edge Linear', icon_value=get_icon_id('EdgeLinear'))
                        col.operator('mesh.bdsm_mesh_edge_curve', text='Edge Curve', icon_value=get_icon_id('EdgeCurve'))
                    col.operator('mesh.bdsm_mesh_relax', text='Relax', icon_value=get_icon_id('Relax'))

                #Merge
                box = layout.box()
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Merg:', icon='PARTICLES')
                icon = 'ToggleOFF'
                if prefs.tg_edit_geometry_merg:
                    icon = 'ToggleON'
                row.prop(prefs, 'tg_edit_geometry_merg', text='', emboss=False, icon_value=get_icon_id(icon))
                if prefs.tg_edit_geometry_merg:
                    grid = col.grid_flow(columns=3, align=True)
                    grid.scale_y = 1.25
                    op = grid.operator('mesh.merge', text='', icon='PIVOT_CURSOR')
                    op.type = 'CURSOR'
                    op = grid.operator('mesh.merge', text='', icon='FULLSCREEN_EXIT')
                    op.type = 'COLLAPSE'
                    op = grid.operator('mesh.merge', text='', icon='TRACKER')
                    op.type = 'CENTER'
                    grid = col.grid_flow(columns=3, align=True)
                    grid.operator('mesh.bdsm_mesh_merge_mouse', text='', icon='MOUSE_MOVE')
                    grid.operator('mesh.bdsm_mesh_merge_active', text='', icon='PIVOT_ACTIVE')
                    grid.operator('mesh.bdsm_mesh_merge_nearselected', text='', icon='DRIVER_DISTANCE')

        #MODIFY_TAB
        if props.topbar_enums == 'MODIFY_TAB':
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(props, 'tg_modifier_apply',text='Modifier', icon='MODIFIER', toggle=True)
            row.operator('object.apply_all_modifiers', text='Apply All', icon='IMPORT')
            row = col.row(align=True)
            row.operator('wm.toggle_all_show_expanded', text='Stack', icon='FULLSCREEN_ENTER')
            row.operator('object.delete_all_modifiers', text='Delete All', icon='X')
            col = box.column(align=True)
            col.operator('wm.call_menu', text='Add Modifier', icon='ADD').name = 'OBJECT_MT_modifier_add'

            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Modify list:', icon='MODIFIER_DATA')
            icon = 'ToggleOFF'
            if prefs.tg_modifier_list:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_modifier_list', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_modifier_list:
                #Generate``
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Generate', icon='PROPERTIES')
                row = col.row(align=True)
                # bpy.ops.object.modifier_add(type='BEVEL')

                row.operator('object.modifier_add', text='Bevel', icon='MOD_BEVEL').type = 'BEVEL'
                row.operator('object.modifier_add', text='Subdivision', icon='MOD_SUBSURF').type = 'SUBSURF'

                row = col.row(align=True)
                row.operator('object.modifier_add', text='Mirror', icon='MOD_MIRROR').type = 'MIRROR'
                row.operator('object.modifier_add', text='Solidify', icon='MOD_SOLIDIFY').type = 'SOLIDIFY'

                row = col.row(align=True)
                row.operator('object.modifier_add', text='Remesh', icon='MOD_REMESH').type = 'REMESH'
                row.operator('object.modifier_add', text='Boolean', icon='MOD_BOOLEAN').type = 'BOOLEAN'


                row = col.row(align=True)
                row.operator('object.modifier_add', text='Skin', icon='MOD_SKIN').type = 'SKIN'
                row.operator('object.modifier_add', text='Screw', icon='MOD_SCREW').type = 'SCREW'

                row = col.row(align=True)
                row.operator('object.modifier_add', text='Geo Node', icon='GEOMETRY_NODES').type = 'NODES'
                row.operator('object.modifier_add', text='Array', icon='MOD_ARRAY').type = 'ARRAY'
                #Deform
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Deform', icon='MOD_ENVELOPE')
                row = col.row(align=True)
                row.operator('object.modifier_add', text='Lattice', icon='MOD_LATTICE').type = 'LATTICE'
                row.operator('object.modifier_add', text='Curve', icon='MOD_CURVE').type = 'CURVE'
                row = col.row(align=True)
                row.operator('object.modifier_add', text='SimpleDeform', icon='MOD_SIMPLEDEFORM').type = 'SIMPLE_DEFORM'
                row.operator('object.modifier_add', text='Mesh Deform', icon='MOD_MESHDEFORM').type = 'MESH_DEFORM'
                row = col.row(align=True)
                row.operator('object.modifier_add', text='Surface Deform', icon='MOD_MESHDEFORM').type = 'SURFACE_DEFORM'
                row.operator('object.modifier_add', text='Shirnkwrap', icon='MOD_SHRINKWRAP').type = 'SHRINKWRAP'
                row = col.row(align=True)
                row.operator('object.modifier_add', text='Smooth', icon='MOD_SMOOTH').type = 'SMOOTH'
                row.operator('object.modifier_add', text='Displace', icon='MOD_DISPLACE').type = 'DISPLACE'

                #Modify

                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text='Modify', icon='NORMALIZE_FCURVES')
                row = col.row(align=True)
                row.operator('object.modifier_add', text='Weighted Normal', icon='MOD_NORMALEDIT').type = 'WEIGHTED_NORMAL'
                row.operator('object.modifier_add', text='Normal Edit', icon='MOD_NORMALEDIT').type = 'NORMAL_EDIT'

            #Subdivision Tool
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=False)
            row.label(text='Subdivision Tool:', icon='MOD_SUBSURF')
            icon = 'ToggleOFF'
            if prefs.tg_modifier_subdiv:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_modifier_subdiv', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_modifier_subdiv:
                row = col.row(align=False)
                row.operator('view3d.bdsm_modifier_subdivide', text='Subdivide Toggle', icon='HIDE_OFF').level_mode = "TOGGLE"
                #row = col.row(align=True)
                row = col.row(align=True)
                row.operator('view3d.bdsm_modifier_subdivide_step', text='Viewport +1').step_up = True
                row.operator('view3d.bdsm_modifier_subdivide_step', text='Viewport -1').step_up = False
                row = col.row(align=True)
                row.prop(props, 'vp_level', text='Viewport')
                row = col.row(align=True)
                row.prop(props, 'render_level', text='Render')
                row = col.row(align=True)
                row.operator('view3d.bdsm_modifier_subdivide', text='Set VP LV').level_mode = "VIEWPORT"
                row.operator('view3d.bdsm_modifier_subdivide', text='Set Render Lv').level_mode = "RENDER"
                row = col.row(align=True)
                row.alignment = "LEFT"
                row.prop(props, 'boundary_smooth', text='Boundary')
                col.separator(factor=0.5)
                col.prop(props, 'optimal_display', text='Use Optimal Display')
                col.prop(props, 'limit_surface', text='Use Limit Surface')
                col.prop(props, 'on_cage', text='On Cage')
                col.prop(props, 'subd_autosmooth')
                col.prop(props, 'flat_edit', text='Flat Shade when off')

        #ORIGIN_TAB
        if props.topbar_enums == 'ORIGIN_TAB':
            #Transform
            col = layout.column(align=True)
            row = col.row(align=True)
            col = row.column_flow(align=True)
            col.operator('mesh.bdsm_transform_move', text='', icon='EMPTY_ARROWS')
            col.operator('mesh.bdsm_transform_rotate', text='', icon='ORIENTATION_GIMBAL')
            col.operator('mesh.bdsm_transform_scale', text='', icon='CON_SIZELIKE')
            col.scale_y = 1.4
            #Pivot + Orientations
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Pivot:', icon='PIVOT_BOUNDBOX')
            # props.oriental_enums = 'ORIENT_' + context.scene.transform_orientation_slots[0].type
            # props.pivot_enums = 'PIVOT_' + context.scene.tool_settings.transform_pivot_point
            sence_orient = context.scene.transform_orientation_slots[0]
            icon = ''
            if sence_orient.type == 'CURSOR':
                icon = 'ORIENTATION_CURSOR'
            if sence_orient.type == 'GLOBAL':
                icon = 'ORIENTATION_GLOBAL'
            if sence_orient.type == 'LOCAL':
                icon = 'ORIENTATION_LOCAL'
            if sence_orient.type == 'NORMAL':
                icon = 'ORIENTATION_NORMAL'
            if sence_orient.type == 'GIMBAL':
                icon = 'ORIENTATION_GIMBAL'
            if sence_orient.type == 'VIEW':
                icon = 'ORIENTATION_VIEW'
            if sence_orient.type == 'PARENT':
                icon = 'ORIENTATION_PARENT'
            if context.mode == 'OBJECT':
                row.operator('view3d.bdsm_oriental_set', text='', icon=icon).mode = 'CYCLE'
            else:
                row.operator('view3d.bdsm_oriental_set', text='', icon=icon).mode = 'TYPE_1'
            icon = ''
            if tool_props.transform_pivot_point == 'BOUNDING_BOX_CENTER':
                icon = 'PIVOT_BOUNDBOX'
            if tool_props.transform_pivot_point == 'CURSOR':
                icon = 'PIVOT_CURSOR'
            if tool_props.transform_pivot_point == 'INDIVIDUAL_ORIGINS':
                icon = 'PIVOT_INDIVIDUAL'
            if tool_props.transform_pivot_point == 'MEDIAN_POINT':
                icon = 'PIVOT_MEDIAN'
            if tool_props.transform_pivot_point == 'ACTIVE_ELEMENT':
                icon = 'PIVOT_ACTIVE'
            if context.mode == 'OBJECT':
                row.operator('view3d.bdsm_pivot_set', text='', icon=icon).mode = 'CYCLE'
            else:
                row.operator('view3d.bdsm_pivot_set', text='', icon=icon).mode = 'TYPE_3'
            col = box.column(align=True)
            grid = col.grid_flow(columns=6, align=True, row_major=True)
            grid.prop(tool_props, 'transform_pivot_point', icon_only=True, expand=True)
            grid.prop_enum(sence_orient, 'type','CURSOR',text='')
            grid.prop_enum(sence_orient, 'type','GLOBAL',text='')
            grid.prop_enum(sence_orient, 'type','LOCAL',text='')
            grid.prop_enum(sence_orient, 'type','NORMAL',text='')
            grid.prop_enum(sence_orient, 'type','GIMBAL',text='')
            grid.prop_enum(sence_orient, 'type','VIEW',text='')
            grid.prop_enum(sence_orient, 'type','PARENT',text='')

            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text=''.join([props.alignbar_enums,':']).replace('_TAB', '').capitalize(), icon='MOD_ARRAY')
            row.prop(props, 'tg_show_origin', icon='OBJECT_ORIGIN', toggle=True, expand=True, icon_only=True)
            row.operator('view3d.bdsm_origin_set', text='', icon='TRANSFORM_ORIGINS').set = True
            col = box.column(align=True)
            col.separator(factor=0.05)
            split = col.split(align=False,factor=0.18)
            col = split.column(align=False)
            col.scale_y = 1.25
            col.prop(props,'alignbar_enums',icon_only=True, expand=True)
            col.operator('object.bdsm_object_drop_it', text='', icon='SORT_ASC')
            col = split.column(align=True)
            col.alignment = "LEFT"
            col.scale_y = 1.25
            if props.alignbar_enums == 'ORIGIN_TAB':
                col.operator('object.origin_set', text='Origin to Cursor', icon='PIVOT_CURSOR').type = 'ORIGIN_CURSOR'
                col.operator('object.origin_set', text='Origin to Object', icon='OUTLINER_OB_MESH').type = 'ORIGIN_GEOMETRY'
                col.operator('object.origin_set', text='Origin to Volume', icon='OUTLINER_OB_EMPTY').type = 'ORIGIN_CENTER_OF_VOLUME'
                col.operator('object.origin_set', text='Origin to Mass', icon='OUTLINER_OB_SURFACE').type = 'ORIGIN_CENTER_OF_MASS'
            if props.alignbar_enums == 'CURSOR_TAB':
                col.operator('view3d.snap_cursor_to_center', text='Cursor to Zero', icon='ORIENTATION_CURSOR')
                col.operator('view3d.snap_cursor_to_selected', text='Cursor to Selected', icon='PIVOT_MEDIAN')
                col.operator('view3d.snap_cursor_to_active', text='Cursor to Active', icon='PIVOT_ACTIVE')
                col.operator('view3d.snap_cursor_to_grid', text='Cursor to Grid', icon='GRID')
            if props.alignbar_enums == 'OBJECT_TAB':
                col.operator('object.origin_set', text='Object to Origin', icon='OBJECT_ORIGIN').type = 'GEOMETRY_ORIGIN'
                col.operator('view3d.snap_selected_to_cursor', text='Object to Cursor', icon='CURSOR').use_offset = False
                col.operator('view3d.snap_selected_to_cursor', text='Object to Cursor Keep offsset', icon='PIVOT_CURSOR').use_offset = True
                col.operator('view3d.snap_selected_to_active', text='Object to Acitve', icon='PIVOT_ACTIVE')

            #Snap Tools
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=False)
            row.label(text='Snap Tools:', icon='SNAP_ON')
            row.prop(tool_props, 'use_snap', toggle=True, expand=True, icon_only=True)
            icon = 'ToggleOFF'
            if prefs.tg_origin_snap:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_origin_snap', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_origin_snap:
                col = box.column(align=True)
                split = col.split(align=False, factor=0.18)
                col = split.column(align=False)
                col.scale_y = 1.25
                col.prop(tool_props,'snap_elements',icon_only=True, expand=True)
                col.prop(props,'record_snap', icon_value=get_icon_id('Save'),icon_only=True, expand=True)
                col = split.column(align=False)
                col.alignment = "LEFT"
                col.scale_y = 1.25
                grid = col.grid_flow(columns=4, align=True)
                grid.prop_enum(tool_props,'snap_target','CLOSEST',text='', icon='FORCE_LENNARDJONES')
                grid.prop_enum(tool_props,'snap_target','CENTER',text='', icon='PROP_ON')
                grid.prop_enum(tool_props,'snap_target','MEDIAN',text='',icon='PIVOT_MEDIAN')
                grid.prop_enum(tool_props,'snap_target','ACTIVE',text='',icon='PIVOT_ACTIVE')
                col.prop(tool_props,'use_snap_grid_absolute', text='Absolute Grid',expand=True, toggle=True, icon='GRID')
                grid = col.grid_flow(columns=3, align=True)
                grid.prop(tool_props, 'use_snap_translate', icon='EMPTY_ARROWS', toggle=True, icon_only=True)
                grid.prop(tool_props, 'use_snap_rotate', icon='ORIENTATION_GIMBAL', toggle=True, icon_only=True)
                grid.prop(tool_props, 'use_snap_scale', icon='CON_SIZELIKE', toggle=True, icon_only=True)
                col = col.column(align=True)
                col.scale_y = 0.99
                col.prop(tool_props,'use_snap_align_rotation', text='Align Rotation',expand=True)
                col.prop(tool_props,'use_snap_backface_culling',expand=True)
                col.prop(tool_props,'use_snap_peel_object',expand=True)
                col.prop(tool_props,'use_snap_self',text='Include Active', icon='EDITMODE_HLT',expand=True, toggle=True)
                col.prop(tool_props,'use_snap_edit',text='Include Edited', icon='OUTLINER_DATA_MESH',expand=True, toggle=True)
                col.prop(tool_props,'use_snap_nonedit',text='Include Non-Edited', icon='OUTLINER_OB_MESH',expand=True, toggle=True)
                col.prop(tool_props,'use_snap_selectable',text='Exclude Non-Selectable', icon='RESTRICT_SELECT_OFF',expand=True, toggle=True)
                col = box.column(align=True)
                grid = col.grid_flow(columns=6, align=True)
                grid.scale_y = 1.25
                snap_mode = 'LOAD'
                if props.record_snap:
                    snap_mode = 'SAVE'
                grid.operator('view3d.bdsm_snap_tool', text='1').mode = snap_mode+'_1'
                grid.operator('view3d.bdsm_snap_tool', text='2').mode = snap_mode+'_2'
                grid.operator('view3d.bdsm_snap_tool', text='3').mode = snap_mode+'_3'
                grid.operator('view3d.bdsm_snap_tool', text='4').mode = snap_mode+'_4'
                grid.operator('view3d.bdsm_snap_tool', text='5').mode = snap_mode+'_5'
                grid.operator('view3d.bdsm_snap_tool', text='6').mode = snap_mode+'_6'

        #DIPSPLAY_TAB
        if props.topbar_enums == 'DIPSPLAY_TAB':
            #Shading
            shading = VIEW3D_PT_shading.get_shading(context)
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Shading:', icon='SHADING_TEXTURE')
            if prefs.tg_display_shading:
                if shading.type == 'SOLID' and shading.light == 'STUDIO' or shading.type == 'MATERIAL' or shading.type == 'RENDERED':
                    row.operator("preferences.studiolight_show", text="", icon='PREFERENCES')
                elif shading.type == 'SOLID' and shading.light == 'MATCAP':
                    row.operator("view3d.toggle_matcap_flip", text="", icon='ARROW_LEFTRIGHT')
                    row.operator("preferences.studiolight_show", text="", icon='PREFERENCES')
            icon = 'ToggleOFF'
            if prefs.tg_display_shading:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_shading', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_shading:
                # if shading.type == 'SOLID' and shading.light == 'STUDIO' or shading.type == 'MATERIAL' or shading.type == 'RENDERED':
                #     row.operator("preferences.studiolight_show", text="", icon='PREFERENCES')
                # elif shading.type == 'SOLID' and shading.light == 'MATCAP':
                #     row.operator("view3d.toggle_matcap_flip", text="", icon='ARROW_LEFTRIGHT')
                #     row.operator("preferences.studiolight_show", text="", icon='PREFERENCES')

                obj = context.active_object
                object_mode = 'OBJECT' if obj is None else obj.mode
                has_pose_mode = (
                    (object_mode == 'POSE') or
                    (object_mode == 'WEIGHT_PAINT' and context.pose_object is not None)
                )
                if has_pose_mode:
                    draw_depressed = view.overlay.show_xray_bone
                elif view.shading.type == 'WIREFRAME':
                    draw_depressed = view.shading.show_xray_wireframe
                else:
                    draw_depressed = view.shading.show_xray

                col = box.column(align=True)
                row = col.row(align=False)
                row.operator('view3d.toggle_xray', text='XRay', icon='XRAY', depress=draw_depressed)
                row.prop(view.shading, "type", text="", expand=True)

                shading = VIEW3D_PT_shading.get_shading(context)
                if shading.type == 'SOLID':
                    col = box.column(align=True)
                    row = col.row()
                    row.prop(shading, "light", expand=True)
                    col = box.column()
                    row = col.row()
                    if shading.light == 'STUDIO':
                        system = context.preferences.system

                        if not system.use_studio_light_edit:
                            row.scale_y = 0.6  # smaller studiolight preview
                            row.template_icon_view(shading, "studio_light", scale_popup=3.0)
                        else:
                            row.prop(system, "use_studio_light_edit",text="Disable Studio Light Edit", icon='NONE',toggle=True,)
                        col = box.column()
                        row = col.row()
                        row.prop(shading, "use_world_space_lighting", text="", icon='WORLD', toggle=True)
                        row = row.row()
                        row.active = shading.use_world_space_lighting
                        row.prop(shading, "studiolight_rotate_z", text="Rotation")
                    elif shading.light == 'MATCAP':
                        row.scale_y = 0.6  # smaller matcap preview
                        row.template_icon_view(shading, "studio_light", scale_popup=3.0)
                elif shading.type == 'MATERIAL':
                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.prop(shading, "use_scene_lights", toggle=True)
                    row.prop(shading, "use_scene_world", toggle=True)

                    col = box.column()
                    row = col.row()
                    if not shading.use_scene_world:
                        row.scale_y = 0.6
                        row.template_icon_view(shading, "studio_light", scale_popup=3)

                        col = box.column()
                        row = col.row()
                        row.prop(shading, "use_studiolight_view_rotation", text="", icon='WORLD', toggle=True)
                        row = row.row()
                        row.prop(shading, "studiolight_rotate_z", text="Rotation")

                        col = box.column()
                        col.prop(shading, "studiolight_intensity")
                        col.prop(shading, "studiolight_background_alpha")
                        col.prop(shading, "studiolight_background_blur")
                elif shading.type == 'RENDERED':
                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.prop(shading, "use_scene_lights_render", toggle=True)
                    row.prop(shading, "use_scene_world_render", toggle=True)

                    col = box.column()
                    row = col.row()
                    if not shading.use_scene_world_render:

                        row.scale_y = 0.6
                        row.template_icon_view(shading, "studio_light", scale_popup=3)

                        col = box.column()
                        row = col.row()
                        row.prop(shading, "studiolight_rotate_z", text="Rotation")
                        col = box.column()
                        col.prop(shading, "studiolight_intensity")
                        col.prop(shading, "studiolight_background_alpha")
                        col.prop(shading, "studiolight_background_blur")

                col = box.column(align=True)
                col.prop(view.shading,'wireframe_color_type', text='',icon='SHADING_WIRE')
                if shading.type == 'SOLID':
                    col = box.column(align=True)
                    col.prop(view.shading,'background_type', text='',icon='IMAGE_BACKGROUND')
                    if view.shading.background_type == 'VIEWPORT':
                        col.prop(view.shading,'background_color', text='',icon='EYEDROPPER')

                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.label(text='Color:', icon='COLOR')
                    grid = col.grid_flow(columns=6, align=True, row_major=True)
                    grid.prop_enum(view.shading,'color_type','MATERIAL', icon='MATERIAL', text='')
                    grid.prop_enum(view.shading,'color_type','OBJECT', icon='OUTLINER_OB_MESH', text='')
                    grid.prop_enum(view.shading,'color_type','VERTEX', icon='OUTLINER', text='')
                    grid.prop_enum(view.shading,'color_type','SINGLE', icon='PROP_OFF', text='')
                    grid.prop_enum(view.shading,'color_type','RANDOM', icon='FILE_3D', text='')
                    grid.prop_enum(view.shading,'color_type','TEXTURE', icon='TEXTURE', text='')

                if shading.type in {'MATERIAL','RENDERED'}:
                    col.prop(view.shading,'render_pass', text='',icon='RESTRICT_RENDER_OFF')
                    col.prop(view.shading,'use_compositor', text='',icon='FILE_IMAGE')

                box = col.box()
                col = box.column(align=True)
                row = col.row(align=False)
                if shading.type == 'SOLID':
                    row = col.row(align=True)
                    row.prop(shading, "show_backface_culling")

                if shading.type == 'WIREFRAME':
                    row = col.row(align=True)
                    row.prop(shading, "show_xray_wireframe", text="")
                    row = row.row()
                    row.active = shading.show_xray_wireframe
                    row.prop(shading, "xray_alpha_wireframe", text="X-Ray")
                elif shading.type == 'SOLID':
                    row = col.row(align=True)
                    row.prop(shading, "show_xray", text="")
                    row = row.row()
                    row.active = shading.show_xray
                    row.prop(shading, "xray_alpha", text="X-Ray")
                    # X-ray mode is off when alpha is 1.0
                    xray_active = shading.show_xray and shading.xray_alpha != 1

                    row = col.row(align=True)
                    row.prop(shading, "show_shadows", text="")
                    row.active = not xray_active
                    row = row.row(align=True)
                    row.active = shading.show_shadows
                    row.prop(shading, "shadow_intensity", text="Shadow")
                    row.popover(
                        panel="VIEW3D_PT_shading_options_shadow",
                        icon='PREFERENCES',
                        text="",
                    )

                    row = col.row()
                    row.active = not xray_active
                    row.prop(shading, "show_cavity")

                    if shading.show_cavity and not xray_active:
                        row.prop(shading, "cavity_type", text="Type")

                        if shading.cavity_type in {'WORLD', 'BOTH'}:
                            col.label(text="World Space")
                            sub = col.row(align=True)
                            sub.prop(shading, "cavity_ridge_factor", text="Ridge")
                            sub.prop(shading, "cavity_valley_factor", text="Valley")
                            sub.popover(
                                panel="VIEW3D_PT_shading_options_ssao",
                                icon='PREFERENCES',
                                text="",
                            )

                        if shading.cavity_type in {'SCREEN', 'BOTH'}:
                            col.label(text="Screen Space")
                            sub = col.row(align=True)
                            sub.prop(shading, "curvature_ridge_factor", text="Ridge")
                            sub.prop(shading, "curvature_valley_factor", text="Valley")

                    row = col.row()
                    row.active = not xray_active
                    row.prop(shading, "use_dof", text="Depth of Field")

                if shading.type in {'WIREFRAME', 'SOLID'}:
                    row = col.row(align=False)
                    row.prop(shading, "show_object_outline")
                    sub = row.row()
                    sub.active = shading.show_object_outline
                    sub.prop(shading, "object_outline_color", text="")

                if shading.type == 'SOLID':
                    row = col.row()
                    if shading.light in {'STUDIO', 'MATCAP'}:
                        row.active = shading.selected_studio_light.has_specular_highlight_pass
                        row.prop(shading, "show_specular_highlight", text="Specular Lighting")

            #Overlay
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=False)
            row.label(text='Overlay:', icon='OVERLAY')

            row.prop(view.overlay, 'show_overlays', text='', toggle=True, icon='OVERLAY')
            icon = 'ToggleOFF'
            if prefs.tg_display_overlay:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_overlay', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_overlay:
                col = box.column(align=False)
                col.enabled = context.space_data.overlay.show_overlays
                row = col.row(align=True)
                row.label(text='Guide:', icon='MENU_PANEL')
                row.prop(view.overlay, 'show_axis_x', text='', toggle=True, icon_value=get_icon_id('MoveX'))
                row.prop(view.overlay, 'show_axis_y', text='', toggle=True, icon_value=get_icon_id('MoveY'))
                row.prop(view.overlay, 'show_axis_z', text='', toggle=True, icon_value=get_icon_id('MoveZ'))
                grid = col.grid_flow(columns=6, align=True, row_major=True)
                grid.prop(view.overlay,'show_ortho_grid', text='Gird', icon='VIEW_ORTHO', icon_only=True)
                grid.prop(view.overlay,'show_floor', text='Ground', icon='VIEW_PERSPECTIVE', icon_only=True)
                grid.prop(view.overlay,'show_cursor', text='Cursor', icon='PIVOT_CURSOR', icon_only=True)
                grid.prop(view.overlay,'show_annotation', text='Draw', icon='LINE_DATA', icon_only=True)
                grid.prop(view.overlay,'show_stats', text='Tris', icon='MESH_ICOSPHERE', icon_only=True)
                grid.prop(view.overlay,'show_text', text='Info', icon='INFO', icon_only=True)

                col = box.column()
                col.enabled = context.space_data.overlay.show_overlays
                col.label(text='Geometry:', icon='MONKEY')
                row = col.row(align=True)
                row.prop(view.overlay, 'show_wireframes', text='', icon='SHADING_WIRE')
                sub = row.row(align=True)
                sub.active = view.overlay.show_wireframes or view.shading.type == 'WIREFRAME'
                sub.prop(view.overlay, "wireframe_threshold", text="Wireframe")
                sub.prop(view.overlay, "wireframe_opacity", text="Opacity")

                row = col.row(align=True)
                row.prop(view.overlay, 'show_viewer_attribute',text='', icon='OUTLINER')
                sub = row.row(align=True)
                sub.active = view.overlay.show_viewer_attribute
                sub.prop(view.overlay, "viewer_attribute_opacity", text="Opacity")

                row = col.row(align=True)
                row.prop(view.overlay, 'show_face_orientation', text='Face Oriental', icon='NORMALS_FACE')
                col = box.column()
                col.enabled = context.space_data.overlay.show_overlays
                row = col.row(align=True)
                row.prop(view, 'show_reconstruction', text='Motion Tracking')
                if view.show_reconstruction:

                    box = col.box()
                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.prop(view, 'show_camera_path', text='Camera', icon='CON_CAMERASOLVER')
                    row.prop(view, 'show_bundle_names', text='Bundle', icon='PACKAGE')
                    row = col.row(align=True)
                    row.prop(view, 'tracks_display_type', text='')
                    row = col.row(align=True)
                    row.prop(view, 'tracks_display_size', text='Size',)

            #Overlay Edit Mesh
            box = layout.box()

            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Overlay Edit:', icon='EDITMODE_HLT')
            icon = 'ToggleOFF'
            if prefs.tg_display_overlay_edit_mesh:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_overlay_edit_mesh', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_overlay_edit_mesh:
                is_any_solid_shading = not (view.shading.show_xray or (view.shading.type == 'WIREFRAME'))
                col = box.column()
                col.enabled = context.mode == 'EDIT_MESH'
                row = col.row(align=True)
                row.active = is_any_solid_shading


                split = col.split(align=False, factor=0.18)
                col = split.column(align=True)
                col.scale_y = 1.25

                col.prop(view.overlay, "show_edges", text="" , icon='EDGESEL')
                col.prop(view.overlay, "show_faces", text="", icon='FACESEL')
                col.prop(view.overlay, "show_face_center", text="", icon='SNAP_FACE_CENTER')

                col.separator(factor=0.5)
                col.prop(view.overlay, "show_edge_crease", text="", toggle=True, icon='PARTICLE_PATH')
                col.prop(view.overlay, "show_edge_sharp", text="", text_ctxt=i18n_contexts.plural, toggle=True, icon='MOD_EDGESPLIT')
                col.prop(view.overlay, "show_edge_bevel_weight", text="", toggle=True, icon='MOD_BEVEL')
                col.prop(view.overlay, "show_edge_seams", text="", toggle=True, icon='FCURVE')
                col = split.column_flow(align=False)
                grid = col.grid_flow(columns=3, align=True)
                grid.scale_y = 1.25
                grid.prop(view.overlay, "show_vertex_normals", text="", icon='NORMALS_VERTEX')
                grid.prop(view.overlay, "show_split_normals", text="", icon='NORMALS_VERTEX_FACE')
                grid.prop(view.overlay, "show_face_normals", text="", icon='NORMALS_FACE')
                row = col.row(align=True)
                row.active = view.overlay.show_vertex_normals or view.overlay.show_face_normals or view.overlay.show_split_normals
                if view.overlay.use_normals_constant_screen_size:
                    row.prop(view.overlay, "normals_constant_screen_size", text="Size")
                else:
                    row.prop(view.overlay, "normals_length", text="Size")
                row.prop(view.overlay, "use_normals_constant_screen_size", text="", icon='FIXED_SIZE')
                col = col.box()
                #Measurement
                col = col.column(align=True)
                col.label(text="Measurement:")
                col.prop(view.overlay, "show_extra_edge_length", text="Edge Length")
                col.prop(view.overlay, "show_extra_edge_angle", text="Edge Angle")
                col.prop(view.overlay, "show_extra_face_area", text="Face Area")
                col.prop(view.overlay, "show_extra_face_angle", text="Face Angle")
                #Developer
                col = col.column(align=True)
                row = col.row(align=True)
                if context.preferences.view.show_developer_ui:
                    col.prop(view.overlay, "show_extra_indices", text="Indices")
                #Shading
                col = box.column(align=True)
                col.enabled = context.mode == 'EDIT_MESH'
                col.label(text="Shading:")
                row = col.row(align=True)
                row.prop(view.overlay, "show_retopology", text='')
                sub = row.row(align=True)
                sub.active = view.overlay.show_retopology
                sub.prop(view.overlay, "retopology_offset", text="Retopology")

                col.prop(view.overlay, "show_weight", text="Vertex Group Weights")
                if view.overlay.show_weight:
                    row = col.row(align=True)
                    row.prop(tool_props, "vertex_group_user", expand=True)

                if shading.type == 'WIREFRAME':
                    xray = shading.show_xray_wireframe and shading.xray_alpha_wireframe < 1.0
                elif shading.type == 'SOLID':
                    xray = shading.show_xray and shading.xray_alpha < 1.0
                else:
                    xray = False
                statvis_active = not xray
                row = col.row()
                row.active = statvis_active
                row.prop(view.overlay, "show_statvis", text="Mesh Analysis")
                if view.overlay.show_statvis:
                    col = col.box()
                    col.active = statvis_active
                    col.prop(tool_props.statvis, "type", text="")

                    statvis_type = tool_props.statvis.type
                    if statvis_type == 'OVERHANG':
                        row = col.row(align=True)
                        row.prop(tool_props.statvis, "overhang_min", text="Minimum")
                        row.prop(tool_props.statvis, "overhang_max", text="Maximum")
                        col.row().prop(tool_props.statvis, "overhang_axis", expand=True)
                    elif statvis_type == 'THICKNESS':
                        row = col.row(align=True)
                        row.prop(tool_props.statvis, "thickness_min", text="Minimum")
                        row.prop(tool_props.statvis, "thickness_max", text="Maximum")
                        col.prop(tool_props.statvis, "thickness_samples")
                    elif statvis_type == 'INTERSECT':
                        pass
                    elif statvis_type == 'DISTORT':
                        row = col.row(align=True)
                        row.prop(tool_props.statvis, "distort_min", text="Minimum")
                        row.prop(tool_props.statvis, "distort_max", text="Maximum")
                    elif statvis_type == 'SHARP':
                        row = col.row(align=True)
                        row.prop(tool_props.statvis, "sharp_min", text="Minimum")
                        row.prop(tool_props.statvis, "sharp_max", text="Maximum")

            #Gizmo
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=False)
            row.label(text='Gizmo:', icon='GIZMO')
            row.prop(view, 'show_gizmo', text='', toggle=True, icon='GIZMO')
            icon = 'ToggleOFF'
            if prefs.tg_display_gizmo:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_gizmo', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_gizmo:
                col = box.column(align=True)
                col.label(text='Object Gizmo:')
                row = col.row(align=True)
                row.prop(view, 'show_gizmo_object_translate', text='', icon='EMPTY_ARROWS', toggle=True)
                row.prop(view, 'show_gizmo_object_rotate', text='', icon='ORIENTATION_GIMBAL', toggle=True)
                row.prop(view, 'show_gizmo_object_scale', text='', icon='CON_SIZELIKE', toggle=True)
                row.prop(context.scene.transform_orientation_slots[1], 'type', text='')

                col = box.column(align=True)
                col.prop(view, 'show_gizmo_navigate')
                col.prop(view, 'show_gizmo_tool')
                col.prop(view, 'show_gizmo_context')






            #View
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=False)
            row.label(text='View Object:', icon='SCENE')
            row.prop(prefs, 'tg_relative', icon_only=True, toggle=True, icon='ORIENTATION_GIMBAL')
            icon = 'ToggleOFF'
            if prefs.tg_display_view:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_view', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_view:
                row = col.row(align=True)
                op = row.operator('view3d.view_selected', text='Selected')
                op.use_all_regions = False
                op = row.operator('view3d.view_all', text='All')
                op.center = False
                row = col.row(align=True)
                row.operator('view3d.localview', text='Isolate')
                row.operator('view3d.view_camera', text='Camera')
                col.operator('mesh.bdsm_mesh_select_view', text='3 point')

                row = box.row(align=True)
                # First column
                col = row.column(align=True)
                col.label(text='')
                op = col.operator('view3d.view_axis', text='Left', icon='TRIA_LEFT')
                op.type = 'LEFT'
                op.relative = prefs.tg_relative
                op.align_active = False
                # Second column
                col = row.column(align=True)
                op = col.operator('view3d.view_axis', text='Top', icon='TRIA_UP')
                op.type = 'TOP'
                op.relative = prefs.tg_relative
                op.align_active = False
                op = col.operator('view3d.view_axis', text='Front',)
                op.type = 'FRONT'
                op.relative = False
                op.align_active = False
                op = col.operator('view3d.view_axis', text='Bottom', icon='TRIA_DOWN')
                op.type = 'LEFT'
                op.relative = prefs.tg_relative
                op.align_active = False
                # Third column
                col = row.column(align=True)
                col.label(text='')
                op = col.operator('view3d.view_axis', text='Right', icon='TRIA_RIGHT')
                op.type = 'RIGHT'
                op.relative = prefs.tg_relative
                op.align_active = False

                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('view3d.view_persportho', text='Pers/Orth', icon='VIEW_PERSPECTIVE')
                row.operator('view3d.bdsm_view_axis', text='Orth Axis', icon='VIEW_ORTHO').contextual = False
                row = col.row(align=True)
                row.operator('view3d.fly', text='Fly', icon='MOD_SOFT')
                row.operator('view3d.walk', text='Walk', icon='MOD_DYNAMICPAINT')

            #Area
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Area:', icon='MESH_GRID')
            icon = 'ToggleOFF'
            if prefs.tg_display_view_area:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_display_view_area', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_display_view_area:
                row = col.row(align=False)
                row.operator('screen.region_quadview', text='Quad Views' , icon='SNAP_VERTEX')
                row.operator('screen.area_dupli', text='Extend Views', icon='WINDOW')

                col = box.column(align=True)
                row = col.row(align=True)
                op = row.operator('screen.area_split', text='Hoziontal' , icon='NODE_TOP')
                op.direction = 'HORIZONTAL'
                op = row.operator('screen.area_split', text='Vertical', icon='NODE_SIDE')
                op.direction = 'VERTICAL'
                col = box.column(align=True)
                row = col.row(align=True)
                row.operator('screen.screen_full_area', text='Maximum' , icon='SHADING_BBOX')
                op = row.operator('screen.screen_full_area', text='Full Screen' , icon='FULLSCREEN_ENTER')
                op.use_hide_panels = True
                row = col.row(align=True)
                row.prop(view, 'show_region_header', text='Header', toggle=True, icon='TOPBAR')
                row.prop(view, 'show_region_tool_header', text='Tool Header', toggle=True, icon='GROUP')
                row = col.row(align=True)
                row.prop(view, 'show_region_toolbar', text='Toolbar', toggle=True, icon='MENU_PANEL')
                row.prop(view, 'show_region_ui', text='Sidebar', toggle=True, icon='MENU_PANEL')
                row = col.row(align=True)
                row.prop(view, 'show_region_asset_shelf', text='Asset Shelf', toggle=True, icon='BRUSHES_ALL')
                row.prop(view, 'show_region_hud', text='Hub', toggle=True, icon='DISK_DRIVE')

        #UTILITIES_TAB
        if props.topbar_enums == 'UTILITIES_TAB':
            box = layout.box()
            box.scale_y = 1.25
            col = box.column(align=True)
            row = col.row(align=True)

            row.label(text='Utilities:', icon='RESTRICT_SELECT_OFF')

            row = col.row(align=True)
            op = row.operator('object.transform_apply', text='Apply All Transform', icon='CHECKMARK')
            op.location = True
            op.rotation = True
            op.scale = True
            row = col.row(align=True)
            op = row.operator('view3d.bdsm_quick_measure', text='Quick Measure', icon='DRIVER_DISTANCE')
            op.qm_start = 'DEFAULT'
            #Clean Up Tool
            box = layout.box()
            box.scale_y = 1.25
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text='Clean Up:', icon='BRUSH_DATA')
            icon = 'ToggleOFF'
            if prefs.tg_ulitily_cleanup:
                icon = 'ToggleON'
            row.prop(prefs, 'tg_ulitily_cleanup', text='', emboss=False, icon_value=get_icon_id(icon))
            if prefs.tg_ulitily_cleanup:
                row = col.row(align=True)
                row.operator('view3d.bdsm_mesh_clean', text='Select').select_only = True
                row.operator('view3d.bdsm_mesh_clean', text='Clean').select_only = False
                col.separator(factor=0.5)
                col.prop(props, 'clean_doubles')
                col.prop(props, 'clean_loose')
                col.prop(props, 'clean_interior')
                col.prop(props, 'clean_degenerate')
                col.prop(props, 'clean_collinear')
                col.prop(props, 'clean_tinyedge')
                col.prop(props, 'clean_tinyedge_val')
                col.prop(props, "clean_collinear_val")
                col = box.column(align=True)
                col.label(text='Purge')
                boxrow = col.row(align=True)
                boxrow.operator('view3d.bdsm_mesh_clean_purge', text='Mesh').block_type = 'MESH'
                boxrow.operator('view3d.bdsm_mesh_clean_purge', text='Material').block_type = 'MATERIAL'
                boxrow.operator('view3d.bdsm_mesh_clean_purge', text='Texture').block_type = 'TEXTURE'
                boxrow.operator('view3d.bdsm_mesh_clean_purge', text='Image').block_type = 'IMAGE'
                col.operator('outliner.orphans_purge', text='Purge All Orphaned Data')

                col.label(text='Selection Tools')
                col.operator('mesh.bdsm_mesh_select_vert_collinear', text='Select Collinear Verts')
                col.operator('mesh.bdsm_mesh_select_flip_normal', text='Select Flip Normal Face')
                col.operator('view3d.bdsm_mesh_select_snapping', text='Check Snaping')
                col.operator('view3d.bdsm_mesh_select_vert_occluded', text='Select Occluded Verts')

                col.label(text='Select Elements by Vert Count:')
                row = col.row(align=True)
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='0').sel_count = '0'
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='1').sel_count = '1'
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='2').sel_count = '2'
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='3').sel_count = '3'
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='4').sel_count = '4'
                row.operator('view3d.bdsm_mesh_select_vert_counter', text='5+').sel_count = '5'
