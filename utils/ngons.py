import bpy, bmesh, mathutils
from itertools import combinations, product
from typing import Optional
from math import inf

SMALL_NUMBER = 0.000001
KINDA_SMALL_NUMBER = 0.001
clamp = lambda x, l, u: l if x < l else u if x > u else x



class FixNgonsRecursively:
    # used for optimization of brute-forcefully calculating all possible quads areas
    possible_quad_indices_per_vert_count = dict()
    min_face_area = 0.001

    def __init__(self, bm:bmesh.types.BMesh, allowed_faces:list[bmesh.types.BMFace], max_recursion_depth:int=100):
        self.current_recursion_depth = 0
        self.current_loop = list()
        self.allowed_faces = allowed_faces.copy()
        self.bm = bm
        self.max_recursion_depth = max_recursion_depth
        self.connect_pairs = list()

        to_fix = [f for f in self.allowed_faces if len(f.verts) > 4]
        for f in to_fix:
            if not f.is_valid:
                continue
            self.fixing = [f]
            self.fix_ngons_recursion()
            self.current_recursion_depth = 0
            self.current_loop = list()

        for f in self.allowed_faces:
            f.select = True
        bmesh.ops.recalc_face_normals(bm, faces=self.allowed_faces)


    def fix_ngons_recursion(self):
        # finished
        if len(self.fixing) == 0:
            return

        # recursion depth check
        self.current_recursion_depth += 1
        if self.current_recursion_depth > self.max_recursion_depth:
            return

        # get the next face to fix
        f = self.fixing[0]

        # get verts to fix and quad verts
        verts = sort_face_verts(f)
        quad_verts = self.get_quad_verts(verts)
        if quad_verts is None:
            self.fixing = self.fixing[1:]
            self.fix_ngons_recursion()
            return
        verts_to_fix = [v for v in verts if v not in quad_verts]

        if len(rel_pairs := [p for p in self.connect_pairs if p[0] in verts_to_fix and p[1] in verts_to_fix]) > 0:
            self.try_split_into_two_faces(f, verts, rel_pairs[0][0], rel_pairs[0][1])

            self.fix_ngons_recursion()
            return
        else:
            possibilities = [(v1, v2) for (v1, v2) in combinations(verts_to_fix, 2) if can_connect_verts_to_create_edge_quad(verts, v1, v2, verts_to_fix)]
            if len(possibilities) > 0:
                # prefer creating shorter edges
                v1, v2 = min(possibilities, key=lambda x: (x[0].co - x[1].co).length)
                self.try_split_into_two_faces(f, verts, v1, v2)

                self.fix_ngons_recursion()
                return

        # get the edges on the opposite sides to the ones that we want to fix
        if len(verts_to_fix) > 0:
            v_fix = verts_to_fix[0]
            v_fix_index = v_fix.index
            e = get_edge_opposite_to_vertex(f, v_fix, verts, quad_verts)

            # get quad verts going left
            left_quad_verts = list()
            current_index = verts.index(v_fix)
            while not (current_vert := verts[(current_index := current_index - 1) % len(verts)]) in quad_verts:
                pass
            left_quad_verts.append(current_vert)
            while not (current_vert := verts[(current_index := current_index - 1) % len(verts)]) in quad_verts:
                pass
            left_quad_verts.append(current_vert)

            # get quad verts going right
            right_quad_verts = list()
            current_index = verts.index(v_fix)
            while not (current_vert := verts[(current_index := current_index + 1) % len(verts)]) in quad_verts:
                pass
            right_quad_verts.append(current_vert)
            while not (current_vert := verts[(current_index := current_index + 1) % len(verts)]) in e.verts:
                pass
            right_quad_verts.append(current_vert)

            line_dir = calculate_median_point([(left_quad_verts[1].co - left_quad_verts[0].co).normalized() + (right_quad_verts[1].co - right_quad_verts[0].co).normalized()]).normalized()
            plane_normal = line_dir
            plane_origin = calculate_median_point([right_quad_verts[1].co, left_quad_verts[1].co])
            new_pos_raw = line_plane_intersection(v_fix.co, v_fix.co + line_dir, plane_origin, plane_normal)

            if is_projected_point_on_segment(new_pos_raw, e.verts[0].co, e.verts[1].co):
                new_vertpos = project_point_on_line(new_pos_raw, e.verts[0].co, e.verts[1].co)
            else:
                distance_left = (left_quad_verts[0].co - v_fix.co).length
                distance_right = (right_quad_verts[0].co - v_fix.co).length
                other_vert = other_edge_vertex(right_quad_verts[1], e)
                ab = other_vert.co - current_vert.co
                new_vertpos = current_vert.co + ab * max(distance_right / (distance_left + distance_right), 0.00001)

            bisect_result = bmesh.ops.bisect_edges(self.bm, edges=[e], cuts=1)['geom_split']
            self.bm.verts.ensure_lookup_table()
            self.bm.edges.ensure_lookup_table()
            self.bm.faces.ensure_lookup_table()

            new_vert = [x for x in bisect_result if isinstance(x, bmesh.types.BMVert)][0]
            new_vert.co = new_vertpos

            self.connect_pairs.append((self.bm.verts[v_fix_index], new_vert))

            # add the other face altered by bisection to the faces which require fixing
            other_faces = [f1 for f1 in new_vert.link_faces if f1.index != f.index]
            if len(other_faces) > 0 and (other_face := other_faces[0]) in self.allowed_faces and len(other_face.verts) > 4 and other_face not in self.fixing:
                if any([v.index in self.current_loop for v in other_face.verts]):
                    other_verts = sort_face_verts(other_face)
                    other_quad_verts = self.get_quad_verts(other_verts)
                    if other_quad_verts is None:
                        self.fix_ngons_recursion()
                        return
                    opposite = get_edge_opposite_to_vertex(other_face, new_vert, other_verts, other_quad_verts)
                    v2 = opposite.verts[0] if (opposite.verts[0].co - new_vert.co).length < (opposite.verts[1].co - new_vert.co).length else opposite.verts[1]
                    self.try_split_into_two_faces(other_face, sort_face_verts(other_face), new_vert, v2)
                else:
                    self.fixing = [other_face] + self.fixing
                    self.current_loop += [v_fix_index, new_vert.index]

        self.fix_ngons_recursion()
        return


    def try_split_into_two_faces(self, f:bmesh.types.BMFace, sorted_verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert) -> tuple[bmesh.types.BMFace, bmesh.types.BMFace]:
        # split into two faces if possible to join
        v1_index = sorted_verts.index(v1)
        verts_len = len(sorted_verts)

        # face 1
        verts1 = [v1]
        i = v1_index
        while sorted_verts[i] != v2:
            i = (i + 1) % verts_len
            verts1.append(sorted_verts[i])

        # face 2
        verts2 = [v1]
        i = v1_index
        while sorted_verts[i] != v2:
            i = (i - 1) % verts_len
            verts2.append(sorted_verts[i])

        # don't create faces with very small area (leave ngons but it's more reasonable in this case)
        if polygon_area([v.co for v in verts1]) > FixNgonsRecursively.min_face_area and polygon_area([v.co for v in verts2]) > FixNgonsRecursively.min_face_area:
            # create the faces and add them to allowed faces
            failed1 = False
            try:
                face1 = self.bm.faces.new(verts1)
                face1.smooth = f.smooth
                self.allowed_faces.append(face1)
            except:
                failed1 = True

            failed2 = False
            try:
                face2 = self.bm.faces.new(verts2)
                face2.smooth = f.smooth
                self.allowed_faces.append(face2)
            except:
                failed2 = True

            # update fixing
            if f in self.fixing:
                self.fixing.remove(f)

            if failed1 or failed2:
                return

            if len(face1.verts) > 4:
                self.fixing = [face1] + self.fixing
            if len(face2.verts) > 4:
                self.fixing = [face2] + self.fixing

            # remove the old face from allowed faces and delete it
            if f in self.allowed_faces:
                self.allowed_faces.remove(f)
            bmesh.ops.delete(self.bm, geom=[f], context='FACES')

        else:
            if f in self.fixing:
                self.fixing.remove(f)


    def get_quad_verts(self, sorted_verts:list[bmesh.types.BMVert]) -> list[bmesh.types.BMVert]:
        verts_count = len(sorted_verts)
        # work out the quad verts and the verts to fix
        if verts_count in FixNgonsRecursively.possible_quad_indices_per_vert_count:
            quads = FixNgonsRecursively.possible_quad_indices_per_vert_count[verts_count]
        else:
            indices = [i for i, v in enumerate(sorted_verts)]
            quads = [sorted(quad) for quad in combinations(indices, 4)]
            FixNgonsRecursively.possible_quad_indices_per_vert_count[verts_count] = quads

        quad_verts_indices = max(quads, key=lambda quad: polygon_area([sorted_verts[i].co for i in quad]))
        # prevent working with faces with very small area
        if polygon_area([sorted_verts[i].co for i in quad_verts_indices]) < FixNgonsRecursively.min_face_area:
            return None
        return [sorted_verts[i] for i in quad_verts_indices] 

