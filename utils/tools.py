import bpy, bmesh, math, mathutils
from collections import OrderedDict, Counter, deque
from math import degrees, atan2, pi, radians, sqrt
from mathutils import Vector, Matrix
import numpy as np

from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from mathutils.geometry import intersect_point_line
MAX_ITERATIONS = 400
DOUBLECLICK_TIME = 0.1


def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            bpy.ops.wm.tool_set_by_id(name=tool_name)

def back_mode(back_mode):
    object_mode_type = ['OBJECT','EDIT_MESH','EDIT','POSE','SCULPT','VERTEX_PAINT','WEIGHT_PAINT','TEXTURE_PAINT','PARTICLE_EDIT','EDIT_GPENCIL','SCULPT_GPENCIL','PAINT_GPENCIL','WEIGHT_GPENCIL','VERTEX_GPENCIL','PAINT_GREASE_PENCIL','SCULPT_CURVES']
    #PAINT_VERTEX,PAINT_WEIGHT,PAINT_TEXTURE
    result = True
    if back_mode in object_mode_type:
        target_mode(back_mode)
        result = False
    if back_mode == 'PAINT_VERTEX':
        bpy.ops.paint.vertex_paint_toggle()
        result = False
    if back_mode == 'PAINT_WEIGHT':
        bpy.ops.paint.weight_paint_toggle()
        result = False
    if back_mode == 'PAINT_TEXTURE':
        bpy.ops.paint.texture_paint_toggle()
        result = False
    if back_mode == 'EDIT_CURVE':
        bpy.ops.object.editmode_toggle()
    return result

def target_mode(target_mode):
    bpy.ops.object.mode_set(mode=target_mode,toggle=True)
    return True

def set_mode(mode,action='TOGGLE', extend=False, expand=False):
    actual_mode = get_mode()
    if mode == 'SELECT_OBJECT' and actual_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    elif mode in ['SELECT_VERT', 'SELECT_EDGE', 'SELECT_FACE']:
        if actual_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type=mode.replace('SELECT_', ''),action=action, use_extend=extend,use_expand=expand)

def get_mode():
    mode = bpy.context.mode
    if mode == 'EDIT_MESH':
        selection_mode = (tuple(bpy.context.scene.tool_settings.mesh_select_mode))
        if selection_mode[0]:
            return 'VERT'
        elif selection_mode[1]:
            return 'EDGE'
        elif selection_mode[2]:
            return 'FACE'

    if mode == 'EDIT_GPENCIL':
        return bpy.context.scene.tool_settings.gpencil_selectmode_edit

    return mode

def get_selected(mode='', item=True, ordered=False, all=False):
    selection = []
    if not mode:
        mode = get_mode()

    if mode == 'OBJECT':
        if item:
            return [obj for obj in bpy.context.selected_objects]

        else:
            return [obj.name for obj in bpy.context.selected_objects]

    elif mode in ['VERT', 'EDGE', 'FACE']:
        bm = get_bmesh()

        if ordered:
            if mode == 'VERT':
                selection = [vert for vert in bm.select_history if isinstance(vert, bmesh.types.BMVert)]
            elif mode == 'EDGE':
                selection = [edge for edge in bm.select_history if isinstance(edge, bmesh.types.BMEdge)]
            elif mode == 'FACE':
                selection = [face for face in bm.select_history if isinstance(face, bmesh.types.BMFace)]

        if all:
            if mode == 'VERT':
                selection = [vert for vert in bm.verts]
            elif mode == 'EDGE':
                selection = [edge for edge in bm.edges]
            elif mode == 'FACE':
                selection = [face for face in bm.faces]

        else:
            if mode == 'VERT':
                selection = [vert for vert in bm.verts if vert.select]
            elif mode == 'EDGE':
                selection = [edge for edge in bm.edges if edge.select]
            elif mode == 'FACE':
                selection = [face for face in bm.faces if face.select]

        if item:
            return selection
        else:
            return [element.index for element in selection]

    elif mode == 'EDIT_CURVE':
        curves = bpy.context.active_object.data.splines
        points = []

        if all:
            for curve in curves:
                if curve.type == 'BEZIER':
                    points.append([point for point in curve.bezier_points])

                else:
                    points.append([point for point in curve.points])

        else:
            for curve in curves:
                if curve.type == 'BEZIER':
                    points.append([point for point in curve.bezier_points
                                   if point.select_control_point])

                else:
                    points.append([point for point in curve.points
                                   if point.select])

        points = [item for sublist in points for item in sublist]
        return points

    else:
        return []

