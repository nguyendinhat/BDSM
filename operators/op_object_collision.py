import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.types import Operator
from mathutils import Vector

from ..utils.tools import average_vector,  get_layer_collection

def bbox_calc(bbx, bby, bbz):
    bbx.sort()
    bby.sort()
    bbz.sort()
    side_x = bbx[-1] - bbx[0]
    side_y = bby[-1] - bby[0]
    side_z = bbz[-1] - bbz[0]
    minmax = (Vector((bbx[0], bby[0], bbz[0])), Vector((bbx[-1], bby[-1], bbz[-1])))
    avg_pos = average_vector(minmax)
    return avg_pos, side_x, side_y, side_z


class BDSM_Object_Collision(Operator):
    bl_idname = 'view3d.bdsm_object_collision'
    bl_label = 'BDSM Object Collision'
    bl_description = 'BDSM Object Collision \n '\
                    'Creates BOX or CONVEX HULL collision-style object from Element or Object selection\n' \
                    'Multi-Object Edit-Mode support.'
    bl_options = {'REGISTER', 'UNDO'}

    collision_type: EnumProperty(
        items=[('BOX', 'Box', 'MOD_MESHDEFORM', 1),
               ('CONVEX', 'Convex Hull', 'CONSTRAINT', 2)],
        name='Collision Type', default='BOX')

    collision_mode : BoolProperty(
        name='Separate Collision Objects',
        default=False, description='Object Mode: Collision object for each selected, or one combined')

    collision_viewport : BoolProperty(
        name='Collision Style Shading',
        default=True, description='Sets collision object(s) viewport color & in-front shading')

    reference_viewport : BoolProperty(
        name='Reference Style Shading',
        default=False, description='Sets collision object(s) viewport to bounds display & not show in renders')

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.use_property_split = True
        row.prop(self, 'collision_type', expand=True)
        layout.separator(factor=1)
        col = layout.column(align=True)
        split = col.split(factor=.3)
        split.label(text='')
        split.prop(self, 'collision_mode', toggle=True)
        col = layout.column(align=True)
        split = col.split(factor=.3)
        split.label(text='')
        split.prop(self, 'collision_viewport', toggle=True)
        col = layout.column(align=True)
        split = col.split(factor=.3)
        split.label(text='')
        split.prop(self, 'reference_viewport', toggle=True)
        layout.separator(factor=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def set_shading(self, obj):
        if self.collision_viewport:
            obj.color = (1, 0, 0, 0.3)
            obj.show_in_front = True
        if self.reference_viewport:
            obj.hide_render = True
            obj.display_type = 'WIRE'

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == 'MESH' or o.type == 'EMPTY']
        sel_count = len(sel_obj)

        if sel_count == 0:
            self.report({'INFO'}, 'Selection Error: No valid/active object(s) selected?')
            return {'CANCELLED'}

        if context.active_object is not None:
            og_obj = context.active_object
        else:
            og_obj = sel_obj[0]

        og_name = str(og_obj.name)

        obj_collection = sel_obj[0].users_collection[0]
        layer_collection = context.view_layer.layer_collection
        layer_coll = get_layer_collection(layer_collection, obj_collection.name)
        context.view_layer.active_layer_collection = layer_coll
        mode = str(context.mode)

        if mode == 'EDIT_MESH':
            all_obj = [o for o in context.scene.objects if o.type == 'MESH']

            if self.collision_type == 'CONVEX':
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type='SELECTED')
                new_obj = [o for o in context.scene.objects if o.type == 'MESH' and o not in all_obj]

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                for o in new_obj:
                    o.select_set(True)
                bpy.context.view_layer.objects.active = new_obj[0]
                if sel_count > 1:
                    bpy.ops.object.join('INVOKE_DEFAULT')

                col_obj = context.view_layer.objects.active
                self.set_shading(col_obj)

                if og_obj:
                    col_obj.name = og_name + '_col'
                else:
                    col_obj.name = col_obj.name + '_col'

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.convex_hull(delete_unused=True, use_existing_faces=True, make_holes=False,
                                         join_triangles=True, face_threshold=0.10472, shape_threshold=0.698132,
                                         uvs=False, vcols=False, seam=False, sharp=False, materials=False)
                bpy.ops.object.mode_set(mode='OBJECT')

            elif self.collision_type == 'BOX':
                bpy.ops.object.mode_set(mode='OBJECT')

                bbx, bby, bbz = [], [], []
                for o in sel_obj:
                    vcos = [o.matrix_world @ v.co for v in o.data.vertices if v.select]
                    for co in vcos:
                        bbx.append(co[0])
                        bby.append(co[1])
                        bbz.append(co[2])

                if len(bbx) == 0:
                    bpy.ops.object.mode_set(mode='EDIT')
                    self.report({'INFO'}, 'Cancelled: Nothing Selected?')
                    return {'CANCELLED'}

                avg_pos, side_x, side_y, side_z = bbox_calc(bbx, bby, bbz)
                bpy.ops.mesh.bdsm_mesh_primitive_box_add(width=side_x / 2, depth=side_y / 2, height=side_z / 2,
                                                  align='WORLD', location=avg_pos, rotation=(0, 0, 0))

                col_obj = [o for o in context.scene.objects if o.type == 'MESH'][-1]
                if og_obj:
                    col_obj.name = og_name + '_col'
                else:
                    col_obj.name = col_obj.name + '_col'

                col_obj = context.view_layer.objects.active
                self.set_shading(col_obj)

        elif mode == 'OBJECT':
            new_sel = []
            bpy.ops.object.select_all(action='DESELECT')

            if self.collision_type == 'CONVEX':

                if self.collision_mode:

                    for o in sel_obj:
                        # New Mesh
                        mesh = bpy.data.meshes.new(name=og_name + '_col')
                        col_obj = bpy.data.objects.new(mesh.name, mesh)
                        obj_collection.objects.link(col_obj)
                        context.view_layer.objects.active = col_obj

                        # Data for CH
                        vco = []

                        if o.type == 'EMPTY' and o.instance_collection is not None:
                            s_o = o.instance_collection.objects[:]
                            for obj in s_o:
                                vco.extend([o.matrix_world @ (obj.matrix_world @ v.co) for v in obj.data.vertices])
                        else:
                            vco = [o.matrix_world @ v.co for v in o.data.vertices]

                        mesh.from_pydata(vco, [], [])

                        # Use CH Op
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.convex_hull(delete_unused=True, use_existing_faces=False, make_holes=False,
                                                 join_triangles=True, face_threshold=0.10472, shape_threshold=0.698132,
                                                 uvs=False, vcols=False, seam=False, sharp=False, materials=False)
                        bpy.ops.object.mode_set(mode='OBJECT')

                        new_sel.append(col_obj)
                        self.set_shading(col_obj)
                        col_obj.select_set(False)

                else:
                    # Data for CH
                    vco = []
                    for o in sel_obj:
                        if o.type == 'EMPTY' and o.instance_collection is not None:
                            s_o = o.instance_collection.objects[:]
                            for obj in s_o:
                                vco.extend([o.matrix_world @ (obj.matrix_world @ v.co) for v in obj.data.vertices])
                        else:
                            vco.extend([o.matrix_world @ v.co for v in o.data.vertices])

                    # New Mesh
                    mesh = bpy.data.meshes.new(name=og_name + '_col')
                    col_obj = bpy.data.objects.new(mesh.name, mesh)
                    obj_collection.objects.link(col_obj)
                    context.view_layer.objects.active = col_obj

                    mesh.from_pydata(vco, [], [])

                    # Use CH Op
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.convex_hull(delete_unused=True, use_existing_faces=False, make_holes=False,
                                             join_triangles=True, face_threshold=0.10472, shape_threshold=0.698132,
                                             uvs=False, vcols=False, seam=False, sharp=False, materials=False)
                    bpy.ops.object.mode_set(mode='OBJECT')

                    new_sel.append(col_obj)
                    self.set_shading(col_obj)
                    col_obj.select_set(False)

            elif self.collision_type == 'BOX':

                if self.collision_mode:

                    for o in sel_obj:
                        bbx, bby, bbz = [], [], []

                        if o.type == 'EMPTY' and o.instance_collection is not None:
                            cbbox = []
                            s_o = o.instance_collection.objects[:]
                            for obj in s_o:
                                vecs = [Vector(vec) for vec in obj.bound_box]
                                cbbox.extend([o.matrix_world @ (obj.matrix_world @ v) for v in vecs])
                            for co in cbbox:
                                bbx.append(co[0])
                                bby.append(co[1])
                                bbz.append(co[2])
                        else:
                            vecs = [Vector(vec) for vec in o.bound_box]
                            vco = [o.matrix_world @ v for v in vecs]
                            for co in vco:
                                bbx.append(co[0])
                                bby.append(co[1])
                                bbz.append(co[2])

                        avg_pos, side_x, side_y, side_z = bbox_calc(bbx, bby, bbz)

                        bpy.ops.mesh.bdsm_mesh_primitive_box_add(width=side_x / 2, depth=side_y / 2, height=side_z / 2,
                                                          align='WORLD', location=avg_pos, rotation=(0, 0, 0))

                        new_obj = context.view_layer.objects.active
                        new_obj.name = o.name + '_col'
                        new_sel.append(new_obj)
                        self.set_shading(new_obj)

                else:
                    bbx, bby, bbz = [], [], []
                    for o in sel_obj:

                        if o.type == 'EMPTY' and o.instance_collection is not None:
                            cbbox = []
                            s_o = o.instance_collection.objects[:]
                            for obj in s_o:
                                vecs = [Vector(vec) for vec in obj.bound_box]
                                cbbox.extend([o.matrix_world @ (obj.matrix_world @ v) for v in vecs])
                            for co in cbbox:
                                bbx.append(co[0])
                                bby.append(co[1])
                                bbz.append(co[2])
                        else:
                            vecs = [Vector(vec) for vec in o.bound_box]
                            vco = [o.matrix_world @ v for v in vecs]
                            for co in vco:
                                bbx.append(co[0])
                                bby.append(co[1])
                                bbz.append(co[2])

                    avg_pos, side_x, side_y, side_z = bbox_calc(bbx, bby, bbz)

                    bpy.ops.mesh.bdsm_mesh_primitive_box_add(width=side_x / 2, depth=side_y / 2, height=side_z / 2,
                                                      align='WORLD', location=avg_pos, rotation=(0, 0, 0))

                    new_obj = context.view_layer.objects.active
                    new_obj.name = sel_obj[0].name + '_col'
                    new_sel.append(new_obj)
                    self.set_shading(new_obj)

            for i in new_sel:
                i.select_set(True)

        if self.collision_viewport:
            context.space_data.shading.color_type = 'OBJECT'

        return {'FINISHED'}