def show_message(message = "", title = "Info", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_bmesh(obj, ensure_verts=True, ensure_edges=False, ensure_faces=False):
    mesh = obj.data
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(mesh)
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)

    if ensure_verts:
        bm.verts.ensure_lookup_table()
    if ensure_edges:
        bm.edges.ensure_lookup_table()
    if ensure_faces:
        bm.faces.ensure_lookup_table()

    return bm


# only supports one-level flattening
def flattened(arr:list[list]) -> list:
    return [item for sublist in arr for item in sublist]


def update_bmesh(obj, bm:bmesh.types.BMesh):
    if obj.mode == 'EDIT':
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)


def free_bmesh(obj, bm:bmesh.types.BMesh):
    if obj.mode != 'EDIT':
        bm.free()


def get_selection_normal(vertpos:list[mathutils.Vector], normals:Optional[list[mathutils.Vector]]) -> mathutils.Vector:
    if len(vertpos) == 0:
        raise Exception('Invalid verts to get normal from')

    # get hold of the selection normal:
    # create a face using the fill operator
    bm = bmesh.new()
    for v in vertpos:
        bm.verts.new(v)

    bm.verts.ensure_lookup_table()

    result = bmesh.ops.contextual_create(bm, geom=bm.verts, use_smooth=True)
    face = result['faces'][0]
    face.normal_update()

    # use vertex normal average to decide on flipping of the created normal
    vertex_normal_avg = calculate_median_point([v for v in normals])

    # flip if necessary
    if face.normal.dot(vertex_normal_avg) < 0:
        face.normal_flip()

    selection_normal = face.normal.copy()
    bm.free()

    return selection_normal