def get_bmesh():
    if get_mode() in ['VERT', 'EDGE', 'FACE']:
        return bmesh.from_edit_mesh(bpy.context.edit_object.data)
    else:
        print("Must be in obj mode to get bmesh")




def rings(loop):
    while True:
        # If radial loop links back here, we're boundary, thus done
        if loop.link_loop_radial_next == loop:
            break
        # Jump to adjacent face and walk two edges forward
        loop = loop.link_loop_radial_next.link_loop_next.link_loop_next
        loop.edge.select = True


def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type='OUTPUT')


def edge_angle(edge_1, edge_2, face_normal):
    b = set(edge_1.verts).intersection(edge_2.verts).pop()
    a = edge_1.other_vert(b).co - b.co
    c = edge_2.other_vert(b).co - b.co
    a.negate()
    axis = a.cross(c).normalized()
    if axis.length < 1e-5:
        return pi # inline vert
    if axis.dot(face_normal) < 0:
        axis.negate()
    M = axis.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
    a = (M @ a).xy.normalized()
    c = (M @ c).xy.normalized()
    return pi - atan2(a.cross(c), a.dot(c))


def get_distance(v1, v2):
    dist = [(a - b) ** 2 for a, b in zip(v1, v2)]
    return sqrt(sum(dist))

def average_vector(vectors):
    try:
        return Vector(sum(vectors, Vector()) / len(vectors))
    except ZeroDivisionError:
        print('Zero Division Error: Invalid Selection?')
        return None

def obj_raycast(obj, matrix, ray_origin, ray_target):
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj
    success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal, face_index
    else:
        return None, None, None

def correct_normal(world_matrix, vec_normal):
    n = (world_matrix.to_quaternion() @ vec_normal).to_4d()
    n.w = 0
    return world_matrix.to_quaternion() @ (world_matrix.inverted() @ n).to_3d().normalized()

def mouse_raycast(context, mouse_pos, evaluated=False):
    region = context.region
    rv3d = context.region_data

    view_vector = region_2d_to_vector_3d(region, rv3d, mouse_pos)
    ray_origin = region_2d_to_origin_3d(region, rv3d, mouse_pos)
    ray_target = ray_origin + view_vector

    hit_length_squared = -1.0
    hit_obj, hit_wloc, hit_normal, hit_face = None, None, None, None

    # cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
    cat = ['MESH']
    # todo: Make hit curves returnable objs w. evaluated

    if not evaluated:
        objects = [o for o in context.visible_objects]
        depsgraph = objects.copy()
        objects = [o.name for o in context.visible_objects]
    else:
        objects = [o.name for o in context.visible_objects]
        depsgraph = context.evaluated_depsgraph_get()
        depsgraph = depsgraph.object_instances

    for dup in depsgraph:
        if evaluated:
            if dup.is_instance:
                obj = dup.instance_object
                obj_matrix = dup.matrix_world.copy()
            else:
                obj = dup.object
                obj_matrix = obj.matrix_world.copy()
        else:
            obj = dup
            obj_matrix = obj.matrix_world.copy()

        if obj.type in cat and obj.name in objects:
            try:
                hit, normal, face_index = obj_raycast(obj, obj_matrix, ray_origin, ray_target)
            except RuntimeError:
                print('Raycast Failed: Unsupported object type?')
                pass

            if hit is not None:
                hit_world = obj_matrix @ hit
                length_squared = (hit_world - ray_origin).length_squared
                if hit_obj is None or length_squared < hit_length_squared:
                    hit_normal = correct_normal(obj_matrix, normal)
                    hit_wloc = hit_world
                    hit_face = face_index
                    hit_length_squared = length_squared
                    hit_obj = obj

    if hit_obj:
        return hit_obj, hit_wloc, hit_normal, hit_face
    else:
        return None, None, None, None

def get_view_type():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if len(space.region_quadviews) > 0:
                        return 'QUAD'
                    elif space.region_3d.is_perspective:
                        return 'PERSP'
                    else:
                        return 'ORTHO'

def set_active_collection(context, obj):
    avail = [i.name for i in context.view_layer.layer_collection.children]
    obj_collection = obj.users_collection[0]
    # Making sure there is no garbage invisible collection used
    for c in context.object.users_collection:
        if c.name in avail:
            obj_collection = c
            break
    layer_collection = context.view_layer.layer_collection
    layer_coll = get_layer_collection(layer_collection, obj_collection.name)
    context.view_layer.active_layer_collection = layer_coll

