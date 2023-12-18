import bpy
import numpy as np

from .. utils.smooth import raycast, get_weights,get_mirrored_axis,get_bmesh,close_bmesh, new_bincount,three_d_bincount_add, get_view_vec, draw_circle_px, get_obj_mesh_bvht
class CommonSmoothMethods():

    @staticmethod
    def get_vg_weights(context):
        np_vg_weights = None
        obj = context.active_object
        prefs = context.preferences.addons['BDSM'].preferences
        if prefs.smooth_mask: # get vertex group mask as float
            vg = obj.vertex_groups[prefs.smooth_mask]
            vg_weights = get_weights(obj, vg)
            np_vg_weights = np.array(vg_weights)
            if obj.bdsm.invert_mask:
                np_vg_weights = 1-np_vg_weights
        return np_vg_weights


    # @cache    # gives infinite boost
    def numpy_smooth_init(self, context, method='LC', from_brush = False, tension='UNIFORM', vg_mask = None):
        # beta = 1-self.smooth_amount*0.6 #map smooth ammount from <0,1> to beta <0,7; 1>
        beta = 1-self.smooth_amount*(0.6 - (self.iteration_amount/20*0.1))  # map smooth ammount from <0,1> to beta <0,7; 1>

        mirror_axes, delta = get_mirrored_axis(context.active_object)
        bm = get_bmesh(context, context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.index_update()
        bm.edges.index_update()

        if from_brush and not self.only_selected:  # smooth all verts
            sel_v = tuple(v for v in bm.verts if not v.hide)
            if len(sel_v) == 0:
                self.report({'ERROR'}, 'No vertices were selected!\nDisable \'Only Selected\' option (or select vertices).\nCancelling')
                return 'CANCELLED'
            sel_adj_verts_ids = [v.index for v in sel_v]
            sel_adj_verts_ids.extend([e.other_vert(s_vert).index for s_vert in sel_v for e in s_vert.link_edges if e.hide])
            sel_e = tuple(e for e in bm.edges if not e.hide)
            sel_adj_verts_ids_unique = np.unique(sel_adj_verts_ids)  # remove duplis
            sel_verts = np.array(tuple(not bm.verts[old_index].hide for old_index in sel_adj_verts_ids_unique), dtype='?') # bool
        else:  #N: automatically hidden mesh is assumed to be non selected.
            sel_v = tuple(v for v in bm.verts if v.select)
            if len(sel_v) == 0:
                self.report({'ERROR'}, 'No vertices were selected!\nDisable \'Only Selected\' option (or select vertices).\nCancelling')
                return 'CANCELLED'
            sel_adj_verts_ids = [v.index for v in sel_v]
            sel_adj_verts_ids.extend([e.other_vert(s_vert).index for s_vert in sel_v for e in s_vert.link_edges if not e.select])
            sel_e = tuple(e for e in bm.edges if e.select)
            sel_adj_verts_ids_unique = np.unique(sel_adj_verts_ids)  # remove duplis
            sel_verts = np.array(tuple(bm.verts[old_index].select for old_index in sel_adj_verts_ids_unique), dtype='?')


        o_normal = np.array([bm.verts[old_index].normal for old_index in sel_adj_verts_ids_unique])
        o_co = np.array([bm.verts[old_index].co for old_index in sel_adj_verts_ids_unique])
        if vg_mask is not None: # float  (0, 1) range mask. Use to blend between smooth and non smooth
            vg_mask = np.array([vg_mask[old_index] for old_index in sel_adj_verts_ids_unique])

        on_axis_vmask = {}
        for axis_id in mirror_axes:  # adjust normals for center verts
            on_axis_vmask[axis_id] = np.abs(o_co[:, axis_id]) < delta  # True for verts on mirror axis
            o_normal[on_axis_vmask[axis_id], axis_id] = 0

            #normalize on axis normals
            normals_mag = np.sqrt(np.einsum('...i,...i', o_normal[on_axis_vmask[axis_id]], o_normal[on_axis_vmask[axis_id]]))
            o_normal[on_axis_vmask[axis_id]] /= normals_mag[:, None]  # total_normal.normalize()

        vert_count = sel_adj_verts_ids_unique.shape[0]
        orig_to_new_idx = dict(zip(sel_adj_verts_ids_unique, range(sel_adj_verts_ids_unique.shape[0])))

        edge_keys = []
        border_vert_ek_mask = [] # list of (e.v1, e.v2)   - 1 everywere where vert will pull neibors.  Only 0 for border verts on non border edges
        sharp_edges = []
        sharp_verts = []

        for edge in sel_e: #N: file border_vert_ek_mask, etc.
            v1_id = orig_to_new_idx[edge.verts[0].index]
            v2_id = orig_to_new_idx[edge.verts[1].index]
            if edge.is_boundary: # boundary edges have  100% influence for  adjacent verts
                border_vert_ek_mask.append([True,True])
            else:  # find all inner mesh edges. And partially weights edges connected to border verts
                v1_is_on_axis = False  # does v1 belongs to center mirror of any axis?
                v2_is_on_axis = False  # does vs belongs to center mirror  of any axis?

                # XXX: does it event work for y, z  mirror symmetry?
                for axis_id, mirror_mask in on_axis_vmask.items():   # we dont care about which axis it lays on (x, y or z)
                    v1_is_on_axis = True if mirror_mask[v1_id] else v1_is_on_axis
                    v2_is_on_axis = True if mirror_mask[v2_id] else v2_is_on_axis


                if v1_is_on_axis and v2_is_on_axis: #special condition - else these 2verts would always pull - but we do not want to pull on axis border verts though
                    border_vert_ek_mask.append([not edge.verts[0].is_boundary,
                                                not edge.verts[1].is_boundary])
                else: #vert pulls if non_boundary or  (boundary but on axis)
                    border_vert_ek_mask.append([not edge.verts[0].is_boundary or v1_is_on_axis,
                                               not edge.verts[1].is_boundary or v2_is_on_axis ])

                #DONE: need to add mirror_axis touching edge second time
                if v1_is_on_axis^v2_is_on_axis:  # add non border edges, when one of (e.v1 xor e.v2) is on mirror axis.
                    border_vert_ek_mask.append([v1_is_on_axis, v2_is_on_axis])  # add fake edge for negative mirror side (actually can be same edge 2x. cos we ignore x component (x=0))
                    sharp_edges.append(not edge.smooth) # add same twice to sharp_edges
                    edge_keys.append([v1_id, v2_id])

            edge_keys.append([v1_id, v2_id])
            sharp_edges.append(not edge.smooth)
            if not edge.smooth:
                sharp_verts.append((orig_to_new_idx[edge.verts[0].index], orig_to_new_idx[edge.verts[1].index]))

        sel_border_verts = [False]*len(sel_adj_verts_ids_unique)
        for s_vert in sel_v:  #N: get non selected edges, but connected to sel_v - as additional smoothing inluencers
            #if drawing by brush (old was not_sel_edges_adj = [] - cos no adjacent non selected edges when all is selected)
            #if smoothing whole mesh then pick hidden edges if any exist
            not_sel_edges_adj = [e for e in s_vert.link_edges if e.hide] if from_brush and not self.only_selected else [e for e in s_vert.link_edges if not e.select]
            if self.freeze_border  and ((from_brush and self.only_selected) or not from_brush):
                not_sel_faces_adj = [f for f in s_vert.link_faces if not f.select]
                sel_border_verts[orig_to_new_idx[s_vert.index]] = len(not_sel_faces_adj)!= 0

            for nsel_e in not_sel_edges_adj:
                edge_keys.append([orig_to_new_idx[nsel_e.verts[0].index], orig_to_new_idx[nsel_e.verts[1].index]])
                # border_vert_ek_mask.append( [not nsel_e.verts[0].is_boundary or nsel_e.is_boundary, not nsel_e.verts[1].is_boundary or nsel_e.is_boundary] )
                border_vert_ek_mask.append([not nsel_e.verts[0].is_boundary or nsel_e.is_boundary,
                                            not nsel_e.verts[1].is_boundary or nsel_e.is_boundary])

                sharp_edges.append(not nsel_e.smooth)
                if not nsel_e.smooth:
                    sharp_verts.extend([(orig_to_new_idx[nsel_e.verts[0].index], orig_to_new_idx[nsel_e.verts[1].index])])
        edge_keys = np.array(edge_keys)
        border_vert_ek_mask = np.array(border_vert_ek_mask)
        sharp_edges = np.array(sharp_edges)  # search for vert that are belonging to sharp edges
        sharp_verts = np.unique(sharp_verts)

        # sharp_edge_neighbors_mask = np.isin(edge_keys, list(sharp_verts)) #find sharp_verts in edge_keys, create mask
        sharp_edge_neighbors_mask = np.in1d(edge_keys, list(sharp_verts))  # find sharp_verts in edge_keys, create mask
        sharp_edge_neighbors_mask.shape = edge_keys.shape
        v_linked_edges = np.zeros(vert_count, dtype=np.float32)
        new_bincount(v_linked_edges, edge_keys[:, 1])
        new_bincount(v_linked_edges, edge_keys[:, 0])

        #count sharp connected edges to vert (==connected edges that are sharp)
        v_sharp_connections = np.zeros(vert_count, dtype=np.float32)
        new_bincount(v_sharp_connections, edge_keys[:, 1], sharp_edges)
        new_bincount(v_sharp_connections, edge_keys[:, 0], sharp_edges)

        freeze_verts = ~sel_verts
        freeze_verts |= v_linked_edges <= 2  # freeze verts with only two edges connected
        freeze_verts |= v_sharp_connections > 2  # freeze verts idf 3 or more sharp edges connected
        freeze_verts |= np.logical_and(v_sharp_connections == 2, v_linked_edges == 3)  # freeze verts with 3 edges if 2 are sharp
        freeze_verts |= v_sharp_connections == 1  # freeze verts if one one sharp edge is connected
        if self.freeze_border:
            freeze_verts |= np.array([bm.verts[old_index].is_boundary for old_index in sel_adj_verts_ids_unique])
            if (from_brush and self.only_selected) or not from_brush:
                freeze_verts |= np.array(sel_border_verts, 'bool')

        #remove sharp edges, so we are left only with neighbors mask
        sharp_edge_neighbors_mask[sharp_edges] = [False, False]  # change double [True,True] to false
        slide_ek_mask = np.logical_and(border_vert_ek_mask, ~sharp_edge_neighbors_mask)

        p_co = np.copy(o_co)  # current new vertex position
        p_normal = np.copy(o_normal)
        b_co = np.zeros(shape=(vert_count, 3), dtype=np.float32)  # offset in iteration x, of vert i

        b_co_sum_neighbors = np.copy(b_co)  # offset in iteration x, of vert i

        v_boundary_mirrored_edges = np.zeros(vert_count, dtype=np.float32)
        #~border_vert_ek_mask[:,0]+1 - ones everywhere, exept 0 where border vert and non border edge.
        new_bincount(v_boundary_mirrored_edges, edge_keys[:, 1], -1*~border_vert_ek_mask[:, 1]+1)  # numb of vert connected to Vert[ek[0]]
        new_bincount(v_boundary_mirrored_edges, edge_keys[:, 0], -1*~border_vert_ek_mask[:, 0]+1)  # numb of vert connected to Vert[ek[1]]

        sum_edge_len_per_vert = np.zeros(vert_count, dtype=np.float32)
        edge_weights = np.ones(edge_keys.shape[0])

        #when suming neibhors border_edge_m add additional weigths on boder verts
        border_edge_multiplier_1 = ~border_vert_ek_mask[:, 1]+1 + self.sharp_edge_weight*sharp_edge_neighbors_mask[:, 1]
        border_edge_multiplier_2 = ~border_vert_ek_mask[:, 0]+1 + self.sharp_edge_weight*sharp_edge_neighbors_mask[:, 0]
        if method == 'INFlATE':
            v_connections = np.zeros(vert_count, dtype=np.float32)
            #sum edges that have vert X  and either end of edge (Va, Vb)
            #~border_vert_ek_mask[:,0]+1 - ones everywhere, exept 2 where border vert and non border edge.
            new_bincount(v_connections, edge_keys[:, 1], (4*~border_vert_ek_mask[:, 1]+1) + self.sharp_edge_weight*sharp_edge_neighbors_mask[:, 1])
            new_bincount(v_connections, edge_keys[:, 0], (4*~border_vert_ek_mask[:, 0]+1) + self.sharp_edge_weight*sharp_edge_neighbors_mask[:, 0])

        #! ############
        def calc_lc_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert
            for _ in range(self.iteration_amount):
                q_co = np.copy(p_co)  # prevoius iteration vert position
                p_co.fill(0)
                b_co.fill(0)
                b_co_sum_neighbors.fill(0)
                sum_edge_len_per_vert.fill(0)
                # for ek in edge_keys:
                diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                if tension == 'PROPORTIONAL':
                    edge_weights = np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)), 0.0001)
                elif tension == 'INVERSE':  # cos strength in inverse prop to len (maybe should be squared?)
                    edge_weights = 1 / np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)), 0.0001)

                new_bincount(sum_edge_len_per_vert, edge_keys[:, 1], edge_weights*border_edge_multiplier_1)
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 0], edge_weights*border_edge_multiplier_2)
                three_d_bincount_add(p_co, edge_keys[:, 1], -1*diff*edge_weights[:, None]*slide_ek_mask[:, 1, None])
                three_d_bincount_add(p_co, edge_keys[:, 0], diff*edge_weights[:, None]*slide_ek_mask[:, 0, None])

                #this vont work with proportional version
                p_co = q_co + p_co / sum_edge_len_per_vert[:, None]  # new aver posision

                where_are_NaNs = np.isnan(p_co)  # nan on corner case - where border and shapr edges meet vert. Just use old co there
                p_co[where_are_NaNs] = q_co[where_are_NaNs]

                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co
                b_co = p_co - (self.alpha*o_co + (1-self.alpha) * q_co)  # difference

                #average of neibors vert differences
                three_d_bincount_add(b_co_sum_neighbors, edge_keys[:, 1], b_co[edge_keys[:, 0]]*slide_ek_mask[:, 1, None])
                three_d_bincount_add(b_co_sum_neighbors, edge_keys[:, 0], b_co[edge_keys[:, 1]]*slide_ek_mask[:, 0, None])

                b_sum_projected_to_normal = np.einsum('ij,i->ij', o_normal, np.einsum('ij,ij->i', o_normal, b_co_sum_neighbors/v_boundary_mirrored_edges[:, None]))
                p_co = p_co - (beta*b_co + (1-beta) * b_sum_projected_to_normal)
                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co

                if vg_mask is not None: # float  (0, 1) range mask. Use to blend between smooth and non smooth
                    p_co = vg_mask[:,None] * p_co + (1-vg_mask[:,None]) * q_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0

        def vol_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert
            for _ in range(self.iteration_amount):
                # q_normal = np.copy(p_normal) #prevoius iteration vert position
                # p_normal.fill(0)
                q_co = np.copy(p_co)  # prevoius iteration vert position
                p_co.fill(0)
                b_co.fill(0)
                b_co_sum_neighbors.fill(0)
                sum_edge_len_per_vert.fill(0)
                # for ek in edge_keys:
                diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                if tension == 'PROPORTIONAL':
                    edge_weights = np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)), 0.0001)
                elif tension == 'INVERSE':  # cos strength in inverse prop to len (maybe should be squared?)
                    edge_weights = 1 / np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)), 0.0001)
                #calculate sum of adjacent edge weights to vert
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 1], edge_weights*border_edge_multiplier_1)
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 0], edge_weights*border_edge_multiplier_2)

                # p_co[ek[0]] += q_co[ek[1]] #sum all verts for ek[0] in data[ek_vert][0]
                # p_co[ek[1]] += q_co[ek[0]] #sum all verts for ek[1] in data[ek_vert][0]
                three_d_bincount_add(p_co, edge_keys[:, 1], -1*diff*edge_weights[:, None]*slide_ek_mask[:, 1, None])
                three_d_bincount_add(p_co, edge_keys[:, 0], diff*edge_weights[:, None]*slide_ek_mask[:, 0, None])

                #this vont work with proportional version
                # p_co = p_co / sum_edge_len_per_vert[:,None]  # /v_connections[:,None]   #new aver posision
                b_co = p_co / sum_edge_len_per_vert[:, None]  # new aver posision

                b_co[freeze_verts] = 0  # not selected ver - reset to original pos o_co

                three_d_bincount_add(b_co_sum_neighbors, edge_keys[:, 1], b_co[edge_keys[:, 0]]*slide_ek_mask[:, 1, None])
                three_d_bincount_add(b_co_sum_neighbors, edge_keys[:, 0], b_co[edge_keys[:, 1]]*slide_ek_mask[:, 0, None])

                #TO prevent border vert slide ahead of loop (caused by sum_b being to big.., so reduce it by projecting on vert normal)
                #  projected b_sum on normal
                b_sum_projected_to_normal = np.einsum('ij,i->ij', o_normal, np.einsum('ij,ij->i', o_normal, b_co_sum_neighbors/v_boundary_mirrored_edges[:, None]))

                # new_co_dif = b_co - beta*b_co - (1-beta)*b_sum_projected_to_normal #   == line below
                new_co_dif = (1 - beta)*(b_co-b_sum_projected_to_normal)

                where_are_NaNs = np.isnan(new_co_dif)  # nan on corner case - where border and shapr edges meet vert. Just use old co there
                new_co_dif[where_are_NaNs] = 0

                #average normals an normalize
                # np.add.at(p_normal, edge_keys[:,1], q_normal[edge_keys[:,1]])
                # np.add.at(p_normal, edge_keys[:,0], q_normal[edge_keys[:,0]])

                # p_normal_magnitudes = np.sqrt(np.einsum('...i,...i', p_normal, p_normal))
                # p_normal /= p_normal_magnitudes[:,None] # total_normal.normalize()

                #p_normal[i].dot(new_co_dif[i])
                diff_projected_on_normal_scalar_li = np.einsum('ij,ij->i', o_normal, new_co_dif)  # normal has to be normlized
                aver_normal_scalar = np.sum(diff_projected_on_normal_scalar_li[sel_verts])/np.sum(sel_verts)

                # projected_diff_on_normal = total_normal* total_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                projected_diff_on_normal = np.einsum('ij,i->ij', o_normal, diff_projected_on_normal_scalar_li*(1-self.normal_smooth) + self.normal_smooth * aver_normal_scalar)

                p_co = q_co + new_co_dif - projected_diff_on_normal * self.Inflate  # new aver normal
                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co

                if vg_mask is not None: # float  (0, 1) range mask. Use to blend between smooth and non smooth
                    p_co = vg_mask[:,None] * p_co + (1-vg_mask[:,None]) * q_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0
                    # q_normal[mirror_center_verts,0] = 0

        def inflate_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert, p_normal, v_connections
            for _ in range(self.iteration_amount):
                q_normal = np.copy(p_normal) #prevoius iteration vert position
                p_normal.fill(0)

                q_co = np.copy(p_co) #prevoius iteration vert position
                p_co.fill(0)
                sum_edge_len_per_vert.fill(0)

                if tension == 'PROPORTIONAL':
                    diff = q_co[edge_keys[:,1]] - q_co[edge_keys[:,0]]
                    # edge_weights = np.sqrt(np.maximum(np.einsum('ij,ij->i', diff, diff) ,0.0001))
                    edge_weights = np.maximum(np.einsum('ij,ij->i', diff, diff) ,0.0001)
                elif tension == 'INVERSE':# cos strength in inverse prop to len (maybe should be squared?)
                    diff = q_co[edge_keys[:,1]] - q_co[edge_keys[:,0]]
                    edge_weights = 1/ np.maximum(np.sqrt(np.einsum('ij,ij->i', diff, diff)) ,0.0001)


                #calculate sum of adjacent edge weights to vert
                new_bincount(sum_edge_len_per_vert, edge_keys[:,0], edge_weights*slide_ek_mask[:,0])
                new_bincount(sum_edge_len_per_vert, edge_keys[:,1], edge_weights*slide_ek_mask[:,1])
                #calculate sum of adjacent edge weights to vert


                #calc average position weighted...
                three_d_bincount_add(p_co, edge_keys[:,1], q_co[edge_keys[:,0]]*edge_weights[:,None]*slide_ek_mask[:,1,None])
                three_d_bincount_add(p_co, edge_keys[:,0], q_co[edge_keys[:,1]]*edge_weights[:,None]*slide_ek_mask[:,0,None])

                p_co =q_co + (p_co / sum_edge_len_per_vert[:,None] - q_co )/ v_connections[:,None]   #new aver posision
                where_are_NaNs = np.isnan(p_co) # nan on corner case - where border and shapr edges meet vert. Just use old co there
                p_co[where_are_NaNs]= q_co[where_are_NaNs]

                #average normals an normalize
                three_d_bincount_add(p_normal, edge_keys[:,1], q_normal[edge_keys[:,1]])
                three_d_bincount_add(p_normal, edge_keys[:,0], q_normal[edge_keys[:,0]])

                p_normal_magnitudes = np.sqrt(np.einsum('...i,...i', p_normal, p_normal))
                p_normal /= p_normal_magnitudes[:,None] # total_normal.normalize()
                #npy dot product:  np.einsum('ij,ij->i',p_normal,new_co_dif)
                # vec list * scalar list => np.einsum('ij,i->ij',p_normal,scalarList)
                new_co_dif = p_co - q_co #to get diff between new and old position -> we will use it to determine size of vert movement along normal

                #p_normal[i].dot(new_co_dif[i])
                diff_projected_on_normal_scalar_li = np.einsum('ij,ij->i',p_normal,new_co_dif)  #normal has to be normlized
                aver_normal_scalar = np.sum(diff_projected_on_normal_scalar_li[sel_verts])/np.sum(sel_verts)

                # projected_diff_on_normal = total_normal* total_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                projected_diff_on_normal = np.einsum('ij,i->ij',p_normal, diff_projected_on_normal_scalar_li*(1-self.normal_smooth) +self.normal_smooth* aver_normal_scalar)

                p_co =  p_co  - projected_diff_on_normal* self.Inflate   #new aver normal
                # p_co =  p_co  + p_normal * self.Inflate   #new aver normal
                p_co[freeze_verts] = q_co[freeze_verts] # not selected ver - reset to original pos o_co

                if vg_mask is not None: # float  (0, 1) range mask. Use to blend between smooth and non smooth
                    p_co = vg_mask[:,None] * p_co + (1-vg_mask[:,None]) * q_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0
                    p_normal[mirror_mask, axis_id] = 0

            if self.smooth_amount<1:
                p_co = self.smooth_amount*p_co + (1-self.smooth_amount)*o_co

        if method == 'LC':
            calc_lc_numpy_smooth()
        elif method == 'INFlATE':
            inflate_numpy_smooth()
        elif method == 'VOL':
            vol_numpy_smooth()

        # source.vertices.foreach_set('co', p_co.ravel())
        if from_brush:
            self.bm = bm
            new_co = np.array([p_co[orig_to_new_idx[v.index]] for v in sel_v], 'f')
            orig_co = np.array([o_co[orig_to_new_idx[v.index]] for v in sel_v], 'f')
            self.o_normal = np.array([o_normal[orig_to_new_idx[v.index]] for v in sel_v], 'f') #for sliding only in brush mode
            self.o_normal = np.array([o_normal[orig_to_new_idx[v.index]] for v in sel_v], 'f') #for sliding only in brush mode
            self.freeze_verts = np.array([freeze_verts [orig_to_new_idx[v.index]] for v in sel_v], 'bool') #for sliding only in brush mode freeze_verts

            self.p_co = new_co
            self.o_co = orig_co
            self.sel_v = sel_v
            self.orig_to_new_idx = orig_to_new_idx

            remapped_mirror_v_mask = {}  #from sub sel vert group + adj geo verts,  to original verts (only selected) ids
            for axis_id, mirror_mask in on_axis_vmask.items():
                remapped_mirror_v_mask[axis_id] = np.array([mirror_mask[orig_to_new_idx[v.index]] for v in sel_v], 'bool')
            self.on_axis_vmask = remapped_mirror_v_mask
        else:
            for v in sel_v:
                if bpy.context.object.data.use_mirror_x:
                    mirror_vert_idx = self.mirror_map[v.index]
                    if mirror_vert_idx >= 0:
                        bm.verts[mirror_vert_idx].co = p_co[orig_to_new_idx[v.index]]
                        bm.verts[mirror_vert_idx].co.x *= -1
                v.co = p_co[orig_to_new_idx[v.index]]
            # source.update()
            close_bmesh(context, bm, context.active_object.data)
        # print('Laplacian numpy smooth took: '+ str(time.time()-startTime)+' sec')
        # bpy.ops.object.mode_set(mode = mode)

    def calc_numpy_smooth(self, context):
        pass

