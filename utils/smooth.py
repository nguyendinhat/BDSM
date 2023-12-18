import math
import numpy as np
from bpy.types import Gizmo


from mathutils.bvhtree import BVHTree
from mathutils import Vector, kdtree, Matrix
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
import gpu
import bmesh
import blf
import bpy

round_to_first_digit = lambda x: math.pow(10, math.floor(math.log10(x)))

class MyCustomShapeWidget(Gizmo):
    bl_idname = 'VIEW3D_GT_Circle_Gizmo'
    __slots__ = (
        'last_depth',
        'depsgraph',
        'first_run',  # do not run gizmo draw till we inith matrix_basis
    )
    bvh_run_update = False
    snap_surface_BVHT = None

    def handler(self, scene, arg):
        if MyCustomShapeWidget.bvh_run_update is False:
            MyCustomShapeWidget.bvh_run_update = self.depsgraph.id_type_updated('MESH') or self.depsgraph.id_type_updated('OBJECT')

    def update_matrix(self, context, location):
        hit_local, normal = raycast(context, location)
        hover_over_mesh = hit_local is not None
        if hit_local is None:
            rv3d = context.region_data
            normal = get_view_vec(context)
            hit_local = view3d_utils.region_2d_to_location_3d(context.region, rv3d, location, self.last_depth)

        self.last_depth = hit_local.copy()
        quat = normal.to_track_quat('Z','Y')  # to_track_quat(track, up)
        rot_mat = quat.to_matrix().to_4x4()

        #NOTE get circle radius, from vps_tool radius prop
        tool = context.workspace.tools.from_space_view3d_mode(context.mode)
        tool_props = tool.operator_properties('mesh.smooth_brush_vps')
        rad_scale_mat = Matrix.Scale(tool_props.radius, 4)

        if hover_over_mesh:
            hit_world = context.active_object.matrix_world @ hit_local
            self.matrix_basis =   Matrix.Translation(hit_world) @ rot_mat @ rad_scale_mat
        else:
            self.matrix_basis = Matrix.Translation(hit_local) @ rot_mat @ rad_scale_mat

    def finish_gizmo(self):
        handler = object.__getattribute__(self, 'handler')
        if handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(handler)

    def draw(self, context):
        # print('Gizmo draw')
        if not self.first_run: #avoids drawing brush circle at Vector((0, 0, 0))
            draw_circle_px(self, (0.9,0.9,0.9,1))

    def setup(self):
        # print('Gizmo setup')
        self.first_run = True
        self.use_draw_offset_scale = True
        self.last_depth = Vector((0, 0, 0))


    def test_select(self, context, location):
        # makes it possible to hover higlight, wont work f draw_select() is used at same time
        self.update_matrix(context, location)
        if self.first_run:
            self.depsgraph = context.evaluated_depsgraph_get()
            bpy.app.handlers.depsgraph_update_post.append(self.handler)
        else:
            if MyCustomShapeWidget.bvh_run_update:
                last_operator = context.window_manager.operators [-1] if bpy.context.window_manager.operators  else None
                if not last_operator or last_operator.name not in {'Select', 'Loop Select', '(De)select All'}:
                    context.active_object.update_from_editmode()
                    self.depsgraph = context.evaluated_depsgraph_get() #XXX: be careful to not trigger depsgraph update loop
                    MyCustomShapeWidget.snap_surface_BVHT = get_obj_mesh_bvht(context.active_object, self.depsgraph, with_mods=False, world_space=False)
                MyCustomShapeWidget.bvh_run_update = False

        self.first_run = False
        context.area.tag_redraw()
        return -1


def get_obj_mesh_bvht(obj, depsgraph, with_mods=True, world_space=True):
    if with_mods:
        if world_space:
            #? OLD way: wont work if mod uses some helper, or there is parent or something, but faster
            obj.data.transform(obj.matrix_world)
            depsgraph.update()  # fixes bad transformation baing applied to obj
            bvh = BVHTree.FromObject(obj, depsgraph)  # ? not required to get with mod: obj.evaluated_get(depsgraph)
            obj.data.transform(obj.matrix_world.inverted())

            #* better but slower - even 5-10 times (0.05 sec), wont work on non meshes (curves?)
            # obj_eval = obj.evaluated_get(depsgraph)
            # bm = bmesh.new()   # create an empty BMesh
            # bm.from_mesh(obj_eval.to_mesh())   # with modifiers
            # bm.transform(obj.matrix_world)
            # bm.normal_update()
            # bvh = BVHTree.FromBMesh(bm)  # ? not required to get with mod: obj.evaluated_get(depsgraph)
            # bm.free()  # free and prevent further access
            # obj_eval.to_mesh_clear()
            return bvh
        else:
            return BVHTree.FromObject(obj, depsgraph)  # with modes
    else:
        if world_space:
            # 4 times slower than data.transform
            #bvh1 =  BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            #bmesh - same time as data.transform
            obj.data.transform(obj.matrix_world)
            bvh = BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            obj.data.transform(obj.matrix_world.inverted())
            return bvh
        else:
            return BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])

