
import bpy , bmesh
from bpy.types import Operator
from bpy.props import EnumProperty,BoolProperty, IntProperty
from ..context import items
from ..utils import tools

def loop_more_next(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_next.link_loop_radial_next.link_loop_next
    return next_loop

def loop_more_prev(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_radial_next.link_loop_radial_prev.link_loop_prev.link_loop_radial_next.link_loop_prev
    return next_loop

def loop_more_dot_next(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_next.link_loop_radial_next.link_loop_next.link_loop_next.link_loop_radial_next.link_loop_next
    return next_loop

def loop_more_dot_prev(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_radial_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_radial_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_next
    next_loop = next_loop.link_loop_next
    return next_loop

def ring_more(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_radial_next.link_loop_next.link_loop_next
    return next_loop

def ring_more_dot(start_loop):
    next_loop = start_loop
    next_loop.edge.select = True
    next_loop = next_loop.link_loop_radial_next.link_loop_next.link_loop_next.link_loop_radial_next.link_loop_next.link_loop_next
    next_loop.edge.select = True
    return next_loop

class BDSM_Mesh_Edge_Select_Loop_Step(Operator):
    bl_idname = "mesh.bdsm_mesh_edge_select_loop_step"
    bl_label = "BDSM Mesh Edge Select Loop step"
    bl_description = "BDSM Mesh Edge Select Loop step"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        items=(items.get_select_loop_step),
        name="Type"
    )
    step: IntProperty(
        name="Step",
        default=1,
        min=1,
        max=1000,
        description="Step loop",
    )
    less: BoolProperty(
        name="Less",
        default= False,
    )
    dotgap: BoolProperty(
        name="Dot Gap",
        default= False,
    )

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        active_obj = bpy.context.object # active mesh data

        if active_obj is None:
            active_obj = context.object
        for i in range(self.step):
            b_mesh = bmesh.from_edit_mesh(active_obj.data)
            b_mesh.verts.ensure_lookup_table()
            b_mesh.edges.ensure_lookup_table()
            b_mesh.faces.ensure_lookup_table()


            selected_verts = [vert for vert in b_mesh.verts if vert.select]
            selected_edges = [edge for edge in b_mesh.edges if edge.select]

            if self.type == "LOOP" and self.less is False and self.dotgap is False:
                for edge in selected_edges:
                    true_link = [edge.index for vert in edge.verts for edge in vert.link_edges]
                    is_border  = edge.verts[0].is_boundary is True and edge.verts[1].is_boundary is True
                    if len(edge.link_loops)>0:
                        if is_border:
                            for loop in edge.link_loops:
                                if loop_more_next(loop).edge.index in true_link:
                                    loop_more_next(loop).edge.select = True
                                if loop_more_prev(loop).edge.index in true_link:
                                    loop_more_prev(loop).edge.select = True
                        else:
                            for loop in edge.link_loops:
                                if loop_more_next(loop).vert.is_boundary is False:
                                    loop_more_next(loop).edge.select = True
            if self.type == "RING" and self.less is False and self.dotgap is False:
                for edge in selected_edges:
                    if len(edge.link_loops)>0:
                        for loop in edge.link_loops:
                            # if ring_more(loop).vert.is_boundary is False:
                            ring_more(loop).edge.select = True
                b_mesh.select_history.clear()
            if self.type == "LOOP" and self.less is True and self.dotgap is False:
                connected = [[vert,edge] for vert in selected_verts for edge in vert.link_edges if edge in selected_edges]
                connected_verts = [vert for [vert,edge] in connected]
                endpoint_verts = [vert for vert in connected_verts if connected_verts.count(vert) == 1]
                endpoint_edge = [edge for [vert, edge] in connected if vert in endpoint_verts]
                for vert in endpoint_verts:
                    vert.select = False
                for edge in endpoint_edge:
                    edge.select = False
            if self.type == "RING" and self.less is True and self.dotgap is False:
                connected = [[edge,face] for edge in selected_edges for face in edge.link_faces]
                connected_face = [face for [edge,face] in connected]
                endpoint_face = [face for face in connected_face if connected_face.count(face) == 1]
                endpoint_edge = [edge for [edge, face] in connected if face in endpoint_face]
                for edge in endpoint_edge:
                    edge.select = False
                for face in endpoint_face:
                    face.select = False
            #loop =selected_edges[0].link_loops[0]
            if self.type == "LOOP" and self.less is False and self.dotgap is True:
                for edge in selected_edges:

                    loop_current_next = loop_more_next(edge.link_loops[0])
                    loop_current_prev = loop_more_prev(edge.link_loops[0])
                    loop_current_dot_next = loop_more_dot_next(edge.link_loops[0])
                    loop_current_dot_prev = loop_more_dot_prev(edge.link_loops[0])

                    true_link_next = [edge.index for vert in loop_current_dot_next.edge.verts for edge in vert.link_edges]
                    true_link_prev = [edge.index for vert in loop_current_dot_prev.edge.verts for edge in vert.link_edges]

                    true_link = true_link_next + true_link_prev
                    true_link =  [ edge for edge in true_link if true_link.count(edge)>1]
                    true_link = list(set(true_link))

                    self.report({"INFO"},' '.join(map(str, true_link)))
                    is_border  = edge.verts[0].is_boundary is True and edge.verts[1].is_boundary is True
                    link_edges = [edge for vert in edge.verts for edge in vert.link_edges]
                    link_edges_next = [edge for vert in loop_current_next.edge.verts for edge in vert.link_edges]
                    link_edges_prev = [edge for vert in loop_current_prev.edge.verts for edge in vert.link_edges]

                    if len(edge.link_loops)>0 and len(link_edges) >= 6 and len(link_edges) <=8:
                        for loop in edge.link_loops:
                            loop_dot_next = loop_more_dot_next(loop)
                            loop_dot_prev = loop_more_dot_prev(loop)
                            if is_border:
                                if loop_dot_next.edge.index in true_link and len(link_edges_next) >= 6 and len(link_edges_next) <=8:
                                    loop_dot_next.edge.select = True
                                if loop_dot_prev.edge.index in true_link and len(link_edges_prev) >= 6 and len(link_edges_prev) <=8:
                                    loop_dot_prev.edge.select = True
                            else:
                                if loop_dot_next.vert.is_boundary is False and loop_more_next(loop).vert.is_boundary is False:
                                    loop_dot_next.edge.select = True
            if self.type == "RING" and self.less is False and self.dotgap is True:
                for edge in selected_edges:
                    if len(edge.link_loops)>0:
                        for loop in edge.link_loops:
                            ring_more_dot(loop).edge.select = True

            if self.type == "LOOP" and self.less is True and self.dotgap is True:
                boder_disconnect_edges = [ edge for vert in selected_verts for edge in vert.link_edges if edge.select is False]
                disconnect_edges = list(set([edge for edge in boder_disconnect_edges if boder_disconnect_edges.count(edge) > 1]))
                indirect_edges = selected_edges + disconnect_edges
                #
                connected = [[vert,edge] for vert in selected_verts for edge in vert.link_edges if edge in indirect_edges]
                connected_verts = [vert for [vert,edge] in connected]
                endpoint_verts = [vert for vert in connected_verts if connected_verts.count(vert) == 1]
                endpoint_edge = [edge for [vert, edge] in connected if vert in endpoint_verts]
                for vert in endpoint_verts:
                    vert.select = False
                for edge in endpoint_edge:
                    edge.select = False
            if self.type == "RING" and self.less is True and self.dotgap is True:
                border_faces = [face for edge in selected_edges for face in edge.link_faces]
                border_edge = [edge for face in border_faces for edge in face.edges]
                indirect_edges = list(set([edge for edge in border_edge if border_edge.count(edge) > 1]))
                #
                connected = [[edge,face] for edge in indirect_edges for face in edge.link_faces]
                connected_face = [face for [edge,face] in connected]
                endpoint_face = [face for face in connected_face if connected_face.count(face) == 1]
                endpoint_edge = [edge for [edge, face] in connected if face in endpoint_face]
                for edge in endpoint_edge:
                    edge.select = False
                for face in endpoint_face:
                    face.select = False
            b_mesh.select_history.clear()
            bmesh.update_edit_mesh(active_obj.data)
        return {'FINISHED'}