class BDSM_Object_BBox_Match(Operator):
    bl_idname = 'object.bdsm_object_bbox_match'
    bl_label = 'BDSM Object BBox Match'
    bl_description = 'BDSM Object BBox Match\n'\
                    'Match Active Bounding Box\n'\
                    'Scales selected object(s) to last selected object bounding box (along axis chosen in redo)\n' \
                    'Make sure origin(s) is properly placed beforehand\nScale will be auto-applied'
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[('UNIT', 'Longest Axis (Unit)', '', 1),
               ('ALL', 'All Axis', '', 2),
               ('X', 'X Only', '', 3),
               ('Y', 'Y Only', '', 4),
               ('Z', 'Z Only', '', 5),
               ],
        name='Scaling', default='UNIT',
        description='Choose which Bounding Box Axis to scale with')

    match_loc : BoolProperty(name='Location', default=False)
    match_rot : BoolProperty(name='Rotation', default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'mode', expand=True)
        layout.separator(factor=0.5)
        row = layout.row()
        row.prop(self, 'match_loc', toggle=True)
        row.prop(self, 'match_rot', toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        if not len(sel_objects) >= 2:
            self.report({'INFO'}, 'Invalid Selection (2+ required)')
            return {'CANCELLED'}

        src_obj = context.object
        src_bb = src_obj.dimensions

        if self.mode == 'UNIT':
            v = sorted(src_bb)[-1]
            src_bb = [v, v, v]
        elif self.mode == 'X':
            v = src_bb[0]
            src_bb = [v, 1, 1]
        elif self.mode == 'Y':
            v = src_bb[1]
            src_bb = [1, v, 1]
        elif self.mode == 'Z':
            v = src_bb[2]
            src_bb = [1, 1, v]

        target_objects = [o for o in sel_objects if o != src_obj]

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False, )

        for o in target_objects:

            bb = o.dimensions
            if self.mode == 'UNIT':
                v = sorted(bb)[-1]
                bb = [v, v, v]
            elif self.mode == 'X':
                v = bb[0]
                bb = [v, 1, 1]
            elif self.mode == 'Y':
                v = bb[1]
                bb = [1, v, 1]
            elif self.mode == 'Z':
                v = bb[2]
                bb = [1, 1, v]

            o.scale[0] *= (src_bb[0] / bb[0])
            o.scale[1] *= (src_bb[1] / bb[1])
            o.scale[2] *= (src_bb[2] / bb[2])

            if self.match_loc:
                o.location = src_obj.location
            if self.match_rot:
                o.rotation_euler = src_obj.rotation_euler

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

        return {'FINISHED'}
