
import math
import mathutils
import numpy as np

from collections import deque

class Loop():
    def __init__(self, bm, edges):
        self.bm = bm
        self.edges = edges

        self.verts = set()
        for e in self.edges:
            for v in e.verts:
                self.verts.add(v)

        # print('edgeloop length: %s' % len(self.edges))
        self.valences = []

        self.ring = {}
        for e in self.edges:
            self.ring[e] = []

        self.edge_rings = {}
        self.ends = {}

    def __str__(self):
        str = '\n'
        for index, edge in enumerate(self.edges):
            str += 'edge: %s -' % (edge.index)
            str += ' valence: %s' % self.valences[index]

            for r in self.get_ring(edge):
                str += ' | %s ' % r.index

            # print(self.edge_ring.values())
            # for k,v in self.edge_ring.items():
            #    print('key: ', k.index)
            #    print('value: ', v)


            # for loop in self.edge_ring[edge]:
            #    str += ' = %s ' % loop.edge.index
            str += '\n'

            ends = self.get_ring_ends(edge)
            for e in ends:
                str += ' end: %s' % e.index

            str += '\n'
        return str

    def __repr__(self):
        return self.__str__()

    def set_ring(self, edge, ring_edge):
        if edge in self.ring and len(self.ring[edge]) <= 2:
            self.ring[edge].append(ring_edge)

    def get_ring(self, edge):
        if edge in self.ring:
            return self.ring[edge]

        raise Exception('edge not in Edgeloop!')

    def select(self):
        for edge in self.edges:
            edge.select = True

    def get_ring_ends(self, edge):
        ring = self.edge_rings[edge]
        return (ring[0], ring[len(ring) - 1])

    def set_curve_flow(self, visited, tension):

        for edge in self.edge_rings:
            a, b = self.ends[edge]

            if a in visited and b in visited:
                continue

            visited.add(a)
            visited.add(b)

            a1 = b.link_loop_radial_prev.link_loop_prev.link_loop_prev.vert
            a2 = b.vert
            a3 = a.link_loop_radial_prev.vert
            a4 = a.link_loop_radial_prev.link_loop_prev.vert

            b1 = b.link_loop_radial_prev.link_loop_prev.vert
            b2 = b.link_loop_next.vert
            b3 = a.link_loop_radial_prev.link_loop_next.vert
            b4 = a.link_loop_radial_prev.link_loop_next.link_loop_next.vert

            #print(a1.index, a2.index, a3.index, a4.index)
            #print(b1.index, b2.index, b3.index, b4.index)

            count = len(self.edge_rings[edge])
            #print('edges: %s' % count)

            for index, loop in enumerate(self.edge_rings[edge]):
                # print(loop.edge.index)
                # print( loop.edge.verts[0].index, loop.edge.verts[1].index )
                value = (index + 1) * (1.0 / (count + 1))
                #print(value)
                result_A = hermite_3d(a1.co, a2.co, a3.co, a4.co, value, -tension, 0)
                result_B = hermite_3d(b1.co, b2.co, b3.co, b4.co, value, -tension, 0)

                loop.edge.verts[0].co = mathutils.Vector(result_A)
                loop.edge.verts[1].co = mathutils.Vector(result_B)

        return visited

    def get_average_distance(self):
        dist = 0
        for e in self.edges:
            dist += (e.verts[0].co - e.verts[1].co).length
        return dist / float(len(self.edges))

    def straighten(self, distance):
        edge = self.edges[0]

        def find_neighbour(p):
            link_edges = set(p.link_edges)
            link_edges.remove(edge)

            #print('face a:', edge.link_faces[0].index, 'face b:', edge.link_faces[1].index)

            faceA_is_quad = len(edge.link_faces[0].verts) == 4

            edges = link_edges
            if faceA_is_quad:
                edges -= set(edge.link_faces[0].edges)

            if not edge.is_boundary:
                faceB_is_quad = len(edge.link_faces[1].verts) == 4
                if faceB_is_quad:
                    edges -= set(edge.link_faces[1].edges)

            v = mathutils.Vector((0, 0, 0))
            count = 0

            for e in edges:
                for vert in e.verts:
                    if vert == p:
                        continue

                    v += vert.co
                    count += 1

            return v / count

        a1 = edge.verts[0]
        a2 = edge.verts[1]

        a1_len = len(a1.link_edges)
        a2_len =  len(a2.link_edges)
        if a1_len <= 3 or a2_len <= 3:
            return

        b1 = find_neighbour(a1)
        b2 = find_neighbour(a2)

        direction = (b2 - b1).normalized()
        max_distance = (b2 - b1).length

        if distance * 2.0 > max_distance:
            distance = max_distance * 0.5

        a1.co = b1 + distance * direction
        a2.co = b2 - distance * direction

    def set_linear(self, even_spacing):

        count = len(self.edges)
        if count < 2:
            return

        #print('even_spacing:', even_spacing)

        for p in self.edges[0].verts:
            if p not in self.edges[1].verts:
                p1 = p

        for p in self.edges[-1].verts:
            if p not in self.edges[-2].verts:
                p2 = p

        direction = (p2.co - p1.co)
        direction = direction / (count)
        direction_normalized = direction.normalized()

        last_vert = p1
        for i in range(count - 1):
            vert = self.edges[i].other_vert(last_vert)
            # print(vert.index, '--', vert.co)

            if even_spacing:
                vert.co = p1.co + direction * (i + 1)
            else:
                proj = vert.co - p1.co
                scalar = proj.dot(direction_normalized)
                vert.co = p1.co + (direction_normalized * scalar)

            last_vert = vert

    def set_flow(self, tension, min_angle):
        visited = set()

        for edge in self.edges:
            target = {}

            if edge.is_boundary:
                continue

            for loop in edge.link_loops:
                if loop in visited:
                    continue

                # todo check triangles/ngons?

                visited.add(loop)
                ring1 = loop.link_loop_next.link_loop_next
                ring2 = loop.link_loop_radial_prev.link_loop_prev.link_loop_prev

                center = edge.other_vert(loop.vert)

                p1 = None
                p2 = ring1.vert
                p3 = ring2.link_loop_radial_next.vert
                p4 = None

                #print('ring1 %s - %s' % (ring1.vert.index, ring1.edge.index))
                #print('ring2 %s - %s' % (ring2.vert.index, ring2.edge.index))
                # print('p2: %s - p3: %s ' % (p2.index, p3.index))

                result = []
                if not ring1.edge.is_boundary:
                    is_quad = len(ring1.face.verts) == 4
                    # if is_quad:
                    final = ring1.link_loop_radial_next.link_loop_next

                    # else:
                    #    final = ring1

                    #print('is_quad:', is_quad, ' - ', final.edge.index)

                    a, b = final.edge.verts
                    if p2 == a:
                        p1 = b.co
                    else:
                        p1 = a.co

                    a = (p1 - p2.co).normalized()
                    b = (center.co - p2.co).normalized()
                    dot = min(1.0, max(-1.0, a.dot(b)))
                    angle = math.acos(dot)

                    if angle < min_angle:
                        # print('r1: %s' % (math.degrees(angle)))
                        p1 = p2.co - (p3.co - p2.co) * 0.5

                        # bmesh.ops.create_vert(self.bm, co=p1)

                else:
                    p1 = p2.co - (p3.co - p2.co)
                    # bmesh.ops.create_vert(self.bm, co=p1)

                result.append(p1)
                result.append(p2.co)

                if not ring2.edge.is_boundary:
                    is_quad = len(ring2.face.verts) == 4
                    # if is_quad:
                    final = ring2.link_loop_radial_prev.link_loop_prev
                    # else:
                    #    final = ring2

                    #print('is_quad:', is_quad, ' - ', final.edge.index)

                    a, b = final.edge.verts

                    if p3 == a:
                        p4 = b.co
                    else:
                        p4 = a.co

                    a = (p4 - p3.co).normalized()
                    b = (center.co - p3.co).normalized()
                    dot = min(1.0, max(-1.0, a.dot(b)))
                    angle = math.acos(dot)

                    if angle < min_angle:
                        # print('r2: %s' % (math.degrees(angle)))
                        p4 = p3.co - (p2.co - p3.co) * 0.5

                        # bmesh.ops.create_vert(self.bm, co=p4)

                else:
                    # radial_next doenst work at boundary
                    p3 = ring2.edge.other_vert(p3)
                    p4 = p3.co - (p2.co - p3.co)
                    # bmesh.ops.create_vert(self.bm, co=p4)

                result.append(p3.co)
                result.append(p4)

                target[center] = result

            for vert, points in target.items():
                p1, p2, p3, p4 = points

                if p1 == p2 or p3 == p4:
                    print('invalid input - two control points are identical!')
                    continue

                # normalize point distances so that long edges dont skew the curve
                d = (p2 - p3).length * 0.5

                p1 = p2 + (d * (p1 - p2).normalized())
                p4 = p3 + (d * (p4 - p3).normalized())

                # print('p1: %s\np2:%s\np3: %s\np4:%s\n1' % (p1, p2, p3, p4))
                # result = mathutils.geometry.interpolate_bezier(p1, p2, p3, p4, 3)[1]

                # result = interpolate.catmullrom(p1, p2, p3, p4, 1, 3)[1]
                result = hermite_3d(p1, p2, p3, p4, 0.5, -tension, 0)
                result = mathutils.Vector(result)
                linear = (p2 + p3) * 0.5

                vert.co = result
                # vert.co = linear.lerp(curved, tension)


