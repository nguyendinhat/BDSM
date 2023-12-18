import bpy,bmesh
from bpy.types import Operator
from ..utils.ngons import *


class BDSM_Mesh_Edge_Subdivide_Loops(Operator):
    bl_idname = 'mesh.bdsm_mesh_edge_subdivide_loops'
    bl_label = 'BDSM Mesh Edge Subdivide Loops'
    bl_description = 'BDSM Mesh Edge Subdivide Loops \nSmart subdivision to create a highly detailed version of the selected the loops'
    bl_options = {'REGISTER', 'UNDO'}

    curve_type: bpy.props.EnumProperty(
        name='Curve type',
        description='The curve type to use for evaluating vertex positions',
        items=[
            ('BEZIER', 'Bezier', 'The bezier curve type. May be useful when the nurbs curve does not give expected results'),
            ('NURBS', 'Nurbs', 'The nurbs curve type. Often gives better results than Bezier. This option doesn\'t support projection modes')
        ],
        default='BEZIER'
    )

    closed_curve: bpy.props.BoolProperty(
        name='Close curve',
        description='Whether or not bezier interpolation should treat the loop as closed or not: this DOES NOT affect unselected edges but only affects the positions of the new vertices',
        default=False
    )

    cuts: bpy.props.IntProperty(
        name='Number of cuts',
        description='How many times to cut each edge for resampling',
        default=1,
        min=1
    )

    project_mode: bpy.props.EnumProperty(
        name='Projection mode',
        description='Projection mode for use when projecting on face planes',
        items=[
            ('none', 'None', 'Do not to project the resulting vertices location on the plane of faces they modify. Often checked if used with singular holes'),
            ('auto/nearby normal', 'Auto/nearby normal', 'If all edges from connected vertex are cross-edges of loops, don\'t project, otherwise use nearby normal projection'),
            ('auto/selection normal', 'Auto/selection normal', 'If all edges from connected vertex are cross-edges of loops, don\'t project, otherwise use selection normal projection'),
            ('auto/distance', 'Auto/distance', 'If all edges from connected vertex are cross-edges of loops, don\'t project, otherwise use distance projection'),
            ('nearby normal', 'Nearby normal', 'Project on faces that have closest normal to normal of the plane including the nearest verts'),
            ('selection normal', 'Selection normal', 'Project on faces that have closest normal to selection normal. This is not ideal for holes in extremely curved surfaces'),
            ('distance', 'Distance', 'Project on faces that are closer to the goal location. This is not ideal for surfaces with irregular bend (AR15 rail example)')
        ],
        default='auto/nearby normal'
    )

    connect_mode: bpy.props.EnumProperty(
        name='Connecting mode',
        description='Connecting mode for use when connecting new geometry',
        items=[
            ('none', 'None', ' Do not connect new vertices'),
            ('fast', 'Fast', 'Fast method can often introduce a triangle in place of a perfectly fitting quad'),
            ('precise', 'Precise', 'REQUIRES LOOPS SELECTION - NO FULL FACES ALLOWED! Much slower than fast but more likely to produce better results in terms of subdivision into quads - quads not guaranteed'),
            ('quads', 'Quads', 'Slower than precise but the best in terms of creating quads. Much better results if faces resemble quads (4 distinctive corners) but should work with any geometry. This will often create additional topology')
        ],
        default='fast'
    )

    coverage_mode: bpy.props.EnumProperty(
        name='Connect coverage mode',
        description='What to fix',
        items=[
            ('selection', 'Only faces within selection', 'If all verts of a face are selected, they will be turned into quads (no need for all of the edges of the faces to be selected)'),
            ('relevant', 'Also faces around selection', 'Selection and the faces around it will all be turned into quads (a single selected vert is enough to quad a face)'),
            ('all', 'All', 'Everything will be turned into quads (hopefully)')
        ],
        default='relevant'
    )

    max_verts: bpy.props.IntProperty(
        name='Max ngon verts',
        description='[Quad mode only] The max number of verts to consider an ngon for when turning into quads (inclusive)',
        default=10,
        min=5
    )

    max_recursion_depth: bpy.props.IntProperty(
        name='Max recursion depth',
        description='[Quad mode only] The max recursion depth per ngon - usually 100 should be more than enough',
        default=100,
        min=1,
        max=900
    )


    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'curve_type')
        layout.prop(self, 'closed_curve')
        layout.prop(self, 'cuts')

        if self.curve_type != 'NURBS':
            layout.prop(self, 'project_mode')

        layout.prop(self, 'connect_mode')
        layout.prop(self, 'coverage_mode')
        layout.prop(self, 'max_verts')
        layout.prop(self, 'max_recursion_depth')

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        obj = context.active_object
        return (obj and obj.type == 'MESH' and
                obj.mode == 'EDIT')
    def execute(self, context):
        obj = bpy.context.object

        # bisect edges
        bm = get_bmesh(obj, True, True, True)
        selected_edges = [e for e in bm.edges if e.select]
        selected_verts_indices = set(v.index for v in bm.verts if v.select)

        all_loop_indices = list()
        all_resulting_vertices = list()
        loops = get_separated_sorted_loops(selected_edges)
        
        # try:
        # except:
        #     show_message('Invalid selection. Remember to only select loops, not full faces!')
        #     free_bmesh(obj, bm)
        #     return {'CANCELLED'}

        for original_indices in loops:
            edges = [e for e in selected_edges if e.verts[0].index in original_indices and e.verts[1].index in original_indices]
            if len(edges) < 2:
                bmesh.ops.bisect_edges(bm, edges=edges, cuts=self.cuts)
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()
                continue

            selection_normal = get_selection_normal([bm.verts[i].co for i in original_indices], [bm.verts[i].normal for i in original_indices])
            curve_vertpos = [bm.verts[i].co.copy() for i in original_indices]

            bisect_result = bmesh.ops.bisect_edges(bm, edges=edges, cuts=self.cuts)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            resulting_edges = [e for e in bisect_result['geom_split'] if type(e) == bmesh.types.BMEdge]
            all_resulting_vertices += [v.index for v in bisect_result['geom_split'] if type(v) == bmesh.types.BMVert]

            # create reference curve for evaluated positions
            cyclic = self.closed_curve or len(resulting_edges) == len(set(flattened([e.verts for e in resulting_edges])))
            curve_vertpos_full = self.extract_curve_geo(curve_vertpos, self.cuts, cyclic, self.curve_type)

            # re-evaluate original indices cos they might have changed during bisection
            original_indices = list()
            all_indices_temp = self.sort_vertices(resulting_edges, None, None)
            for pos in curve_vertpos:
                orig = min(all_indices_temp, key=lambda i: (bm.verts[i].co - pos).length)
                original_indices.append(all_indices_temp.pop(all_indices_temp.index(orig)))

            # calculate the starting point and the points next to it
            closest_to_0 = min(original_indices, key=lambda i: (bm.verts[i].co - curve_vertpos_full[0]).length)
            neighbours = [other_edge_vertex(bm.verts[closest_to_0], e).index for e in bm.verts[closest_to_0].link_edges if e in resulting_edges]

            # sort the vertices so that the curve vertices correspond correctly
            if len(neighbours) > 1:
                all_indices = self.sort_vertices(resulting_edges, closest_to_0, neighbours[0])
                all_indices_alternative = [all_indices[0]] + all_indices[1:][::-1]# self.sort_vertices(resulting_edges, closest_to_0, neighbours[1])

                if sum([(bm.verts[all_indices[i]].co - curve_vertpos_full[i]).length for i in range(len(all_indices))]) > sum([(bm.verts[all_indices_alternative[i]].co - curve_vertpos_full[i]).length for i in range(len(all_indices_alternative))]):
                    all_indices = all_indices_alternative
            else:
                all_indices = self.sort_vertices(resulting_edges, closest_to_0, neighbours[0])
            all_loop_indices.append(all_indices)

            # print(closest_to_0)
            # print(all_indices)
            # print(original_indices)

            # offset the vertices to their final locations
            if self.project_mode != 'none' and self.curve_type != 'NURBS':
                possible_faces = get_relevant_faces(bm, all_indices)
                for i, pos in zip(all_indices, curve_vertpos_full):
                    if self.curve_type == 'BEZIER' and i in original_indices:
                        continue

                    candidates = [f for f in possible_faces if i in [v.index for v in f.verts]]

                    # if no faces around: just use the position sampled from curve
                    if len(candidates) == 0:
                        bm.verts[i].co = pos
                        continue

                    if 'nearby normal' in self.project_mode:
                        face = min(candidates, key=lambda f: (nearby_plane_normal(bm.verts[i], [bm.verts[x] for x in all_indices], cyclic) - f.normal).length)
                    if 'selection normal' in self.project_mode:
                        face = min(candidates, key=lambda f: (selection_normal - f.normal).length)
                    elif 'distance' in self.project_mode:
                        face = min(candidates, key=lambda f: point_to_plane_dist(pos, f.calc_center_median(), f.normal))

                    if 'auto' in self.project_mode:
                        link_faces_verts = [v for v in set(flattened([f.verts for f in bm.verts[i].link_faces])) if v.index not in all_resulting_vertices]

                        if all([v.index in selected_verts_indices for v in link_faces_verts]):
                            bm.verts[i].co = pos
                        else:
                            bm.verts[i].co = project_point_on_plane(pos, face.calc_center_median(), face.normal)
                    else:
                        bm.verts[i].co = project_point_on_plane(pos, face.calc_center_median(), face.normal)
            else:
                for i, pos in zip(all_indices, curve_vertpos_full):
                    bm.verts[i].co = pos

            # select all edges so that user can i.e. bevel
            for e in resulting_edges:
                e.select = True
                selected_verts_indices.add(e.verts[0].index)
                selected_verts_indices.add(e.verts[1].index)

        if self.connect_mode != 'none':
            if self.coverage_mode == 'selection':
                relevant_faces = [f for f in get_relevant_faces(bm, selected_verts_indices) if all([v.index in selected_verts_indices for v in f.verts])]
            elif self.coverage_mode == 'relevant':
                relevant_faces = get_relevant_faces(bm, selected_verts_indices)
            elif self.coverage_mode == 'all':
                relevant_faces = [f for f in bm.faces]
            relevant_faces = [f for f in relevant_faces if len(f.verts) <= max(5, self.max_verts)]

            if self.connect_mode == 'fast':
                bmesh.ops.connect_verts_concave(bm, faces=relevant_faces)
            elif self.connect_mode == 'quads':
                FixNgonsRecursively(bm, relevant_faces, self.max_recursion_depth)
            elif self.connect_mode == 'precise':
                grouped_loops = group_loops(all_loop_indices, relevant_faces)
                possible = possible_edges(grouped_loops, relevant_faces)
                v_edges = viable_edges(bm, possible)

                for x in v_edges:
                    for e in x:
                        bmesh.ops.connect_verts(bm, verts=(bm.verts[e[0]], bm.verts[e[1]]), check_degenerate=True)

        update_bmesh(obj, bm)
        free_bmesh(obj, bm)

        return {'FINISHED'}


    @staticmethod
    def sort_vertices(edges:list[bmesh.types.BMEdge], known_tip:int=None, known_next:int=None) -> list[int]:
        edge_connections = get_edge_connections_index(edges)

        # ensure that the selection is correct and select the tip as the starting point if available
        current = None
        for i, con in edge_connections.items():
            l = len(con)
            if l == 0:
                raise(BaseException('Singular vertices selected!'))
            elif l == 1:
                current = i
            elif l > 2:
                raise(BaseException('More than 2 edges branch out from a vertex!'))

        if known_tip is not None:
            current = known_tip
        else:
            for v in edge_connections.keys():
                break
            current = v if current is None else current

        # add in the rest of vertices traversing the edges
        sorted_indices = [current]
        if known_next is not None:
            edge_connections.pop(current, None)
            current = known_next
            sorted_indices.append(current)
        for _ in range(len(edge_connections.keys()) - 1):
            current = other_edge_vertex_index(edge_connections.pop(current, None), sorted_indices)
            sorted_indices.append(current)

        return sorted_indices

    @staticmethod
    def extract_curve_geo(curve_vertpos:list[mathutils.Vector], cuts:int, cyclic:bool, curve_type:str) -> list[mathutils.Vector]:
        # make a new curve
        crv = bpy.data.curves.new('crv', 'CURVE')
        crv.dimensions = '3D'


        # make a new spline in that curve
        spline = crv.splines.new(type=curve_type)

        # create a spline point for each point
        if curve_type == 'NURBS':
            # theres already one point by default
            spline.points.add(len(curve_vertpos) - 1)

            # adjust point positions
            for i in range(len(curve_vertpos)):
                spline.points[i].co = curve_vertpos[i].to_4d()

            spline.use_endpoint_u = not cyclic

        elif curve_type == 'BEZIER':
            # theres already one point by default
            spline.bezier_points.add(len(curve_vertpos) - 1)

            # assign the point coordinates to the spline points
            for i in range(len(curve_vertpos)):
                spline.bezier_points[i].co = curve_vertpos[i]
                spline.bezier_points[i].handle_left = spline.bezier_points[i].handle_right = spline.bezier_points[i].co
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'

        else:
            raise Exception('Invalid curve type')

        crv.resolution_u = cuts + 1
        spline.use_cyclic_u = cyclic

        # make a new object with the curve
        obj_curve = bpy.data.objects.new('helper_curve', crv)
        mesh_curve = obj_curve.to_mesh()

        # # DEBUG
        # mesh = bpy.data.meshes.new('mesh_curve')
        # obj_mesh_curve = bpy.data.objects.new('Test curve', mesh)
        # bpy.context.collection.objects.link(obj_curve)
        # bpy.context.collection.objects.link(obj_mesh_curve)
        # bm_curve = get_bmesh(obj_mesh_curve)
        # for v in mesh_curve.vertices:
        #     bm_curve.verts.new(v.co)
        # bm_curve.verts.ensure_lookup_table()
        # for e in mesh_curve.edges:
        #     bm_curve.edges.new((bm_curve.verts[e.vertices[0]], bm_curve.verts[e.vertices[1]]))
        # bm_curve.edges.ensure_lookup_table()
        # update_bmesh(obj_mesh_curve, bm_curve)
        # free_bmesh(obj_mesh_curve, bm_curve)

        return [v.co.copy() for v in mesh_curve.vertices]

    # current and neighbour as in vertex indices (not indices in the list)
    @staticmethod
    def vertex_list_by_current_next(sorted_indices:list[int], current:int, neighbour:int) -> list[int]:
        c = sorted_indices.index(current)
        n = sorted_indices.index(neighbour)
        l = sorted_indices

        if c == 0:
            if n == 1:
                return l # return l[c:] + l[:c]
            else:
                return l[:c + 1][::-1] + l[c + 1:][::-1]
        elif c == len(l) - 1:
            if n == c - 1:
                return l[::-1] # return l[:c + 1][::-1] + l[c + 1:][::-1]
            else:
                return l[c:] + l[:c]
        else:
            if n < c:
                return l[:c + 1][::-1] + l[c + 1:][::-1]
            else:
                return l[c:] + l[:c]
