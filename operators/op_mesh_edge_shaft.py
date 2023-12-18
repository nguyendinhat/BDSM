import bpy, bmesh
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty

from mathutils import Matrix, Vector
from math import radians

from ..utils.tools import is_selected_enough, flip_edit_mode, distance_point_line, is_axial, error_handlers

ENABLE_DEBUG = False

class BDSM_Mesh_Edge_Shaft(Operator):
    bl_idname = 'mesh.bdsm_mesh_edge_shaft'
    bl_label = 'BDSM Mesh Edge Shaft'
    bl_description = 'BDSM Mesh Edge Shaft \nCreate a shaft mesh around an axis'
    bl_options = {'REGISTER', 'UNDO'}

    # Selection defaults:
    shaftType = 0

    # For tracking if the user has changed selection:
    last_edge: IntProperty(
            name='Last Edge',
            description='Tracks if user has changed selected edges',
            min=0, max=1,
            default=0
            )
    last_flip = False

    edge: IntProperty(
            name='Edge',
            description='Edge to shaft around',
            min=0, max=1,
            default=0
            )
    flip: BoolProperty(
            name='Flip Second Edge',
            description='Flip the perceived direction of the second edge',
            default=False
            )
    radius: FloatProperty(
            name='Radius',
            description='Shaft Radius',
            min=0.0, max=1024.0,
            default=1.0
            )
    start: FloatProperty(
            name='Starting Angle',
            description='Angle to start the shaft at',
            min=-360.0, max=360.0,
            default=0.0
            )
    finish: FloatProperty(
            name='Ending Angle',
            description='Angle to end the shaft at',
            min=-360.0, max=360.0,
            default=360.0
            )
    segments: IntProperty(
            name='Shaft Segments',
            description='Number of segments to use in the shaft',
            min=1, max=4096,
            soft_max=512,
            default=32
            )

    def draw(self, context):
        layout = self.layout

        if self.shaftType == 0:
            layout.prop(self, 'edge')
            layout.prop(self, 'flip')
        elif self.shaftType == 3:
            layout.prop(self, 'radius')

        layout.prop(self, 'segments')
        layout.prop(self, 'start')
        layout.prop(self, 'finish')

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        # Make sure these get reset each time we run:
        self.last_edge = 0
        self.edge = 0

        return self.execute(context)

    def execute(self, context):
        try:
            me = context.object.data
            bm = bmesh.from_edit_mesh(me)
            bm.normal_update()

            bFaces = bm.faces
            bEdges = bm.edges
            bVerts = bm.verts

            active = None
            edges, verts = [], []

            # Pre-caclulated values:
            rotRange = [radians(self.start), radians(self.finish)]
            rads = radians((self.finish - self.start) / self.segments)

            numV = self.segments + 1
            numE = self.segments

            edges = [e for e in bEdges if e.select]

            # Robustness check: there should at least be one edge selected
            if not is_selected_enough(self, edges, 0, edges_n=1, verts_n=0, types='Edge'):
                return {'CANCELLED'}

            # If two edges are selected:
            if len(edges) == 2:
                # default:
                edge = [0, 1]
                vert = [0, 1]

                # By default, we want to shaft around the last selected edge (it
                # will be the active edge). We know we are using the default if
                # the user has not changed which edge is being shafted around (as
                # is tracked by self.last_edge). When they are not the same, then
                # the user has changed selection.
                # We then need to make sure that the active object really is an edge
                # (robustness check)
                # Finally, if the active edge is not the initial one, we flip them
                # and have the GUI reflect that
                if self.last_edge == self.edge:
                    if isinstance(bm.select_history.active, bmesh.types.BMEdge):
                        if bm.select_history.active != edges[edge[0]]:
                            self.last_edge, self.edge = edge[1], edge[1]
                            edge = [edge[1], edge[0]]
                    else:
                        flip_edit_mode()
                        self.report({'WARNING'},
                                    'Active geometry is not an edge. Operation Cancelled')
                        return {'CANCELLED'}
                elif self.edge == 1:
                    edge = [1, 0]

                verts.append(edges[edge[0]].verts[0])
                verts.append(edges[edge[0]].verts[1])

                if self.flip:
                    verts = [1, 0]

                verts.append(edges[edge[1]].verts[vert[0]])
                verts.append(edges[edge[1]].verts[vert[1]])

                self.shaftType = 0
            # If there is more than one edge selected:
            # There are some issues with it ATM, so don't expose is it to normal users
            # @todo Fix edge connection ordering issue
            elif ENABLE_DEBUG and len(edges) > 2:
                if isinstance(bm.select_history.active, bmesh.types.BMEdge):
                    active = bm.select_history.active
                    edges.remove(active)
                    # Get all the verts:
                    # edges = order_joined_edges(edges[0])
                    verts = []
                    for e in edges:
                        if verts.count(e.verts[0]) == 0:
                            verts.append(e.verts[0])
                        if verts.count(e.verts[1]) == 0:
                            verts.append(e.verts[1])
                else:
                    flip_edit_mode()
                    self.report({'WARNING'},
                                'Active geometry is not an edge. Operation Cancelled')
                    return {'CANCELLED'}
                self.shaftType = 1
            else:
                verts.append(edges[0].verts[0])
                verts.append(edges[0].verts[1])

                for v in bVerts:
                    if v.select and verts.count(v) == 0:
                        verts.append(v)
                    v.select = False
                if len(verts) == 2:
                    self.shaftType = 3
                else:
                    self.shaftType = 2

            # The vector denoting the axis of rotation:
            if self.shaftType == 1:
                axis = active.verts[1].co - active.verts[0].co
            else:
                axis = verts[1].co - verts[0].co

            # We will need a series of rotation matrices. We could use one which
            # would be faster but also might cause propagation of error
            # matrices = []
            # for i in range(numV):
            #    matrices.append(Matrix.Rotation((rads * i) + rotRange[0], 3, axis))
            matrices = [Matrix.Rotation((rads * i) + rotRange[0], 3, axis) for i in range(numV)]

            # New vertice coordinates:
            verts_out = []

            # If two edges were selected:
            #  - If the lines are not parallel, then it will create a cone-like shaft
            if self.shaftType == 0:
                for i in range(len(verts) - 2):
                    init_vec = distance_point_line(verts[i + 2].co, verts[0].co, verts[1].co)
                    co = init_vec + verts[i + 2].co
                    # These will be rotated about the origin so will need to be shifted:
                    for j in range(numV):
                        verts_out.append(co - (matrices[j] @ init_vec))
            elif self.shaftType == 1:
                for i in verts:
                    init_vec = distance_point_line(i.co, active.verts[0].co, active.verts[1].co)
                    co = init_vec + i.co
                    # These will be rotated about the origin so will need to be shifted:
                    for j in range(numV):
                        verts_out.append(co - (matrices[j] @ init_vec))
            # Else if a line and a point was selected:
            elif self.shaftType == 2:
                init_vec = distance_point_line(verts[2].co, verts[0].co, verts[1].co)
                # These will be rotated about the origin so will need to be shifted:
                verts_out = [
                    (verts[i].co - (matrices[j] @ init_vec)) for i in range(2) for j in range(numV)
                    ]
            else:
                # Else the above are not possible, so we will just use the edge:
                #  - The vector defined by the edge is the normal of the plane for the shaft
                #  - The shaft will have radius 'radius'
                if is_axial(verts[0].co, verts[1].co) is None:
                    proj = (verts[1].co - verts[0].co)
                    proj[2] = 0
                    norm = proj.cross(verts[1].co - verts[0].co)
                    vec = norm.cross(verts[1].co - verts[0].co)
                    vec.length = self.radius
                elif is_axial(verts[0].co, verts[1].co) == 'Z':
                    vec = verts[0].co + Vector((0, 0, self.radius))
                else:
                    vec = verts[0].co + Vector((0, self.radius, 0))
                init_vec = distance_point_line(vec, verts[0].co, verts[1].co)
                # These will be rotated about the origin so will need to be shifted:
                verts_out = [
                    (verts[i].co - (matrices[j] @ init_vec)) for i in range(2) for j in range(numV)
                    ]

            # We should have the coordinates for a bunch of new verts
            # Now add the verts and build the edges and then the faces

            newVerts = []

            if self.shaftType == 1:
                # Vertices:
                for i in range(numV * len(verts)):
                    new = bVerts.new()
                    new.co = verts_out[i]
                    bVerts.ensure_lookup_table()
                    new.select = True
                    newVerts.append(new)
                # Edges:
                for i in range(numE):
                    for j in range(len(verts)):
                        e = bEdges.new((newVerts[i + (numV * j)], newVerts[i + (numV * j) + 1]))
                        bEdges.ensure_lookup_table()
                        e.select = True
                for i in range(numV):
                    for j in range(len(verts) - 1):
                        e = bEdges.new((newVerts[i + (numV * j)], newVerts[i + (numV * (j + 1))]))
                        bEdges.ensure_lookup_table()
                        e.select = True

                # Faces: There is a problem with this right now
                '''
                for i in range(len(edges)):
                    for j in range(numE):
                        f = bFaces.new((newVerts[i], newVerts[i + 1],
                                       newVerts[i + (numV * j) + 1], newVerts[i + (numV * j)]))
                        f.normal_update()
                '''
            else:
                # Vertices:
                for i in range(numV * 2):
                    new = bVerts.new()
                    new.co = verts_out[i]
                    new.select = True
                    bVerts.ensure_lookup_table()
                    newVerts.append(new)
                # Edges:
                for i in range(numE):
                    e = bEdges.new((newVerts[i], newVerts[i + 1]))
                    e.select = True
                    bEdges.ensure_lookup_table()
                    e = bEdges.new((newVerts[i + numV], newVerts[i + numV + 1]))
                    e.select = True
                    bEdges.ensure_lookup_table()
                for i in range(numV):
                    e = bEdges.new((newVerts[i], newVerts[i + numV]))
                    e.select = True
                    bEdges.ensure_lookup_table()
                # Faces:
                for i in range(numE):
                    f = bFaces.new((newVerts[i], newVerts[i + 1],
                                    newVerts[i + numV + 1], newVerts[i + numV]))
                    bFaces.ensure_lookup_table()
                    f.normal_update()

            bmesh.update_edit_mesh(me)

        except Exception as e:
            error_handlers(self, 'mesh.edgetools_shaft', e,
                           reports='Shaft Operator failed', func=False)
            return {'CANCELLED'}

        return {'FINISHED'}