def raycast(context, mouse_2d_co):
    if not MyCustomShapeWidget.snap_surface_BVHT:
        depsgraph = context.evaluated_depsgraph_get()
        MyCustomShapeWidget.snap_surface_BVHT = get_obj_mesh_bvht(context.active_object, depsgraph, with_mods=False, world_space=False)
    snap_surface_BVHT = MyCustomShapeWidget.snap_surface_BVHT

    region = context.region
    rv3d = context.region_data
    ray_max = 1000.0
    mat_inv = context.active_object.matrix_world.inverted()

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_2d_co)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_2d_co)

    if rv3d.view_perspective == 'ORTHO':  # move ortho origin back
        ray_origin = ray_origin - (view_vector * (ray_max / 2.0))

    ray_target = ray_origin + (view_vector * ray_max)

    ray_origin_obj = mat_inv @ ray_origin  # not sure why this order works, whatever...
    ray_target_obj = mat_inv @ ray_target
    view_vector_obj = ray_target_obj - ray_origin_obj

    # ray_direction = ray_origin - ray_target
    hit_local, normal, face_index, depth = snap_surface_BVHT.ray_cast(ray_origin_obj, view_vector_obj)
    return hit_local, normal

def get_view_vec(context):
    rv3d = context.region_data
    view_mat = rv3d.view_matrix.to_3x3()
    # screen_depth = view_ma[2].xyz
    # screen_up = view_ma[1].xyz
    # screen_right = view_ma[1].xyz
    return view_mat[2].xyz

def circle_coords_calc(circle_resol):
    import math
    m_2pi = 2 * math.pi
    coords = ()
    for a in range(circle_resol + 1):
        ang = (m_2pi * a) / circle_resol
        coords += (math.sin(ang), math.cos(ang), 0.0),
    return coords

circle_co = circle_coords_calc(32)

shader_3d_uniform = gpu.shader.from_builtin('UNIFORM_COLOR')

def draw_circle_px(self, color):
    gpu.state.line_width_set(2)
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    with gpu.matrix.push_pop():
        gpu.matrix.multiply_matrix(self.matrix_basis)
        batch = batch_for_shader(shader_3d_uniform, 'LINE_LOOP', {'pos': circle_co})
        shader_3d_uniform.bind()
        shader_3d_uniform.uniform_float('color', color)
        batch.draw(shader_3d_uniform)

    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1)

# function that draws gls text in 2d mouse position
def draw_text_px(self, color):
    gpu.state.blend_set('ALPHA')
    font_id = 0
    blf.color(font_id, *color)
    blf.position(font_id, self.mouse_init_co[0]-20, self.mouse_init_co[1], 0)
    blf.size(font_id, 30, 72) if bpy.app.version <= (4, 0, 0) else blf.size(font_id, 30)
    blf.draw(font_id, str(int(self.strength+0.5)))
    gpu.state.blend_set('NONE')

def get_weights(ob, vgroup):
    weights = [0.0]*len(ob.data.vertices)
    for index, vert in enumerate(ob.data.vertices):
        for group in vert.groups:
            if group.group == vgroup.index:
                weights[index] = group.weight
    return weights

def get_mirrored_axis(source):
    x = y = z = False
    merge_threshold = 0.001
    use_m = bpy.context.object.data
    x, y, z = use_m.use_mirror_x, use_m.use_mirror_y, use_m.use_mirror_z
    if not (x and y and z):
        for mod in source.modifiers:
            if mod.type == 'MIRROR' and mod.mirror_object == None:  #  and mod.show_viewport use first visible
                x = mod.use_axis[0] or x
                y = mod.use_axis[1] or y
                z = mod.use_axis[2] or z
                merge_threshold = mod.merge_threshold
    mirror_axes = []
    if x:
        mirror_axes.append(0)
    if y:
        mirror_axes.append(1)
    if z:
        mirror_axes.append(1)
    return mirror_axes, merge_threshold

def get_mirrored_verts(mesh):
    kd = kdtree.KDTree(len(mesh.vertices))
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)
    kd.balance()

    mirror_map = []
    for vert in mesh.vertices:
        co, mirror_vert_index, dist = kd.find(Vector((-vert.co[0], vert.co[1], vert.co[2])))
        if mirror_vert_index == vert.index:
            mirror_map.append(-1)
        elif dist < 0.0001:  # delta
            mirror_map.append(mirror_vert_index)
        else:
            mirror_map.append(-2)
    return tuple(mirror_map)

def close_bmesh(context,  bm, source):
    bm.normal_update()
    if context.object.mode == 'EDIT':
        bmesh.update_edit_mesh(source, loop_triangles=False, destructive=False)
    else:
        bm.to_mesh(source)
        bm.free()
        # source.update()

def get_bmesh(context, mesh):
    bm = bmesh.new()
    if context.active_object.mode == 'OBJECT':
        bm.from_mesh(mesh)
    elif context.active_object.mode == 'EDIT':
        bm =  bmesh.from_edit_mesh(mesh)
    return bm

def three_d_bincount_add(out ,e_k, weights):
    out[:,0] += np.bincount(e_k, weights[:,0], out.shape[0])
    out[:,1] += np.bincount(e_k, weights[:,1], out.shape[0])
    out[:,2] += np.bincount(e_k, weights[:,2], out.shape[0])

def new_bincount(out, e_k, weights = None):
    out += np.bincount(e_k, weights, out.shape[0])