def edge_exists(v1:bmesh.types.BMVert, v2:bmesh.types.BMVert):
    return v2 in [x for y in [a.verts for a in v1.link_edges] for x in y if x != v1]


def other_edge_vertex_index(edge_vertices:list[int], to_ignore:list[int]) -> Optional[int]:
    if edge_vertices is None:
        return None

    for v in edge_vertices:
        if v is not None and v not in to_ignore:
            return v
    return None


def other_edge_vertex(v:bmesh.types.BMVert, edge:bmesh.types.BMEdge) -> Optional[bmesh.types.BMVert]:
    if v not in edge.verts:
        return None
    return edge.verts[0] if edge.verts[0] != v else edge.verts[1]


# TODO: incorporate link edges in here
def get_edge_connections(edges:list[bmesh.types.BMEdge]) -> dict[bmesh.types.BMVert, list[bmesh.types.BMVert]]:
    edge_connections = dict()
    for e in edges:
        v1, v2 = e.verts[0], e.verts[1]

        edge_connections.setdefault(v1, list()).append(v2)
        edge_connections.setdefault(v2, list()).append(v1)

    return edge_connections


def get_edge_connections_index(edges:list[bmesh.types.BMEdge]) -> dict[int, list[int]]:
    result = dict()
    edge_connections = get_edge_connections(edges)
    for v, con in edge_connections.items():
        result[v.index] = [x.index for x in con]
    
    return result


def loop_by_vert_index(loops:list[list[int]], vert:int) -> Optional[list[int]]:
    for loop in loops:
        if vert in loop:
            return loop
    return None


# returns the list of lists of vertex indices, the verts order is reliable: indices next to each other should correspond if they are i.e. bevel edges
def get_separated_sorted_loops(edges:list[bmesh.types.BMEdge]) -> list[list[int]]:
    edge_connections = get_edge_connections_index(edges)

    remaining = list(edge_connections.keys())
    result = list()
    while len(remaining) > 0:
        # ensure that the selection is correct and select the tip as the starting point if available
        current = None
        for i, con in edge_connections.items():
            l = len(con)
            if l == 0:
                raise Exception('Singular vertices selected!')
            elif l == 1:
                current = i
            elif l > 2:
                raise Exception('More than 2 edges branch out from a vertex!')

        current = remaining[0] if current is None else current
        
        sorted_indices = [current]
        while (next := other_edge_vertex_index(edge_connections.pop(current, None), sorted_indices)) != None:
            current = next
            sorted_indices.append(current)

        result.append(sorted_indices)
        remaining = [i for i in remaining if i not in sorted_indices]

    return result


# returns loops that will have correct corresponding verts (there's a linking edge between them) and in the order such that
# the loops are like [boundary1, next_to_boundary1, next_to_next_to_boundary1, ... next_to_boundary_2, boundary2]
def get_separated_sorted_loops_bevel(bm: bmesh.types.BMesh, edges:list[bmesh.types.BMEdge]) -> list[list[int]]:
    loops = get_separated_sorted_loops(edges)
    
    # rearrange the sorted indices so that the loops starting points are linked if loops are closed
    # reorder the loops so they are like [boundary1, next_to_boundary1, next_to_next_to_boundary1, ... next_to_boundary_2, boundary2]
    all_linking_edges = set()
    verts_to_check = [loops[0][0]]
    verts_checked = list()
    while len(verts_to_check) > 0:
        v_check = verts_to_check.pop(0)
        verts_checked.append(v_check)
        loop = loop_by_vert_index(loops, v_check)
        other_loops_verts_indices = flattened([l for l in loops if l != loop])
        linking_edges = [e for e in bm.verts[v_check].link_edges if other_edge_vertex(bm.verts[v_check], e).index in other_loops_verts_indices]
        all_linking_edges.update(linking_edges)
        for e in linking_edges:
            other_v = other_edge_vertex(bm.verts[v_check], e).index
            if other_v not in verts_checked:
                verts_to_check.append(other_v)

    sorted_linking_verts = get_separated_sorted_loops(list(all_linking_edges))[0]
    for i in range(len(loops)):
        index_of_first = [loops[i].index(v_index) for v_index in sorted_linking_verts if v_index in loops[i]][0]
        loops[i] = loops[i][index_of_first:] + loops[i][:index_of_first]

    ordered_loops = list()
    for v in sorted_linking_verts:
        ordered_loops.append(loop_by_vert_index(loops, v))

    loops = ordered_loops

    # check if loops are not the other way round = check if the verts are corresponding - allows to rely on the order of vertices
    for i in range(1, len(loops)):
        v1 = bm.verts[loops[i - 1][0]]
        v2 = bm.verts[loops[i - 1][1]]

        connected_verts_indices_v1 = [other_edge_vertex(v1, e).index for e in v1.link_edges]
        connected_verts_indices_v2 = [other_edge_vertex(v2, e).index for e in v2.link_edges]

        if loops[i][0] not in connected_verts_indices_v1:
            raise Exception('Wrong unbevel selection!!!')
        if loops[i][1] not in connected_verts_indices_v2:
            loops[i] = [loops[i][0]] + loops[i][1:][::-1]

    return loops


