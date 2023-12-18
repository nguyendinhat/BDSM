import bpy, bmesh, time
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty

import numpy as np
from math import pow
from mathutils import Vector

from .. lib.smooth import CommonSmoothMethods

from .. utils.smooth import get_bmesh, close_bmesh, get_mirrored_axis, get_mirrored_verts

class BDSM_Mesh_Smooth_Laplacian(Operator, CommonSmoothMethods):
    bl_idname = 'mesh.bdsm_mesh_smooth_laplacian'
    bl_label = 'BDSM Smooth Laplacian'
    bl_description = 'BDSM Smooth Laplacian'
    bl_options = {'REGISTER', 'UNDO'}

    smooth_amount: FloatProperty(name='Smooth amount', description='Smooth amount', default=1, min=0, max=1, step=10, precision=2)
    # beta:= FloatProperty(name='beta', description='Beta i influence (vs neibors)', default=0.5, min=0, max=1, step=10, precision=2)
    # beta_inf:= FloatProperty(name='beta influence', description='Beta influence ', default=1, min=0, max=1, step=10, precision=2)
    iteration_amount: IntProperty(name='Iterations', description='Number of times to repeat the smoothing', default=5, min=0, soft_max=20)
    # preserveVol: FloatProperty(name='Maintain Volume', description='Maintain  Volume', default=0.0, min=0, max=1, step=0.5, precision=2)
    alpha: FloatProperty(name='Origin influence', description='Strength of original vertex position influence', default=0.5, min=0, max=1, step=10, precision=1)
    tension: bpy.props.EnumProperty(
                                    items = (('UNIFORM','Uniform','','',0),
                                            ('INVERSE','Inverse to edge length','','',1),
                                            ('PROPORTIONAL','Proportional to edge length','','',2)),
                                    name = 'Tension',
                                    default = 'UNIFORM',)
    sharp_edge_weight: IntProperty(name='Sharp edge weight', description='sharp edge weight', default=1, min=0, max=100, step=1)
    freeze_border: BoolProperty( name='Freeze border', description='Freeze border verts', default=False)
    # force_numpy: BoolProperty( name='Force Numpy', description='Force algorithm to use Numpy', default=False)

    def lc_smooth_mesh(self, context):
        beta = 1-self.smooth_amount*0.5 #map smooth ammount from <0,1> to beta <0,7; 1>
        source = context.active_object.data
        delta = 0.0001
        startTime = time.time()
        bm = get_bmesh(context, context.active_object.data)
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis (context.active_object)
        selected_vertices = [ v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = selected_vertices = [ v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        o_co =np.array([vert.co.copy() for vert in bm.verts]  )
        p_co =  np.copy(o_co)
        b_co = np.zeros(shape=(len(bm.verts),3), dtype=np.float32)
        q_co = np.copy(o_co)

        edge_weights = [1]*len(bm.edges)
        sel_v_mask = np.array([v.select for v in bm.verts])
        edge_keys = np.array([ [edge.verts[0].index, edge.verts[1].index] for edge in  bm.edges])
        for x in range(self.iteration_amount):
            q_co[sel_v_mask] = np.copy(p_co[sel_v_mask])
            b_co.fill(0)
            p_co.fill(0)
            diff = q_co[edge_keys[:,1]] - q_co[edge_keys[:,0]]
            if self.tension == 'PROPORTIONAL':
                edge_weights = np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff) ),0.0001)
            elif self.tension == 'INVERSE':# cos strength in inverse prop to len (maybe should be squared?)
                edge_weights = 1/ np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)) ,0.0001)
            for vertex in selected_vertices:
                linked_edges = len(vertex.link_edges)
                if linked_edges==0:
                    continue
                i = vertex.index
                edges_weight_total = 0
                boundary_mirrored_edges= 0
                for edge in vertex.link_edges:
                    if not vertex.is_boundary or edge.is_boundary:
                        i_other = edge.other_vert(vertex).index
                        edges_weight_total += edge_weights[edge.index]
                        p_co[i] += (q_co[i_other]- q_co[i])*edge_weights[edge.index]
                    else:
                        edges_weight_total += 2*edge_weights[edge.index]
                        # edges_weight_total += edge_weights[edge.index]
                        boundary_mirrored_edges +=1 #times 2 cos we count virulat boundary mirror edge....
                # p_co[i] = q_co[i] + (p_co[i] / edges_weight_total - q_co[i])/(linked_edges+2*boundary_mirrored_edges)
                p_co[i] = q_co[i] + p_co[i] / edges_weight_total
            p_co[~sel_v_mask] = o_co[~sel_v_mask]
            b_co = p_co - (self.alpha*o_co  + (1-self.alpha) * q_co)
            beta_sum = np.zeros(3, dtype = np.float32)
            for vertex in selected_vertices:
                if len(vertex.link_edges)==0:
                    continue
                beta_sum.fill(0)
                i = vertex.index
                boundary_mirrored_edges = 0
                for edge in vertex.link_edges:
                    i_other = edge.other_vert(vertex).index
                    if not vertex.is_boundary or edge.is_boundary:
                        beta_sum += b_co[i_other]
                    else: #for border vert and non border edge ignore

                        boundary_mirrored_edges +=1
                b_sum_projected_to_normal = bm.verts[i].normal*np.dot(bm.verts[i].normal,beta_sum/(len(vertex.link_edges)-boundary_mirrored_edges))
                p_co[i]  = p_co[i] - (beta*b_co[i] + (1-beta)*b_sum_projected_to_normal)*self.beta_inf

        for i, vertex in enumerate(selected_vertices):
            vertex.co = Vector(p_co[vertex.index]) #- projected_diff_on_normal * self.preserveVol
        # print('Laplacian smooth took: '+ str(time.time()-startTime)+' sec')
        close_bmesh(context, bm, context.active_object.data)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def draw(self, context):
        prefs = bpy.context.preferences.addons['BDSM'].preferences
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'smooth_amount')
        col.prop(self, 'iteration_amount')
        col.prop(self, 'tension')
        col.prop(self, 'alpha')
        col.prop(self, 'freeze_border')
        col.prop(self, 'sharp_edge_weight')
        row = layout.row(align=True)
        row.prop_search(prefs, 'smooth_mask', context.active_object, 'vertex_groups', text='Vertex Group')
        row.prop(prefs, 'invert_mask', text='', icon='ARROW_LEFTRIGHT', toggle=True)

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.mode == 'EDIT' and obj.type == 'MESH')
    def execute(self, context):
        # if self.force_numpy:
        np_vg_weights = self.get_vg_weights(context)
        self.numpy_smooth_init(context, method='LC', tension=self.tension, vg_mask=np_vg_weights)
        # else:
        #     self.lc_smooth_mesh(context)
        return {'FINISHED'}