def walk_boundary(start_edge, limit_to_edges=None):
    edge_loop = set([start_edge])
    visited = set()

    candidates = [start_edge]
    while True:
        for candidate in candidates:
            for vert in candidate.verts:
                if len(vert.link_edges) > 2:  # valence of verts as a blocker
                    for edge in vert.link_edges:
                        if edge.is_boundary and edge not in edge_loop:
                            if limit_to_edges != None:
                                if edge in limit_to_edges:
                                    edge_loop.add(edge)
                            else:
                                edge_loop.add(edge)

            visited.add(candidate)

        candidates = edge_loop - visited
        if len(visited) == len(edge_loop):
            break

    #sorting this mess..
    raw_edge_loop = list(edge_loop)

    start_edge = raw_edge_loop[0]
    raw_edge_loop.remove(start_edge)

    sorted_edge_loop = deque()
    sorted_edge_loop.append(start_edge)
    add = sorted_edge_loop .append

    for p in start_edge.verts:
        while True:

            edge = None
            for e in raw_edge_loop:
                if p in e.verts:
                    edge = e

            if edge != None:
                add(edge)
                p = edge.other_vert(p)
                raw_edge_loop.remove(edge)
            else:
                break

        add = sorted_edge_loop .appendleft

    #for e in list(sorted_edge_loop ):
    #    print('###', e.index)

    if len(sorted_edge_loop ) != len(edge_loop):
        raise  Exception('WTF')

    return list(sorted_edge_loop)