def group_loops(loops:list[list[int]], relevant_faces:list[bmesh.types.BMFace]) -> list[tuple[set[int]]]:
    # TODO: further optimization: instead of looping through these combinations,
    #  for each loop compute which loop it is connected to by
    #  getting hold of all linked vertices (through linked edges/faces) to the vertices of the loop
    result = list()
    for i, j in combinations(range(len(loops)), 2):
        shared_i, shared_j = list(), list()
        for f in relevant_faces:
            in_i = [v.index for v in f.verts if v.index in loops[i]]
            in_j = [v.index for v in f.verts if v.index in loops[j]]

            if len(in_i) > 0 and len(in_j) > 0:
                shared_i += in_i
                shared_j += in_j

        result.append(((set(shared_i), set(shared_j))))

    return result


# returns a dictionary of lists of possible edges (tuple of vert indices) for each face (keys are face indices)
# this doesn't care about existing edges but it should be fine...
def possible_edges(loop_groups:list[tuple[set[int]]], relevant_faces:list[bmesh.types.BMFace]) -> list[list[tuple[int]]]:
    possible_edges = list()
    for a, b in loop_groups:
        possible_subedges = list()
        for f in relevant_faces:
            verts_from_a = [v.index for v in f.verts if v.index in a]
            verts_from_b = [v.index for v in f.verts if v.index in b]
            possible_subedges += product(verts_from_a, verts_from_b)

        possible_edges.append(possible_subedges)

    # then sort them by increasing edge length
    return possible_edges


# sorted by edge length so that shortest edges come in first,
# removes edges that would cause duplication and so on
def viable_edges(bm:bmesh.types.BMesh, possible_edges:list[list[tuple[int]]]) -> list[list[tuple[int]]]:
    all_viable = list()
    for edgeset in possible_edges:
        edges = sorted(edgeset, key=lambda e: (bm.verts[e[0]].co - bm.verts[e[1]].co).length)

        viable = list()
        seen_verts = set()
        for e in edges:
            if e[0] not in seen_verts and e[1] not in seen_verts:
                seen_verts.update((e[0], e[1]))
                viable.append(e)
        all_viable.append(viable)
        
    return all_viable


# find out relevant faces (no need to loop through everything if we have only selected x number of verts)
def get_relevant_faces(bm:bmesh.types.BMesh, verts_indices:list[int]) -> set[bmesh.types.BMFace]:
    return list(set(flattened([v.link_faces for v in [bm.verts[i] for i in verts_indices]])))


def calculate_straightened_point(vert:bmesh.types.BMVert, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector, straighten_mode:str, all_straightened_verts:list[bmesh.types.BMVert], edge_choosing_distance_treshold:float=0.1) ->mathutils.Vector:
    if straighten_mode == 'simple':
        return project_point_on_plane(vert.co, plane_origin, plane_normal)
    elif straighten_mode == 'edges':
        # select the edges so that they are not included within our selected faces: in case of 2+ outgoing edges, use their average direction as the line
        possible_line_verts = [other_edge_vertex(vert, e) for e in vert.link_edges if e.verts[0] not in all_straightened_verts or e.verts[1] not in all_straightened_verts]

        # no edges to use, just use simple projection
        if len(possible_line_verts) == 0:
            return project_point_on_plane(vert.co, plane_origin, plane_normal)
        # find the line intersection, in case of parallel: simple projection
        else:
            distances = [(vert.co - line_plane_intersection(vert.co, v.co, plane_origin, plane_normal)).length for v in possible_line_verts]
            verts_dist = sorted(zip(possible_line_verts, distances), key=lambda x: x[1])
            verts_dist = [(x[0], x[1] - verts_dist[0][1]) for x in verts_dist]
            possible_line_verts = [x[0] for x in verts_dist if x[1] <= edge_choosing_distance_treshold]

            median = calculate_median_point([x.co for x in possible_line_verts])
            p = line_plane_intersection(vert.co, median, plane_origin, plane_normal)
            if p is None:
                return project_point_on_plane(vert.co, plane_origin, plane_normal)
            else:
                return p
    else:
        return vert.co


def edge_by_vertex_indices(v1:int, v2:int, possible_edges:list[bmesh.types.BMEdge]) -> Optional[bmesh.types.BMEdge]:
    for e in possible_edges:
        if e.verts[0].index == v1 and e.verts[1].index == v2 or e.verts[0].index == v2 and e.verts[1].index == v1:
            return e
    return None