class BDSM_Mesh_Smooth_Inflate(Operator, CommonSmoothMethods):
    bl_idname = 'mesh.bdsm_mesh_smooth_inflate'
    bl_label = 'BDSM Mesh Smooth Inflate'
    bl_description = 'BDSM Mesh Smooth Inflate'
    bl_options = {'REGISTER', 'UNDO'}

    smooth_amount: FloatProperty(name='Smooth Amount', description='Amount of smoothing to apply', default=1, min=0, max=1, step=10, precision=2)
    iteration_amount: IntProperty(name='Iterations', description='Number of times to repeat the smoothing', default=5, min=1, soft_max=20, step=1)
    Inflate: FloatProperty(name='Inflate', description='Inflate', default=1, min=-2, max=2, step=10, precision=2)
    normal_smooth: FloatProperty(name='Normal Smooth', description='Amount of smoothing to normals', default=0.5, min=0, max=1, step=10, precision=2)

    tension: bpy.props.EnumProperty(
                                    items = (('UNIFORM','Uniform','','',0),
                                            ('INVERSE','Inverse to edge length','','',1),
                                            ('PROPORTIONAL','Proportional to edge length','','',2)),
                                    name = 'Tension',
                                    default = 'UNIFORM',)
    sharp_edge_weight: IntProperty(name='Sharp edge weight', description='sharp edge weight', default=1, min=0, max=100, step=1)
    freeze_border: BoolProperty( name='Freeze border', description='Freeze border verts', default=False)
    # force_numpy: BoolProperty( name='Force Numpy', description='Force algorithm to use Numpy', default=False)


    def inflate_smooth(self,context, bm):
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis (context.active_object)
        selected_vertices = [ v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = selected_vertices = [ v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        #Go through each vertex and compute their smoothed position.
        o_normal  = [vert.normal.copy() for vert in bm.verts]

        edge_weights = [1]*len(bm.edges)

        o_co = [vert.co.copy() for vert in bm.verts]
        q_co = o_co[:]
        p_co = o_co[:]
        edge_weights = [1]*len(bm.edges)
        diff_projected_on_normal_scalar_li = [0]*len(bm.verts)

        p_normal = o_normal[:]
        for i in range(self.iteration_amount):
            if self.tension == 'PROPORTIONAL':
                edge_weights = [pow(edge.calc_length(),2) for edge in bm.edges]
            elif self.tension == 'INVERSE':# cos strength in inverse prop to len (maybe should be squared?)
                edge_weights = [1/max(edge.calc_length(), 0.001) for edge in bm.edges]
            new_co_dif = [Vector((0,0,0))]*len(bm.verts)
            q_normal = p_normal[:]
            p_normal = [Vector((0,0,0))]*len(bm.verts)
            for vertex in selected_vertices:
                i = vertex.index
                temp_new_normal = Vector((0,0,0)) #cos stupid bug in blender if normalizing vector list element
                total_sum = Vector((0, 0, 0))
                edge_count = len(vertex.link_edges)
                if edge_count==0:
                    continue
                edges_weight_total = 0
                for edge in vertex.link_edges:
                    neighbor_vert = edge.other_vert(vertex)
                    edge_weight = edge_weights[edge.index]
                    edges_weight_total += edge_weight
                    to_neighbor_vert_dir = bm.verts[neighbor_vert.index].co - vertex.co
                    if not vertex.is_boundary or edge.is_boundary : #skip bounary vert and not boundary edges.
                        total_sum += to_neighbor_vert_dir*edge_weight
                        temp_new_normal += q_normal[neighbor_vert.index]*edge_weight
                new_co_dif[i] = total_sum  / edges_weight_total / edge_count
                if x_axis_mirror and vertex.co[0]<= delta: #preserve mirrored vert splitting
                    new_co_dif[i][0] = 0
                    temp_new_normal[0] = 0
                if y_axis_mirror and vertex.co[1]<= delta:
                    new_co_dif[i][1] = 0
                    temp_new_normal[1] = 0
                if z_axis_mirror and vertex.co[2]<= delta:
                    new_co_dif[i][2] = 0
                    temp_new_normal[2] = 0

                p_normal[i] = temp_new_normal.normalized()
                diff_projected_on_normal_scalar_li[i] = p_normal[i].dot(new_co_dif[i])
            #average offsett along normal if smoothed normal is used.
            aver_normal_scalar = sum(diff_projected_on_normal_scalar_li)/len(selected_vertices)
            for vertex in selected_vertices:
                i = vertex.index
                vertex.co = vertex.co + self.smooth_amount*new_co_dif[i]
                projected_diff_on_normal = p_normal[i]*(diff_projected_on_normal_scalar_li[i]*(1-self.normal_smooth) +self.normal_smooth* aver_normal_scalar)  # u(u dot v)  - projection of v on u
                # projected_diff_on_normal = p_normal* p_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                vertex.co -= self.smooth_amount * projected_diff_on_normal * self.Inflate
        # print('Inflate smooth  took: '+ str(time.time()-startTime)+' sec')

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and  obj.type == 'MESH')

    def draw(self, context):
        prefs = context.preferences.addons['BDSM'].preferences
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'smooth_amount')
        col.prop(self, 'iteration_amount')
        col.prop(self, 'tension')
        col.prop(self, 'normal_smooth')
        col.prop(self, 'Inflate')
        col.prop(self, 'freeze_border')
        col.prop(self, 'sharp_edge_weight')
        row = layout.row(align=True)
        row.prop_search(prefs, 'smooth_mask', context.active_object, 'vertex_groups', text='Vertex Group')
        row.prop(prefs, 'invert_mask', text='', icon='ARROW_LEFTRIGHT', toggle=True)

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.mode == 'EDIT' and obj.type == 'MESH')
    def execute(self, context):
        # if  context.active_object.mode == 'OBJECT' or self.force_numpy or np.sum(sel_verts)> len(bm.verts)/5: #if we select more than 20% verts use numpy
        np_vg_weights = self.get_vg_weights(context)
        self.numpy_smooth_init(context, method='INFlATE', tension=self.tension, vg_mask=np_vg_weights)
        return {'FINISHED'}