def walk_ngon(start_edge, limit_to_edges=None):
    edge_loop = deque()
    edge_loop.append(start_edge)

    start_loops = []
    face_valence = []
    for linked_loop in start_edge.link_loops:
        vert_count = len(linked_loop.face.verts)
        if vert_count > 4:
            start_loops.append(linked_loop)
            face_valence.append(vert_count)

    max_value = max(face_valence)
    start_loop = start_loops[face_valence.index(max_value)]

    # print(start_loop.vert.index, start_loop.edge.index)

    loop = start_loop.link_loop_next
    while len(loop.vert.link_edges) < 4 and loop.edge not in edge_loop:
        if limit_to_edges != None and loop.edge not in limit_to_edges:
            break

        edge_loop.append(loop.edge)
        # print('next', loop.edge.index)
        loop = loop.link_loop_next

    # print('switch')
    loop = start_loop.link_loop_prev
    while len(loop.edge.other_vert(loop.vert).link_edges) < 4 and loop.edge not in edge_loop:
        if limit_to_edges != None and loop.edge not in limit_to_edges:
            break

        edge_loop.appendleft(loop.edge)
        loop = loop.link_loop_prev
        # print('prev', loop.edge.index)

    return list(edge_loop)


def walk_edge_loop(start_edge, limit_to_edges=None):
    edge_loop = deque()
    edge_loop.append(start_edge)
    add = edge_loop.append

    for loop in start_edge.link_loops:
        start_valence = len(loop.vert.link_edges)
        # print('start_valence', start_valence)

        if start_valence <= 4:
            while True:
                valence = len(loop.vert.link_edges)
                # print('valence: %s | vert: %s edge: %s' % (valence, loop.vert.index, loop.edge.index))

                if valence == 4 and start_valence == valence:
                    loop = loop.link_loop_prev.link_loop_radial_prev.link_loop_prev

                    if limit_to_edges != None:
                        if loop.edge in limit_to_edges:
                            add(loop.edge)
                        else:
                            break
                    else:
                        add(loop.edge)

                        # print('add edge:', loop.edge.index)
                else:
                    # print('break valence', valence, loop.face != face)
                    break
        else:
            pass
            # print('ignore this direction')
        add = edge_loop.appendleft

    return list(edge_loop)


