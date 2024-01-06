import sys

def build_mesh_graph_normal(bm, debug=False):
    mesh_graph = {}
    for v in bm.verts:
        mesh_graph[v.index] = []

    for edge in bm.edges:
        mesh_graph[edge.verts[0].index].append((edge.verts[1].index, edge.verts[1].select, edge.select))
        mesh_graph[edge.verts[1].index].append((edge.verts[0].index, edge.verts[0].select, edge.select))

    if debug:
        for idx in mesh_graph:
            print(idx, mesh_graph[idx])

    return mesh_graph

def build_mesh_graph(verts, edges, topo=True):
    mg = {}
    for v in verts:
        mg[v] = []

    for e in edges:
        distance = 1 if topo else e.calc_length()

        mg[e.verts[0]].append((e.verts[1], distance))
        mg[e.verts[1]].append((e.verts[0], distance))

    return mg


def get_shortest_path(bm, vstart, vend, topo=False, ignore_selected=False, select=False):

    def dijkstra(mg, vstart, vend, topo=True):
        d = dict.fromkeys(mg.keys(), sys.maxsize)

        predecessor = dict.fromkeys(mg.keys())

        d[vstart] = 0

        unknownverts = [(0, vstart)]

        while unknownverts:

            dist, vcurrent = unknownverts[0]

            others = mg[vcurrent]

            if ignore_selected and vcurrent == vstart and vend in [v for v, _ in others]:
                others = [(v, d) for v, d in others if v != vend]

            for vother, distance in others:

                if ignore_selected and vother not in [vstart, vend] and vother.select:
                    continue

                if d[vother] > d[vcurrent] + distance:
                    d[vother] = d[vcurrent] + distance

                    unknownverts.append((d[vother], vother))
                    predecessor[vother] = vcurrent

            unknownverts.pop(0)

            if topo and vcurrent == vend:
                break

        path = []
        endvert = vend

        while endvert is not None:
            path.append(endvert)
            endvert = predecessor[endvert]

        return reversed(path)

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    verts = [v for v in bm.verts]
    edges = [e for e in bm.edges]

    mg = build_mesh_graph(verts, edges, topo)

    path = dijkstra(mg, vstart, vend, topo)

    path = f7(path)

    if select:
        for v in path:
            v.select = True

    return path