class BDSM_Mesh_Smooth_Volume(Operator, CommonSmoothMethods):
    bl_idname = 'mesh.bdsm_mesh_smooth_volume'
    bl_label = 'BDSM Mesh Smooth Volume'
    bl_description = 'BDSM Mesh Smooth Volume'
    bl_options = {'REGISTER', 'UNDO'}


    smooth_amount: FloatProperty(name='Smooth amount', description='Smooth amount', default=1, min=0, max=1, step=1, precision=2)
    iteration_amount: IntProperty(name='Iterations', description='Number of times to repeat the smoothing', default=5, min=1, soft_max=20)
    tension: bpy.props.EnumProperty(
                                    items = (('UNIFORM','Uniform','','',0),
                                            ('INVERSE','Inverse to edge length','','',1),
                                            ('PROPORTIONAL','Proportional to edge length','','',2)),
                                    name = 'Tension',
                                    default = 'UNIFORM',)
    sharp_edge_weight: IntProperty(name='Sharp edge weight', description='sharp edge weight', default=1, min=0, max=100, step=1)
    freeze_border: BoolProperty( name='Freeze border', description='Freeze border verts', default=False)
    normal_smooth: FloatProperty(name='Normal Smooth', description='Amount of smoothing to normals', default=0.5, min=0, max=1, step=10, precision=2)
    Inflate: FloatProperty(name='Inflate', description='Inflate', default=0.85, min=0, max=2, step=10, precision=2)

    # force_numpy: BoolProperty( name='Force Numpy', description='Force algorithm to use Numpy', default=False)

    def vol_smooth_mesh(self, context):
        # beta = 1-self.smooth_amount*0.6 #map smooth ammount from <0,1> to beta <0,7; 1>
        beta = 1-self.smooth_amount*(0.6 - (self.iteration_amount/20*0.1)) #map smooth ammount from <0,1> to beta <0,7; 1>
        source = context.active_object.data
        bm = bmesh.from_edit_mesh(source)
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis (context.active_object)
        selected_vertices = [ v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = [ v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        # Go through each vertex and compute their smoothed position.

        startTime=time.time()

        vert_connections = []
        for vertex  in selected_vertices:
            edges_count = len(vertex.link_edges)
            boundary_mirrored_edges = 0
            for edge in vertex.link_edges:
                if  vertex.is_boundary and not edge.is_boundary :
                     boundary_mirrored_edges +=1
            vert_connections.append([edges_count + boundary_mirrored_edges, edges_count - boundary_mirrored_edges])
        for i in range(self.iteration_amount):
            edge_weights = [0]*len(bm.edges)
            new_co_diff = [Vector((0, 0, 0))]*len(bm.verts)

            for vertex, v_links in zip(selected_vertices,vert_connections):
                if v_links[0]==0:
                    continue
                total_sum = Vector((0, 0, 0))
                edges_weight_total = 0
                for edge in vertex.link_edges:
                    neighbor_vert = edge.other_vert(vertex)
                    if edge_weights[edge.index] == 0:
                        edge_len = edge.calc_length()
                        if edge_len == 0:
                            edge_len = 0.001
                        if self.tension =='UNIFORM':
                            edge_weights[edge.index] = pow(edge_len,2)
                        else:# cos strength in inverse prop to len (maybe should be squared?)
                            edge_weights[edge.index] = 1/edge_len
                    edge_weight = edge_weights[edge.index]
                    edges_weight_total += edge_weight
                    to_neighbor_vert_dir = bm.verts[neighbor_vert.index].co - vertex.co
                    if not vertex.is_boundary or edge.is_boundary :
                        total_sum += to_neighbor_vert_dir*edge_weight

                new_co_diff[vertex.index] = total_sum / edges_weight_total / v_links[0]
            for vertex, v_links in zip(selected_vertices,vert_connections):
                if v_links[0]==0:
                    continue
                beta_x = Vector((0, 0, 0))
                for edge in vertex.link_edges:
                    if not vertex.is_boundary or edge.is_boundary :
                        neighbor_vert = edge.other_vert(vertex)
                        beta_x += new_co_diff[neighbor_vert.index]
                beta_sum = beta_x/v_links[1]
                vert_offset = new_co_diff[vertex.index] - (beta*new_co_diff[vertex.index] + (1-beta)*beta_sum)
                if x_axis_mirror and vertex.co[0]<= delta: #preserve mirrored vert splitting
                    vertex.normal[0] = 0
                if y_axis_mirror and vertex.co[1]<= delta:
                    vertex.normal[1] = 0
                if z_axis_mirror and vertex.co[2]<= delta:
                    vertex.normal[2] = 0

                projected_diff_on_normal = vertex.normal *  vertex.normal.dot( vert_offset)  # u(u dot v)  - projection of v on u
                vertex.co = vertex.co + vert_offset -  projected_diff_on_normal * self.Inflate
        # Update the user mesh.
        # print('Volume smooth took: '+ str(time.time()-startTime)+' sec')
        bm.normal_update()
        bmesh.update_edit_mesh(source, loop_triangles=False, destructive=False)
        # bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.mode == 'EDIT' and obj.type == 'MESH')

    def draw(self, context):
        prefs = context.preferences.addons['BDSM'].preferences
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'smooth_amount')
        col.prop(self, 'iteration_amount')
        col.prop(self, 'tension')
        col.prop(self, 'normal_smooth')
        col.prop(self, 'Inflate')
        col.prop(self, 'freeze_border')
        col.prop(self, 'sharp_edge_weight')
        row = layout.row(align=True)
        row.prop_search(prefs, 'smooth_mask', context.active_object, 'vertex_groups', text='Vertex Group')
        row.prop(prefs, 'invert_mask', text='', icon='ARROW_LEFTRIGHT', toggle=True)

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)

    def execute(self, context):
        np_vg_weights = self.get_vg_weights(context)
        self.numpy_smooth_init(context, method='VOL', tension=self.tension, vg_mask=np_vg_weights)
        return {'FINISHED'}