# call like a function and it will fix the ngons automatically
class FixNgonsRecursively:
    # used for optimization of brute-forcefully calculating all possible quads areas
    possible_quad_indices_per_vert_count = dict()
    min_face_area = 0.001

    def __init__(self, bm:bmesh.types.BMesh, allowed_faces:list[bmesh.types.BMFace], max_recursion_depth:int=100):
        self.current_recursion_depth = 0
        self.current_loop = list()
        self.allowed_faces = allowed_faces.copy()
        self.bm = bm
        self.max_recursion_depth = max_recursion_depth
        self.connect_pairs = list()

        to_fix = [f for f in self.allowed_faces if len(f.verts) > 4]
        for f in to_fix:
            if not f.is_valid:
                continue
            self.fixing = [f]
            self.fix_ngons_recursion()
            self.current_recursion_depth = 0
            self.current_loop = list()

        for f in self.allowed_faces:
            f.select = True
        bmesh.ops.recalc_face_normals(bm, faces=self.allowed_faces)


    def fix_ngons_recursion(self):
        # finished
        if len(self.fixing) == 0:
            return

        # recursion depth check
        self.current_recursion_depth += 1
        if self.current_recursion_depth > self.max_recursion_depth:
            return

        # get the next face to fix
        f = self.fixing[0]

        # get verts to fix and quad verts
        verts = sort_face_verts(f)
        quad_verts = self.get_quad_verts(verts)
        if quad_verts is None:
            self.fixing = self.fixing[1:]
            self.fix_ngons_recursion()
            return
        verts_to_fix = [v for v in verts if v not in quad_verts]

        if len(rel_pairs := [p for p in self.connect_pairs if p[0] in verts_to_fix and p[1] in verts_to_fix]) > 0:
            self.try_split_into_two_faces(f, verts, rel_pairs[0][0], rel_pairs[0][1])

            self.fix_ngons_recursion()
            return
        else:
            possibilities = [(v1, v2) for (v1, v2) in combinations(verts_to_fix, 2) if can_connect_verts_to_create_edge_quad(verts, v1, v2, verts_to_fix)]
            if len(possibilities) > 0:
                # prefer creating shorter edges
                v1, v2 = min(possibilities, key=lambda x: (x[0].co - x[1].co).length)
                self.try_split_into_two_faces(f, verts, v1, v2)

                self.fix_ngons_recursion()
                return

        # get the edges on the opposite sides to the ones that we want to fix
        if len(verts_to_fix) > 0:
            v_fix = verts_to_fix[0]
            v_fix_index = v_fix.index
            e = get_edge_opposite_to_vertex(f, v_fix, verts, quad_verts)

            # get quad verts going left
            left_quad_verts = list()
            current_index = verts.index(v_fix)
            while not (current_vert := verts[(current_index := current_index - 1) % len(verts)]) in quad_verts:
                pass
            left_quad_verts.append(current_vert)
            while not (current_vert := verts[(current_index := current_index - 1) % len(verts)]) in quad_verts:
                pass
            left_quad_verts.append(current_vert)

            # get quad verts going right
            right_quad_verts = list()
            current_index = verts.index(v_fix)
            while not (current_vert := verts[(current_index := current_index + 1) % len(verts)]) in quad_verts:
                pass
            right_quad_verts.append(current_vert)
            while not (current_vert := verts[(current_index := current_index + 1) % len(verts)]) in e.verts:
                pass
            right_quad_verts.append(current_vert)

            line_dir = calculate_median_point([(left_quad_verts[1].co - left_quad_verts[0].co).normalized() + (right_quad_verts[1].co - right_quad_verts[0].co).normalized()]).normalized()
            plane_normal = line_dir
            plane_origin = calculate_median_point([right_quad_verts[1].co, left_quad_verts[1].co])
            new_pos_raw = line_plane_intersection(v_fix.co, v_fix.co + line_dir, plane_origin, plane_normal)

            if is_projected_point_on_segment(new_pos_raw, e.verts[0].co, e.verts[1].co):
                new_vertpos = project_point_on_line(new_pos_raw, e.verts[0].co, e.verts[1].co)
            else:
                distance_left = (left_quad_verts[0].co - v_fix.co).length
                distance_right = (right_quad_verts[0].co - v_fix.co).length
                other_vert = other_edge_vertex(right_quad_verts[1], e)
                ab = other_vert.co - current_vert.co
                new_vertpos = current_vert.co + ab * max(distance_right / (distance_left + distance_right), 0.00001)

            bisect_result = bmesh.ops.bisect_edges(self.bm, edges=[e], cuts=1)['geom_split']
            self.bm.verts.ensure_lookup_table()
            self.bm.edges.ensure_lookup_table()
            self.bm.faces.ensure_lookup_table()

            new_vert = [x for x in bisect_result if isinstance(x, bmesh.types.BMVert)][0]
            new_vert.co = new_vertpos

            self.connect_pairs.append((self.bm.verts[v_fix_index], new_vert))

            # add the other face altered by bisection to the faces which require fixing
            other_faces = [f1 for f1 in new_vert.link_faces if f1.index != f.index]
            if len(other_faces) > 0 and (other_face := other_faces[0]) in self.allowed_faces and len(other_face.verts) > 4 and other_face not in self.fixing:
                if any([v.index in self.current_loop for v in other_face.verts]):
                    other_verts = sort_face_verts(other_face)
                    other_quad_verts = self.get_quad_verts(other_verts)
                    if other_quad_verts is None:
                        self.fix_ngons_recursion()
                        return
                    opposite = get_edge_opposite_to_vertex(other_face, new_vert, other_verts, other_quad_verts)
                    v2 = opposite.verts[0] if (opposite.verts[0].co - new_vert.co).length < (opposite.verts[1].co - new_vert.co).length else opposite.verts[1]
                    self.try_split_into_two_faces(other_face, sort_face_verts(other_face), new_vert, v2)
                else:
                    self.fixing = [other_face] + self.fixing
                    self.current_loop += [v_fix_index, new_vert.index]

        self.fix_ngons_recursion()
        return


    def try_split_into_two_faces(self, f:bmesh.types.BMFace, sorted_verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert) -> tuple[bmesh.types.BMFace, bmesh.types.BMFace]:
        # split into two faces if possible to join
        v1_index = sorted_verts.index(v1)
        verts_len = len(sorted_verts)

        # face 1
        verts1 = [v1]
        i = v1_index
        while sorted_verts[i] != v2:
            i = (i + 1) % verts_len
            verts1.append(sorted_verts[i])

        # face 2
        verts2 = [v1]
        i = v1_index
        while sorted_verts[i] != v2:
            i = (i - 1) % verts_len
            verts2.append(sorted_verts[i])

        # don't create faces with very small area (leave ngons but it's more reasonable in this case)
        if polygon_area([v.co for v in verts1]) > FixNgonsRecursively.min_face_area and polygon_area([v.co for v in verts2]) > FixNgonsRecursively.min_face_area:
            # create the faces and add them to allowed faces
            failed1 = False
            try:
                face1 = self.bm.faces.new(verts1)
                face1.smooth = f.smooth
                self.allowed_faces.append(face1)
            except:
                failed1 = True

            failed2 = False
            try:
                face2 = self.bm.faces.new(verts2)
                face2.smooth = f.smooth
                self.allowed_faces.append(face2)
            except:
                failed2 = True

            # update fixing
            if f in self.fixing:
                self.fixing.remove(f)

            if failed1 or failed2:
                return

            if len(face1.verts) > 4:
                self.fixing = [face1] + self.fixing
            if len(face2.verts) > 4:
                self.fixing = [face2] + self.fixing

            # remove the old face from allowed faces and delete it
            if f in self.allowed_faces:
                self.allowed_faces.remove(f)
            bmesh.ops.delete(self.bm, geom=[f], context='FACES')

        else:
            if f in self.fixing:
                self.fixing.remove(f)


    def get_quad_verts(self, sorted_verts:list[bmesh.types.BMVert]) -> list[bmesh.types.BMVert]:
        verts_count = len(sorted_verts)
        # work out the quad verts and the verts to fix
        if verts_count in FixNgonsRecursively.possible_quad_indices_per_vert_count:
            quads = FixNgonsRecursively.possible_quad_indices_per_vert_count[verts_count]
        else:
            indices = [i for i, v in enumerate(sorted_verts)]
            quads = [sorted(quad) for quad in combinations(indices, 4)]
            FixNgonsRecursively.possible_quad_indices_per_vert_count[verts_count] = quads

        quad_verts_indices = max(quads, key=lambda quad: polygon_area([sorted_verts[i].co for i in quad]))
        # prevent working with faces with very small area
        if polygon_area([sorted_verts[i].co for i in quad_verts_indices]) < FixNgonsRecursively.min_face_area:
            return None
        return [sorted_verts[i] for i in quad_verts_indices] 