def get_duplicates(dl):
    # credJohnLaRooy
    seen = set()
    seen2 = set()
    seen_add = seen.add
    seen2_add = seen2.add
    for item in dl:
        if item in seen:
            seen2_add(item)
        else:
            seen_add(item)
    return list(seen2)

def pick_closest_edge(context, matrix, mousepos, edges):
    pick, prev = None, 9001
    for e in edges:
        emp = average_vector([matrix @ v.co for v in e.verts])
        p = location_3d_to_region_2d(context.region, context.space_data.region_3d, emp)
        dist = sqrt((mousepos[0] - p.x) ** 2 + (mousepos[1] - p.y) ** 2)
        if dist < prev:
            pick, prev = e, dist
    return pick

def get_edge_rings(start_edge, sel):
    max_count = 1000
    ring_edges = []
    area_bools = []
    faces_visited = []

    for loop in start_edge.link_loops:
        abools = []
        start = loop
        edges = [loop.edge]

        i = 0
        while i < max_count:
            loop = loop.link_loop_radial_next.link_loop_next.link_loop_next

            if len(loop.face.edges) != 4:
                # self.nq_report += 1
                break

            if loop.face in sel:
                abools.append(True)
                faces_visited.extend([loop.face])
            else:
                abools.append(False)
                break

            edges.append(loop.edge)

            if loop == start or loop.edge.is_boundary:
                break
            i += 1

        ring_edges.append(edges)
        area_bools.append(abools)

    edge_cuts = len(ring_edges)

    if edge_cuts == 2:
        # crappy workaround - better solution tbd
        if len(ring_edges[0]) == 1 and ring_edges[0][0] == start_edge:
            ring_edges = [ring_edges[1]]
            edge_cuts = 1
        elif len(ring_edges[1]) == 1 and ring_edges[1][0] == start_edge:
            ring_edges = [ring_edges[0]]
            edge_cuts = 1

    ring = []

    if edge_cuts == 1:
        # 1-directional (Border edge starts)
        ring = [start_edge]
        if len(area_bools[0]) == 0:
            ab = area_bools[1]
        else:
            ab = area_bools[0]

        for b, e in zip(ab, ring_edges[0][1:]):
            if b:
                ring.append(e)

    elif edge_cuts == 2:
        # Splicing bidirectional loops
        ring = [start_edge]
        for b, e in zip(area_bools[0], ring_edges[0][1:]):
            if b and e != start_edge:
                ring.append(e)

        rest = []
        for b, e in zip(area_bools[1], ring_edges[1][1:]):
            if b and e not in ring:
                rest.append(e)

        rest.reverse()
        ring = rest + ring

    return ring, list(set(faces_visited))

def getset_transform(o='GLOBAL', p='MEDIAN_POINT', setglobal=True):
    og = [bpy.context.scene.transform_orientation_slots[0].type, bpy.context.scene.tool_settings.transform_pivot_point]
    if setglobal:
        bpy.ops.transform.select_orientation(orientation=o)
        bpy.context.scene.tool_settings.transform_pivot_point = p
    return og


def restore_transform(og_op):
    bpy.ops.transform.select_orientation(orientation=og_op[0])
    bpy.context.scene.tool_settings.transform_pivot_point = og_op[1]


def apply_transform(obj, loc=False, rot=True, scl=True):
    mb = obj.matrix_basis
    idmat = Matrix()
    dloc, drot, dscl = mb.decompose()
    trmat = Matrix.Translation(dloc)
    rotmat = mb.to_3x3().normalized().to_4x4()
    sclmat = Matrix.Diagonal(dscl).to_4x4()
    transform = [idmat, idmat, idmat]
    basis = [trmat, rotmat, sclmat]

    def swap(i):
        transform[i], basis[i] = basis[i], transform[i]

    if loc:
        swap(0)
    if rot:
        swap(1)
    if scl:
        swap(2)

    mat = transform[0] @ transform[1] @ transform[2]
    if hasattr(obj.data, 'transform'):
        obj.data.transform(mat)
    for c in obj.children:
        c.matrix_local = mat @ c.matrix_local
    obj.matrix_basis = basis[0] @ basis[1] @ basis[2]
    bpy.context.evaluated_depsgraph_get().update()


def get_layer_collection(layer_coll, coll_name):
    # todo: find better solution to set active coll
    if layer_coll.name == coll_name:
        return layer_coll
    for layer in layer_coll.children:
        found = get_layer_collection(layer, coll_name)
        if found:
            return found
    return None

def get_area_and_type():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if len(space.region_quadviews) > 0:
                        return area, 'QUAD'
                    elif space.region_3d.is_perspective:
                        return area, 'PERSP'
                    else:
                        return area, 'ORTHO'