def get_edgeloop(bm, start_edge, limit_to_edges=None):
    start_loops = start_edge.link_loops

    is_ngon = False
    for loop in start_loops:
        if len(loop.face.verts) > 4:
            is_ngon = True
            break

    quad_flow = len(start_edge.verts[0].link_edges) == 4 and len(start_edge.verts[1].link_edges) == 4
    loop_end = (len(start_edge.verts[0].link_edges) > 4 and len(start_edge.verts[1].link_edges) == 4 or
                len(start_edge.verts[0].link_edges) == 4 and len(start_edge.verts[1].link_edges) > 4)

    # print( 'is quad flow', quad_flow)
    # print('is loop end', loop_end)

    if is_ngon and not quad_flow and not loop_end:
        return Loop(bm, walk_ngon(start_edge, limit_to_edges))

    elif start_edge.is_boundary:
        return Loop(bm, walk_boundary(start_edge, limit_to_edges))
    else:
        return Loop(bm, walk_edge_loop(start_edge, limit_to_edges))


def get_edgeloops(bm, edges):
    '''
    edge_loop = get_edgeloop(edges[0])

    for e in edge_loop:
        e.select = True

    return
    '''

    not_visited = set(edges)

    edge_loops = []
    while (len(not_visited) > 0):
        next = not_visited.pop()

        edge_loop = get_edgeloop(bm, next, not_visited)
        edge_loops.append(edge_loop)

        for edge in edge_loop.edges:
            if edge in not_visited:
                not_visited.remove(edge)

    # print('edge_loops:', len(edge_loops))

    edge_loops = compute_edgeloop_data(edge_loops)
    return edge_loops


def find_edge_ring_neighbours(edgeloops, edge_to_Edgeloop):
    # find neighbouring edge rings
    for edgeloop in edgeloops:
        for edge in edgeloop.edges:

            if len(edgeloop.get_ring(edge)) == 2:
                continue

            for link_loop in edge.link_loops:
                if len(link_loop.face.verts) != 4:
                    continue

                next = link_loop.link_loop_next.link_loop_next.edge

                if next not in edgeloop.get_ring(edge):
                    if next in edge_to_Edgeloop.keys():
                        edgeloop.set_ring(edge, next)
                        edge_to_Edgeloop[next].set_ring(next, edge)


def find_control_edgeloop(edgeloops, edge_to_Edgeloop):
    for edgeloop in edgeloops:
        for edge in edgeloop.edges:
            if edge in edgeloop.edge_rings:
                continue

            #print('start edge: ', edge.index)

            edge_ring = deque()
            edge_ring.append(edge.link_loops[0])
            ends = []
            append_func = edge_ring.append

            for index, loop in enumerate(edge.link_loops):
                next = loop
                prev = None
                visited = set()
                while True:

                    ring = next.link_loop_prev.link_loop_prev
                    #print(ring.edge.index)
                    if ring in visited:
                        break
                    visited.add(ring)

                    if ring.edge not in edge_to_Edgeloop:
                        ends.append(ring)
                        break

                    # print( ring.edge.index )
                    append_func(ring)
                    prev = next
                    next = ring.link_loop_radial_prev

                    if ring.edge.is_boundary:
                        ends.append(ring)
                        break

                #edges have max 2 loops so this I can just switch like this
                if index == 0:
                    append_func = edge_ring.appendleft


            #print('edge_ring:')
            #for l in edge_ring:
            #    print(l.edge.index)
            for ring in edge_ring:
                edge_to_Edgeloop[ring.edge].edge_rings[ring.edge] = edge_ring
                edge_to_Edgeloop[ring.edge].ends[ring.edge] = ends
            #edgeloop.edge_rings[ring] = edge_ring