def sort_face_verts(face:bmesh.types.BMFace) -> list[bmesh.types.BMVert]:
    available_edges = list(face.edges)

    current = available_edges[0].verts[0]
    result = [current]

    while len(available_edges) > 0:
        possible_edges = [e for e in available_edges if current in e.verts]
        available_edges = [e for e in available_edges if e not in possible_edges]
        next_edge = possible_edges[0]
        current = other_edge_vertex(current, next_edge)
        result.append(current)
    return result


def get_edge_opposite_to_vertex(face:bmesh.types.BMFace, vert:bmesh.types.BMVert, sorted_verts:list[bmesh.types.BMVert], quad_verts:list[bmesh.types.BMVert]) -> bmesh.types.BMEdge:
    eligible_edges = [e for e in face.edges if vert not in e.verts]
    with_dots = [(e, abs((calculate_median_point([v.co for v in e.verts]) - vert.co).normalized().dot((e.verts[0].co - e.verts[1].co).normalized()))) for e in eligible_edges]
    with_dots.sort(key=lambda x: x[1])

    # ensure that the new edge is at least 2 quad verts away from the vert
    for x in with_dots:
        e = x[0]
        path0, path1 = path_between_sorted_verts(sorted_verts, vert, e.verts[0]), path_between_sorted_verts(sorted_verts, vert, e.verts[1])
        path = path0 if len(path0) < len(path1) else path1

        if [v in path for v in quad_verts].count(True) != 2:
            continue
        return e
    return None


def path_between_sorted_verts(verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert) -> list[bmesh.types.BMVert]:
    verts_len = len(verts)

    result1 = [v1]
    i = verts.index(v1)
    while verts[i] != v2:
        i = (i - 1) % verts_len
        result1.append(verts[i])
    
    result2 = [v1]
    i = verts.index(v1)
    while verts[i] != v2:
        i = (i + 1) % verts_len
        result2.append(verts[i])

    return result1 if len(result1) < len(result2) else result2


def distance_between_sorted_verts(verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert) -> int:
    v1_index, v2_index = verts.index(v1), verts.index(v2)
    bigger, smaller = (v1_index, v2_index) if v1_index > v2_index else (v2_index, v1_index)
    return min(len(verts) - bigger + smaller, bigger - smaller)