def vertloops(vertpairs):
    '''Sort verts from list of vert pairs'''
    loop_vp = [i for i in vertpairs]
    loops = []
    while len(loop_vp) > 0:
        vpsort = [loop_vp[0][0], loop_vp[0][1]]
        loop_vp.pop(0)
        loops.append(vpsort)
        for n in range(0, len(vertpairs)):
            i = 0
            for e in loop_vp:
                if vpsort[0] == e[0]:
                    vpsort.insert(0, e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[0] == e[1]:
                    vpsort.insert(0, e[0])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[0]:
                    vpsort.append(e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[1]:
                    vpsort.append(e[0])
                    loop_vp.pop(i)
                    break
                else:
                    i = i + 1
    return loops


def get_vert_nearest_mouse(context, mousepos, verts, mtx):
    nearest = 100000
    merge_point = []
    for v in verts:
        vpos = mtx @ Vector(v.co)
        vscreenpos = location_3d_to_region_2d(context.region, context.space_data.region_3d, vpos)
        if vscreenpos:
            dist = (mousepos - vscreenpos).length
            if dist < nearest:
                merge_point = v
                nearest = dist
    return merge_point

def get_distance(v1, v2):
    dist = [(a - b) ** 2 for a, b in zip(v1, v2)]
    return sqrt(sum(dist))


def is_selected_enough(self, bEdges, bVerts, edges_n=1, verts_n=0, types='Edge'):
    check = False
    try:
        if bEdges and types == 'Edge':
            check = (len(bEdges) >= edges_n)
        elif bVerts and types == 'Vertex':
            check = (len(bVerts) >= verts_n)
        elif bEdges and bVerts and types == 'All':
            check = (len(bEdges) >= edges_n and len(bVerts) >= verts_n)

        if check is False:
            strings = '%s Vertices and / or ' % verts_n if verts_n != 0 else ''
            self.report({'WARNING'},
                        'Needs at least ' + strings + '%s Edge(s) selected. '
                        'Operation Cancelled' % edges_n)
            flip_edit_mode()

        return check

    except Exception as e:
        error_handlers(self, 'is_selected_enough', e,
                      'No appropriate selection. Operation Cancelled', func=True)
        return False

    return False
def flip_edit_mode():
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    
# Handle error notifications
def error_handlers(self, op_name, error, reports='ERROR', func=False):
    if self and reports:
        self.report({'WARNING'}, reports + ' (See Console for more info)')

    is_func = 'Function' if func else 'Operator'
    print('\n[Mesh EdgeTools]\n{}: {}\nError: {}\n'.format(is_func, op_name, error))


def distance_point_line(pt, line_p1, line_p2):
    int_co = intersect_point_line(pt, line_p1, line_p2)
    distance_vector = int_co[0] - pt
    return distance_vector



def is_axial(v1, v2, error=0.000002):
    vector = v2 - v1
    # Don't need to store, but is easier to read:
    vec0 = vector[0] > -error and vector[0] < error
    vec1 = vector[1] > -error and vector[1] < error
    vec2 = vector[2] > -error and vector[2] < error
    if (vec0 or vec1) and vec2:
        return 'Z'
    elif vec0 and vec1:
        return 'Y'
    return None

def flatten(nested):
    for item in nested:
        try:
            yield from flatten(item)
        except TypeError:
            yield item


def flattened(nested):
    return list(flatten(nested))

def is_bmvert_collinear(v, tolerance=3.1415):
    le = v.link_edges
    if len(le) == 2:
        vec1 = Vector(v.co - le[0].other_vert(v).co)
        vec2 = Vector(v.co - le[1].other_vert(v).co)
        if vec1.length and vec2.length:
            if abs(vec1.angle(vec2)) >= tolerance:
                return True
    return False

def mesh_world_coords(obj):
    """Calculate verts world space coords really fast (np.einsum)"""
    n = len(obj.data.vertices)
    coords = np.empty((n * 3), dtype=float)
    obj.data.vertices.foreach_get("co", coords)
    coords = np.reshape(coords, (n, 3))
    coords4d = np.empty(shape=(n, 4), dtype=float)
    coords4d[::-1] = 1
    coords4d[:, :-1] = coords
    return np.einsum('ij,aj->ai', obj.matrix_world,  coords4d)[:, :-1]

def mesh_select_all(obj, action):
    obj.data.polygons.foreach_set("select", (action,) * len(obj.data.polygons))



def mesh_hide_all(obj, state):
    obj.data.polygons.foreach_set("hide", (state,) * len(obj.data.polygons))


def mesh_world_coords(obj):
    """Calculate verts world space coords really fast (np.einsum)"""
    n = len(obj.data.vertices)
    coords = np.empty((n * 3), dtype=float)
    obj.data.vertices.foreach_get("co", coords)
    coords = np.reshape(coords, (n, 3))
    coords4d = np.empty(shape=(n, 4), dtype=float)
    coords4d[::-1] = 1
    coords4d[:, :-1] = coords
    return np.einsum('ij,aj->ai', obj.matrix_world,  coords4d)[:, :-1]


def dupe(src):
    new = src.copy()
    new.data = src.data.copy()
    src.users_collection[0].objects.link(new)
    return new


def shred(obj):
    rem_data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(rem_data)

def cycle_mode_array(array , value):
    if value not in array:
        return array[0]
    else:
        id_old = array.index(value)
        id_next = 0
        if id_old < len(array) - 1:
            id_next = id_old + 1
        return array[id_next]


def cycle_mode_list(list , value):
    item_old = None
    item_old = [item for item in list if item[0]==value][0]
    if item_old is None:
        return list[0][0]
    else:
        id_old = list.index(item_old)
        id_next = 0
        if id_old < len(list) - 1:
            id_next = id_old + 1
        return list[id_next][0]

def shift_list(a, s):
    s %= len(a)
    s *= -1
    return a[s:] + a[:s]

def get_midpoint(p1, p2):
    mid_p = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2]
    return mid_p

def get_scene_unit(value, nearest=False):
    """Converts value to current scene setting"""
    unit_length = bpy.context.scene.unit_settings.length_unit
    unit_scale = bpy.context.scene.unit_settings.scale_length
    unit_system = bpy.context.scene.unit_settings.system
    value = value * unit_scale
    factor, unit = 1, ""

    if unit_length == 'ADAPTIVE':
        nearest = True

    if nearest and unit_system == 'METRIC':
        if value == 0:
            unit = 'm'
        elif value >= 1000:
            unit, value = 'km', value * 0.001
        elif 999 > value >= 0.9999:
            unit = 'm'
        elif 1 > value >= 0.009999:
            unit, value = 'cm', value * 100
        elif 0.01 > value >= 0.0009999:
            unit, value = 'mm', value * 1000
        elif value < 0.001:
            unit, value = '\u00b5' + 'm', value * 1000000

    elif nearest and unit_system == 'IMPERIAL':
        if value == 0:
            unit = '\u0027'
        else:
            value = round((value * 3.280839895013123), 3)  # feet
            if value >= 5280:
                unit, value = 'mi', value / 5280
            elif value >= 1:
                unit, value = '\u0027', value
            elif value > 0.0833333333:
                unit, value = '\u0022', round((value * 12), 2)
            else:
                unit, value = ' thou', int(value * 12000)

    elif unit_length == 'KILOMETERS':
        unit, factor = 'km', 0.001
    elif unit_length == 'METERS':
        unit, factor = 'm', 1
    elif unit_length == 'CENTIMETERS':
        unit, factor = 'cm', 100
    elif unit_length == 'MILLIMETERS':
        unit, factor = 'mm', 1000
    elif unit_length == 'MICROMETERS':
        unit, factor = '\u00b5' + 'm', 1000000
    elif unit_length == 'MILES':
        unit, factor = 'mi', 0.00062137119223733
    elif unit_length == 'FEET':
        unit, factor = '\u0027', 3.280839895013123
    elif unit_length == 'INCHES':
        unit, factor = '\u0022', 39.37007874015748
    elif unit_length == 'THOU':
        unit, factor = 'thou', 39370.07874015748
    else:
        unit, factor = 'bu', 1

    value = value / factor
    value = round(value, 4)
    # de-floating whole nrs
    if value.is_integer():
        value = int(value)

    return unit, value


def set_status_text(context, text_list, spacing=5, mb="\u25cf", kb="\u25a0"):
    """Unicode-icon statusbar modal-printing - remember to set to None"""
    if text_list is not None:
        separator = "\u2003" * spacing
        message = ""
        for line in text_list:
            if "WHEEL" in line or "MB" in line:
                message += mb + " " + line + separator
            else:
                message += kb + " " + line + separator
        context.workspace.status_text_set(message)
    else:
        context.workspace.status_text_set(None)

def tuple_append(tuple1, child):
    tuple1_list = list(tuple1)
    tuple1_list.append(child)
    return tuple(tuple1_list)