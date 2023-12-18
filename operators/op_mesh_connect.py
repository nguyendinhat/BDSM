import bpy, bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty
from .. utils import tools

class BDSM_Mesh_Connect(Operator):
    bl_idname = 'mesh.bdsm_mesh_connect'
    bl_label = 'BDSM Mesh Connect'
    bl_description = 'BDSM Mesh Connect'
    bl_options = {'REGISTER', 'UNDO'}

    square: BoolProperty(name='Square Corners', default=True)

    show_cuts = False
    face_mode = False
    region = None
    rv3d = None
    screen_x = 0
    matrix = None
    mouse_pos = [0, 0]
    visited = []

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout
        if self.show_cuts:
            layout.use_property_split = True
            layout.prop(context.window_manager.BDSM_Context, 'step')
            if self.face_mode:
                layout.prop(self, 'square', expand=True, toggle=True)

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        self.edge_cuts = context.window_manager.BDSM_Context.step
        return self.execute(context)

    def execute(self, context):
        select_mode = context.tool_settings.mesh_select_mode[:]
        single_edge = False
        added_counter = 0

        if select_mode[2]:
            self.face_mode = True

        # No selection (or 1 vert) -> knife
        context.object.update_from_editmode()
        object_selected = [object for object in context.selected_objects if object.type == 'MESH']
        if not object_selected:
            object_selected.append(context.object)

        verts_selected = []
        for object in object_selected:
            verts_selected.extend([vert for vert in object.data.vertices if vert.select])
        if not verts_selected or len(verts_selected) == 1:
            bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
            self.report({'INFO'},'Connect: by Knife tool')
            return {'FINISHED'}

        elif select_mode[0]:
            if len(verts_selected) == 2:
                subdivide = False
                edges = [e for e in context.object.data.edges if e.select]
                if edges:
                    everts = edges[0].vertices[:]
                    selverts = [v.index for v in verts_selected]
                    if all([i for i in everts if i in selverts]):
                        subdivide = True
                if subdivide:
                    bpy.ops.mesh.subdivide('INVOKE_DEFAULT')
                    self.report({'INFO'},'Connected: Vert (subdivide)')
                    return {'FINISHED'}
            try:
                bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
            except Exception as e:
                self.report({'WARNING'},'Connect: Vertex connect path')
                bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')
            self.report({'INFO'},'Connected: Verts')
            return {'FINISHED'}

        elif select_mode[1]:
            edges_counter = []
            object_name = []

            for object in object_selected:
                mesh = object.data
                b_mesh= bmesh.from_edit_mesh(mesh)
                b_mesh.edges.ensure_lookup_table()

                edges_selected = [edge for edge in b_mesh.edges if edge.select]
                if edges_selected:
                    edges_counter.append(len(edges_selected))
                    for edge in edges_selected:
                        edge.select = False

                    new_edges = bmesh.ops.subdivide_edges(b_mesh, edges=edges_selected, cuts=context.window_manager.BDSM_Context.step, use_grid_fill=False)
                    for edge in new_edges['geom_inner']:
                        edge.select = True
                        added_counter =+ 1

                    bmesh.update_edit_mesh(mesh)
                else:
                    object_name.append(object.name)

            if any(len_edge == 1 for len_edge in edges_counter):
                single_edge = True
                bpy.ops.mesh.select_mode(type='VERT')
                select_mode = (True, False, False)

            if object_name:
                string = ', '.join(object_name)
                self.report({'WARNING'}, 'Connect: No edges selected on "%s"' % string)
            else:
                self.report({'INFO'},'Connect: Edges')

        elif select_mode[2]:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    self.region = area.regions[-1]
                    self.rv3d = area.spaces.active.region_3d

            self.screen_x = int(self.region.width * .5)

            if not object_selected:
                self.report({'INFO'}, 'Connect: No objects selected!')
                return {'CANCELLED'}

            for object in object_selected:
                self.matrix = object.matrix_world.copy()
                mesh = object.data
                b_mesh= bmesh.from_edit_mesh(object.data)
                b_mesh.edges.ensure_lookup_table()

                faces_selected = [face for face in b_mesh.faces if face.select]
                # sel_verts = [v.index for v in b_mesh.verts if v.select]

                if len(faces_selected) == 1:
                    start_edge = tools.pick_closest_edge(context, matrix=self.matrix, mousepos=self.mouse_pos, edges=faces_selected[0].edges)
                    end_edge = None
                    for edge in faces_selected[0].edges:
                        if not any(vert in edge.verts for vert in start_edge.verts):
                            end_edge = edge
                            break

                    if end_edge is None:
                        return {'CANCELLED'}

                    ring = [start_edge, end_edge]

                    for edge in b_mesh.edges:
                        edge.select = False

                    new_edges = bmesh.ops.subdivide_edges(b_mesh, edges=ring, cuts=context.window_manager.BDSM_Context.step, use_grid_fill=False)
                    for edge in new_edges['geom_inner']:
                        edge.select = True
                        added_counter =+ 1

                elif len(faces_selected) > 1:
                    face_edges = []
                    for face in faces_selected:
                        face_edges.extend(face.edges)

                    shared_edges = tools.get_duplicates(face_edges)
                    shared_edges_backup = shared_edges.copy()

                    if not shared_edges:
                        self.report({'WARNING'}, 'Connect: Invalid (Discontinuous?) selection')
                        return {'CANCELLED'}

                    rings = []
                    ring, self.visited = tools.get_edge_rings(shared_edges[0], faces_selected)
                    rings.append(ring)

                    if (len(ring) - 2) != len(shared_edges):

                        id_verts_selected = [vert.index for vert in b_mesh.verts if vert.select]

                        sanity = 9001
                        shared_edges = [edge for edge in shared_edges if edge not in ring]

                        while shared_edges or sanity > 0:
                            if shared_edges:
                                ring, face_visited = tools.get_edge_rings(shared_edges[0], faces_selected)
                                self.visited.extend(face_visited)
                                rings.append(ring)
                                shared_edges = [edge for edge in shared_edges if edge not in ring]
                            else:
                                break
                            sanity -= 1

                        # improvised solution here...as we go ;D
                        occurances = [[x, self.visited.count(x)] for x in set(self.visited)]
                        corners = []
                        cedges = []
                        for item in occurances:
                            if item[1] > 1:
                                corners.append(item[0])
                                cedges.extend(item[0].edges)

                        new_rings = []

                        for ring in rings:
                            discard = []
                            for edge in ring:
                                if edge not in shared_edges_backup and edge in cedges:
                                    discard.append(edge)

                            collect = [edge for edge in ring if edge not in discard]
                            new_rings.append(collect)

                        rings = new_rings

                        # QUAD CORNERS
                        if self.square:

                            ring_edges = [edge for ring in rings for edge in ring]
                            border_collect = []

                            for face in corners:
                                if len(face.verts) == 4:

                                    face_edges = [e for e in face.edges if e in ring_edges]

                                    if len(face_edges) == 2:
                                        face_edges_verts = face_edges[0].verts[:] + face_edges[1].verts[:]
                                        inner_vert = tools.get_duplicates(face_edges_verts)
                                        outer_vert = [vert for vert in face.verts if vert not in face_edges_verts]

                                        if inner_vert and outer_vert:
                                            convert_verts = [inner_vert[0], outer_vert[0]]
                                            border_collect.append(convert_verts)
                            if border_collect:
                                for vert in border_collect:
                                    ret = bmesh.ops.connect_verts(b_mesh, verts=vert)
                                    new_cedges = ret['edges']
                                    bmesh.update_edit_mesh(mesh)

                                    if new_cedges:
                                        rings[0].extend(new_cedges)

                        # PREP for cuts
                        for edge in b_mesh.edges:
                            edge.select_set(False)

                        for ring in rings:
                            for edge in ring:
                                edge.select_set(True)

                        # I should find a cleaner bmesh solution for cornering, but meh...
                        bpy.ops.mesh.subdivide(number_cuts=context.window_manager.BDSM_Context.step)
                        bpy.ops.mesh.tris_convert_to_quads()

                        b_mesh.verts.ensure_lookup_table()
                        verts_selected = [vert for vert in b_mesh.verts if vert.select]

                        bpy.ops.mesh.select_all(action='DESELECT')

                        for vert in verts_selected:
                            if vert.index not in id_verts_selected:
                                vert.select_set(True)

                        bpy.ops.mesh.select_mode(type='VERT')

                    else:
                        # Sinple one-ring direction cut
                        if rings:

                            for edge in b_mesh.edges:
                                edge.select = False

                            for ring in rings:
                                new_edges = bmesh.ops.subdivide_edges(b_mesh, edges=ring, cuts=context.window_manager.BDSM_Context.step, use_grid_fill=False)
                                for edge in new_edges['geom_inner']:
                                    edge.select = True
                                    added_counter =+ 1

                        b_mesh.verts.ensure_lookup_table()

                else:
                    self.report({'WARNING'}, 'Nothing selected?')
                    return {'CANCELLED'}

                bmesh.update_edit_mesh(mesh)
                self.report({'INFO'},'Connected: Faces')

        if not select_mode[0]:
            self.show_cuts = True
            bpy.ops.mesh.select_mode(type='EDGE')

        if single_edge:
            self.show_cuts = True

        return {'FINISHED'}