# dir either 'r' or 'l' to go right in the list or left
def traverse_check_two_quad_corners_visited(verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert, to_fix:list[bmesh.types.BMVert], dir:str='r') -> bool:
    addend = 1 if dir == 'r' else -1
    verts_len = len(verts)
    quad_verts = [v for v in verts if v not in to_fix]

    corner_counter = 0
    i = verts.index(v1)
    while verts[i] != v2:
        i = (i + addend) % verts_len
        if verts[i] in quad_verts:
            corner_counter += 1
            continue
        
        if corner_counter == 0 and verts[i] in to_fix:
            return False
        if corner_counter == 2:
            return verts[i] == v2
        elif corner_counter > 2:
            return False

    return False


# only avoid counting to_fix if they are before the second quad corner
def can_connect_verts_to_create_edge_quad(verts:list[bmesh.types.BMVert], v1:bmesh.types.BMVert, v2:bmesh.types.BMVert, to_fix:list[bmesh.types.BMVert]) -> Optional[list[bmesh.types.BMVert]]:
    return traverse_check_two_quad_corners_visited(verts, v1, v2, to_fix, 'r') or traverse_check_two_quad_corners_visited(verts, v1, v2, to_fix, 'l')


def nearby_plane_normal(v:bmesh.types.BMVert, verts:list[bmesh.types.BMVert], cyclic:bool) -> Optional[mathutils.Vector]:
    if v not in verts or len(verts) < 3:
        return None

    verts_len = len(verts)
    v_mid = v
    v_mid_index = verts.index(v_mid)
    if cyclic:
        v_right_index = (v_mid_index + 1) % verts_len
        v_right = verts[v_right_index]
        v_left_index = (v_mid_index - 1) % verts_len
        v_left = verts[v_left_index]

        i = 0
        while collinear_three_points(v_left.co, v_mid.co, v_right.co):
            if v_right == v_mid or v_left == v_mid or v_left == v_right:
                return None
            if i % 2 == 0:
                v_right_index = (v_right_index + 1) % verts_len
                v_right = verts[v_right_index]
            else:
                v_left_index = (v_left_index - 1) % verts_len
                v_left = verts[v_left_index]
            i += 1

    else:
        if v_mid_index == 0:
            v_right_index = clamp(v_mid_index + 2, 0, verts_len - 1)
            v_right = verts[v_right_index]
            v_left_index = clamp(v_mid_index + 1, 0, verts_len - 1) 
            v_left = verts[v_left_index]

            i = 0
            while collinear_three_points(v_left.co, v_mid.co, v_right.co):
                if v_right == v_mid or v_left == v_mid or v_left == v_right:
                    return None
                if i % 2 == 0:
                    v_right_index = clamp(v_right_index + 1, 0, verts_len - 1)
                    v_right = verts[v_right_index]
                else:
                    v_left_index = clamp(v_left_index + 1, 0, verts_len - 1)
                    v_left = verts[v_left_index]
                i += 1

        elif v_mid_index == verts_len - 1:
            v_right_index = clamp(v_mid_index - 2, 0, verts_len - 1)
            v_right = verts[v_right_index]
            v_left_index = clamp(v_mid_index - 1, 0, verts_len - 1) 
            v_left = verts[v_left_index]

            i = 0
            while collinear_three_points(v_left.co, v_mid.co, v_right.co):
                if v_right == v_mid or v_left == v_mid or v_left == v_right:
                    return None
                if i % 2 == 0:
                    v_right_index = clamp(v_right_index - 1, 0, verts_len - 1)
                    v_right = verts[v_right_index]
                else:
                    v_left_index = clamp(v_left_index - 1, 0, verts_len - 1)
                    v_left = verts[v_left_index]
                i += 1

        else:
            v_right_index = clamp(v_mid_index + 1, 0, verts_len - 1)
            v_right = verts[v_right_index]
            v_left_index = clamp(v_mid_index - 1, 0, verts_len - 1) 
            v_left = verts[v_left_index]

            i = 0
            while collinear_three_points(v_left.co, v_mid.co, v_right.co):
                if v_right == v_mid or v_left == v_mid or v_left == v_right:
                    return None
                if i % 2 == 0:
                    v_right_index = clamp(v_right_index + 1, 0, verts_len - 1)
                    v_right = verts[v_right_index]
                else:
                    v_left_index = clamp(v_left_index - 1, 0, verts_len - 1)
                    v_left = verts[v_left_index]
                i += 1

    return get_selection_normal([v_left.co, v_mid.co, v_right.co], [v_left.normal, v_mid.normal, v_right.normal])

def point_to_plane_dist(p:mathutils.Vector, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector):
    v = p - plane_origin
    return abs(v.dot(plane_normal))

class Plane:
    # index just for the reference
    def __init__(self, center:mathutils.Vector, normal:mathutils.Vector, index:int=None) -> None:
        self.center = center
        self.normal = normal
        self.index = index

    # NOTE: for our purpose, just compare the normals of the two planes
    def __eq__(self, other: object) -> bool:
        return vectors_equal(self.normal, other.normal)

    # # NOTE: for our purpose, just use the hash of the normal
    # def __hash__(self) -> int:
    #     return id(self.normal)
    
    def __str__(self) -> str:
        return "Plane: center={} normal={} index={}".format(self.center, self.normal, self.index)
    
    def __repr__(self) -> str:
        return str(self)