def compute_edge_ring_valences(edgeloops, edge_to_Edgeloop):
    for edgeloop in edgeloops:
        max_valence = -1
        for edge in edgeloop.edges:
            valence = 0
            visited = set()
            search = set()
            search.add(edge)
            while len(search) > 0:
                current = search.pop()
                visited.add(current)

                loop = edge_to_Edgeloop[current]
                ring_edges = loop.get_ring(current)

                add_to_valence = True
                for ring in ring_edges:
                    if ring not in visited:
                        search.add(ring)
                        if add_to_valence:
                            valence += 1
                            add_to_valence = False

            edgeloop.valences.append(valence)
            max_valence = max(max_valence, valence)
        edgeloop.max_valence = max_valence


def compute_edgeloop_data(edgeloops):
    edge_to_Edgeloop = {}

    for edgeloop in edgeloops:
        for edge in edgeloop.edges:
            edge_to_Edgeloop[edge] = edgeloop

    find_edge_ring_neighbours(edgeloops, edge_to_Edgeloop)
    compute_edge_ring_valences(edgeloops, edge_to_Edgeloop)

    find_control_edgeloop(edgeloops, edge_to_Edgeloop)

    result = sorted(edgeloops, key=lambda edgeloop: edgeloop.max_valence)
    result = list(reversed(result))

    #for el in edgeloops:
    #    print(el)

    return result



def catmullrom(P0, P1, P2, P3, a, nPoints=100):
    '''
    P0, P1, P2, and P3 should be (x,y,z) point pairs that define the Catmull-Rom spline.
    nPoints is the number of points to include in this curve segment.
    '''
    # Convert the points to numpy so that we can do array multiplication
    P0, P1, P2, P3 = map(np.array, [P0, P1, P2, P3])

    # Calculate t0 to t4
    alpha = a

    def tj(ti, Pi, Pj):
        xi, yi, zi = Pi
        xj, yj, zj = Pj

        # ( ( (xj-xi)**2 + (yj-yi)**2 )**0.5 )**alpha + ti
        a = (xj - xi) ** 2 + (yj - yi) ** 2 + (zj - zi) ** 2
        b = a ** 0.5
        c = b ** alpha
        return c + ti

    t0 = 0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    # Only calculate points between P1 and P2
    t = np.linspace(t1, t2, nPoints)

    # Reshape so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    t = t.reshape(len(t), 1)

    A1 = (t1 - t) / (t1 - t0) * P0 + (t - t0) / (t1 - t0) * P1
    A2 = (t2 - t) / (t2 - t1) * P1 + (t - t1) / (t2 - t1) * P2
    A3 = (t3 - t) / (t3 - t2) * P2 + (t - t2) / (t3 - t2) * P3

    B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
    B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3

    C = (t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2
    return C


def hermite_1d(y0, y1, y2, y3, mu, tension, bias):
    mu2 = mu * mu
    mu3 = mu2 * mu

    m0 = (y1 - y0) * (1 + bias) * (1 - tension) / 2
    m0 += (y2 - y1) * (1 - bias) * (1 - tension) / 2
    m1 = (y2 - y1) * (1 + bias) * (1 - tension) / 2
    m1 += (y3 - y2) * (1 - bias) * (1 - tension) / 2
    a0 = 2 * mu3 - 3 * mu2 + 1
    a1 = mu3 - 2 * mu2 + mu
    a2 = mu3 - mu2
    a3 = -2 * mu3 + 3 * mu2

    return a0 * y1 + a1 * m0 + a2 * m1 + a3 * y2


def hermite_3d(p1, p2, p3, p4, mu, tension, bias):
    '''
    Mu: For interpolated values between p2 and p3 mu ranges between 0 and 1
    Tension: 1 is high, 0 normal, -1 is low
    Bias: 0 is even,
         positive is towards first segment,
         negative towards the other
    :return: List
    '''
    x = hermite_1d(p1[0], p2[0], p3[0], p4[0], mu, tension, bias)
    y = hermite_1d(p1[1], p2[1], p3[1], p4[1], mu, tension, bias)
    z = hermite_1d(p1[2], p2[2], p3[2], p4[2], mu, tension, bias)

    return [x, y, z]
