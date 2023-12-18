import typing
import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.types import Context, Operator
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri

from ..utils.tools import get_distance, average_vector, mouse_raycast, get_view_type, set_active_collection


class BDSM_Copy(Operator):
    bl_idname = 'view3d.bdsm_copy'
    bl_label = 'BDSM Copy'
    bl_description = 'BDSM Copy \nCut+ or Copy+ face selection (to temporary cache) then Paste+ into another object.'
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        items=[('COPY', 'Copy', '', 1),
               ('PASTE', 'Paste', '', 2),
               ('CUT', 'Cut', '', 3),
               ],
        options={'HIDDEN'},
        default='COPY'
        )

    mouse_point: BoolProperty(
        name='Mouse Point',
        default=False,
        description='Paste+ Point\n'
                    'ON: Places pasted Object(s) at Mouse Point.  \nOFF: Original location'
    )

    merge: BoolProperty(
        name='Merg',
        default=False,
        description='Paste+ Merge\n'
                    'ON: Merges Pasted items with selected(Active Object) in Object Mode\n'
                    'OFF: Paste items into New Object, with or without selections in Object Mode')


    screen_x = 0
    mouse_pos = [0, 0]
    active = None

    def invoke(self, context, event):
        self.screen_x = int(context.region.width * 0.5)
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        return self.execute(context)

    def execute(self, context):
        # SELECTION
        paste_merge = bool(self.merge)
        mouse_point = bool(self.mouse_point)

        select_mode = context.mode[:]
        select_object = [o for o in context.selected_objects]
        self.active = context.object

        # CollectionSetup
        active_coll = context.scene.collection

        if self.active:
            set_active_collection(context, self.active)
            active_coll = self.active.users_collection[0]
        elif select_object:
            set_active_collection(context, select_object[0])
            self.active = select_object[0]
            active_coll = self.active.users_collection[0]
        #
        # OBJECT MODE
        #
        if select_mode == 'OBJECT':

            if self.mode == 'COPY' or self.mode == 'CUT':
                if select_object:
                    bpy.ops.view3d.copybuffer()
                    if self.mode == 'CUT':
                        bpy.ops.object.delete()
                else:
                    self.report({'INFO'}, 'No objects selected?')

            elif self.mode == 'PASTE' and active_coll:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.view3d.pastebuffer()
                new_objects = context.selected_objects

                if mouse_point:
                    # View placement compensation & Z0 drop
                    hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
                    if hit_obj:
                        setpos = hit_wloc
                    else:
                        view_vec = region_2d_to_vector_3d(context.region, context.space_data.region_3d, self.mouse_pos)
                        view_pos = context.space_data.region_3d.view_matrix.inverted().translation
                        raypos = []
                        snap = 0.01
                        if get_view_type() != 'ORTHO':
                            ground = ((0, 0, 0), (0, 1, 0), (1, 0, 0))
                            raypos = intersect_ray_tri(ground[0], ground[1], ground[2], view_vec, view_pos, False)
                        if raypos:
                            setpos = Vector((round(raypos[0], 3), round(raypos[1], 3), snap / 2))
                        else:
                            setpos = region_2d_to_location_3d(context.region, context.space_data.region_3d,
                                                              self.mouse_pos, view_vec)
                    # Calc offsets if more than one
                    vecs, offsets = [], []
                    if len(new_objects) > 1:
                        cpos = average_vector([o.location for o in new_objects])
                        for o in new_objects:
                            vecs.append(Vector((o.location - cpos)).normalized())
                            offsets.append(get_distance(o.location, cpos))

                    # Place
                    for i, o in enumerate(new_objects):
                        pos = setpos
                        if offsets:
                            pos = setpos + (offsets[i] * vecs[i])
                        o.location = pos

                if paste_merge and self.active:
                    context.view_layer.objects.active = self.active
                    self.active.select_set(True)
                    bpy.ops.object.join()

            return {'FINISHED'}
        #
        # EDIT MODE
        #
        elif select_mode == 'EDIT_MESH':
            sel_poly = []
            # Limit obj selection to Mesh, for now
            select_object = [o for o in context.selected_objects if o.type == 'MESH']

            if self.mode == 'COPY' or self.mode == 'CUT':
                # SELECTION CHECK
                for o in select_object:
                    o.update_from_editmode()
                    p = [i for i in o.data.polygons if i.select]
                    sel_poly.extend(p)
                if not sel_poly:
                    self.report({'INFO'}, 'No polygons selected?')
                    return {'CANCELLED'}

                # COPY/CUT MACRO
                if self.mode == 'COPY':
                    bpy.ops.mesh.duplicate()

                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')

                for o in select_object:
                    o.select_set(False)

                new_obj = [o for o in context.selected_objects if o.type == 'MESH' and o not in select_object]
                obj_to_cache = new_obj[0]
                if len(new_obj) > 1:
                    context.view_layer.objects.active = obj_to_cache
                    bpy.ops.object.join()

                # CLEAR PARENT
                mtx = obj_to_cache.matrix_world.to_translation()
                obj_to_cache.parent = None
                obj_to_cache.matrix_world.translation = mtx

                # BUFFER
                bpy.ops.view3d.copybuffer()
                if self.mode in {'CUT', 'COPY'}:
                    bpy.ops.object.delete()

                # RESTORE EDIT MODE
                for o in select_object:
                    o.select_set(True)
                context.view_layer.objects.active = self.active
                bpy.ops.object.mode_set(mode='EDIT')

            elif self.mode == 'PASTE':
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')

                # PASTE (DUPES FROM BUFFER)
                bpy.ops.view3d.pastebuffer()

                # MERGE & RESTORE EDIT MODE
                self.active.select_set(True)
                context.view_layer.objects.active = self.active
                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='INVERT')

        return {'FINISHED'}


class BDSM_Duplicate(Operator):
    bl_idname = 'view3d.bdsm_duplicate'
    bl_label = 'BDSM Duplicate'
    bl_description = 'BDSM Duplicate'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH': return True
        if len(context.selected_objects) == 0: return False
        return context.object is not None

    def execute(self, context):
        select_mode = context.mode[:]
        if select_mode == 'OBJECT':
            bpy.ops.object.duplicate_move('INVOKE_DEFAULT')
            return {'FINISHED'}
        elif select_mode == 'EDIT_MESH':
            bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT')
            return {'FINISHED'}
        return {'FINISHED'}

class BDSM_Detach(Operator):
    bl_idname = 'mesh.bdsm_detach'
    bl_label = 'BDSM Detach'
    bl_description = 'BDSM Detach'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        return bpy.ops.mesh.separate(type='SELECTED')