def project_point_on_line(p: mathutils.Vector, a: mathutils.Vector, b: mathutils.Vector, epsilon:float=SMALL_NUMBER) -> mathutils.Vector:
    ap = p - a
    ab = b - a
    return a + ap.dot(ab) / max(ab.dot(ab), epsilon) * ab


def is_projected_point_on_segment(p: mathutils.Vector, a:mathutils.Vector, b:mathutils.Vector) -> bool:
    ap = p - a
    ab = b - a
    dot = ab.dot(ap)
    return dot > 0 and dot < ab.length_squared


def project_point_on_plane(p:mathutils.Vector, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector):
    v = p - plane_origin
    dist = v.dot(plane_normal)
    return p - dist * plane_normal


def point_to_plane_dist(p:mathutils.Vector, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector):
    v = p - plane_origin
    return abs(v.dot(plane_normal))


def point_to_plane_dist_signed(p:mathutils.Vector, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector):
    v = p - plane_origin
    return -v.dot(plane_normal)


def line_plane_intersection(a:mathutils.Vector, b:mathutils.Vector, plane_origin:mathutils.Vector, plane_normal:mathutils.Vector, epsilon:float=1e-6) -> Optional[mathutils.Vector]:
    u = b - a
    dot = plane_normal.dot(u)

    if abs(dot) > epsilon:
        # The factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # Otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = a - plane_origin
        fac = -plane_normal.dot(w) / dot
        u *= fac
        return a + u

    # in case the line is parallel to the plane
    return None


def calculate_median_point(verts:list[mathutils.Vector]) -> mathutils.Vector:
    if len(verts) == 0:
        return None

    co_sum = mathutils.Vector([sum([v[0] for v in verts]),
                               sum([v[1] for v in verts]),
                               sum([v[2] for v in verts])])
    return co_sum / len(verts)


class Node:
    @property
    def edges(self):
        return (e for e in self.vert.link_edges if not e.tag)
    
    def __init__(self, v):
        self.vert = v
        self.length = inf
        self.shortest_path = []
        

def dijkstra(bm, v_start, v_target=None):
    for e in bm.edges:
        e.tag = False
    
    d = {v : Node(v) for v in bm.verts}
    node = d[v_start]
    node.length = 0
    
    visiting = [node]

    while visiting:
        node = visiting.pop(0)
        
        if node.vert is v_target:
            return d
        
        for e in node.edges:
            e.tag = True
            length = node.length + e.calc_length()
            v = e.other_vert(node.vert)
            
            visit = d[v]
            visiting.append(visit)
            if visit.length > length:
                visit.length = length
                visit.shortest_path = node.shortest_path + [e]
      
        visiting.sort(key=lambda n: n.length)

    return d


def polygon_area(verts:list[mathutils.Vector]) -> float:
    if len(verts) < 3:
        return 0
    bm = bmesh.new()
    for v in verts:
        bm.verts.new(v)
    result = bm.faces.new(bm.verts).calc_area()
    bm.free()
    return result


def collinear_three_points(a:mathutils.Vector, b:mathutils.Vector, c:mathutils.Vector, treshold:float=SMALL_NUMBER) -> bool:
    return (b - a).cross(c - a).length < treshold
    # return ((c - a) - (b - a) - (c - b)).length < treshold


clamp = lambda x, l, u: l if x < l else u if x > u else x


def planes_parallel(p1_normal:mathutils.Vector, p2_normal:mathutils.Vector, treshold:float=SMALL_NUMBER) -> bool:
    return abs(p1_normal.normalized().dot(p2_normal.normalized())) > (1.0 - treshold)


def line_plane_parallel(a:mathutils.Vector, b:mathutils.Vector, normal:mathutils.Vector, treshold:float=SMALL_NUMBER) -> bool:
    return (b - a).normalized().cross(normal.normalized()).length > (1.0 - treshold)


def three_plane_intersection(p1:Plane, p2:Plane, p3:Plane, epsilon:float=SMALL_NUMBER) -> mathutils.Vector:
    m1 = mathutils.Vector((p1.normal.x, p2.normal.x, p3.normal.x))
    m2 = mathutils.Vector((p1.normal.y, p2.normal.y, p3.normal.y))
    m3 = mathutils.Vector((p1.normal.z, p2.normal.z, p3.normal.z))
    d = mathutils.Vector((point_to_plane_dist_signed(mathutils.Vector(), p1.center, p1.normal),
                          point_to_plane_dist_signed(mathutils.Vector(), p2.center, p2.normal),
                          point_to_plane_dist_signed(mathutils.Vector(), p3.center, p3.normal)))

    u = m2.cross(m3)
    v = m1.cross(d)
    denom = m1.dot(u)

    if abs(denom) < epsilon:
        raise Exception('Invalid point plane intersection evaluation attempt (perhaps invalid selection?)')

    return mathutils.Vector((d.dot(u) / denom, m3.dot(v) / denom, -m2.dot(v) / denom))


def vectors_equal(a:mathutils.Vector, b:mathutils.Vector, epsilon:float=KINDA_SMALL_NUMBER) -> bool:
    return a.dot(b) >= (1.0 - epsilon)


def vectors_equal_abs(a:mathutils.Vector, b:mathutils.Vector, epsilon:float=KINDA_SMALL_NUMBER) -> bool:
    return abs(a.dot(b)) >= (1.0 - epsilon)