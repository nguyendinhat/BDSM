import bpy, bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector
from .. utils import tools

class BDSM_Mesh_Merge_Mouse(Operator):
    bl_idname = 'mesh.bdsm_mesh_merge_mouse'
    bl_label = 'BDSM Mesh Merge Mouse'
    bl_description = 'BDSM Mesh Merge Mouse'
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]

        # IDC...maybe later
        areatype = tools.get_area_and_type()[1]
        if areatype == 'QUAD':
            bpy.ops.mesh.merge(type='LAST')
            return {'FINISHED'}

        obj = context.object
        obj_mtx = obj.matrix_world.copy()
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        skip_linked = False

        # Sel check
        sel_verts = [v for v in bm.verts if v.select]
        if not sel_verts:
            print('Cancelled: Nothing Selected')
            return {'CANCELLED'}

        if sel_mode[1]:
            sel_edges = [e for e in bm.edges if e.select]

            if len(sel_edges) > 1:
                sedges = tools.vertloops([e.verts for e in sel_edges])
                start_line = []

                close_vert_candidate = tools.get_vert_nearest_mouse(context, self.mouse_pos, sel_verts, obj_mtx)
                for line in sedges:
                    if close_vert_candidate in line:
                        start_line = line

                if not start_line:
                    print('Cancelled: Target Edge Loop not found')
                    return {'CANCELLED'}

                le = []
                for v in sel_verts:
                    for e in v.link_edges:
                        if all(i in sel_verts for i in e.verts) and e not in sel_edges:
                            # Brute linkvert back & forth to cover Triangulation
                            skip = []
                            ce = []
                            for edge in sel_edges:
                                if v in edge.verts:
                                    ce = edge
                                    break
                            ov = e.other_vert(v)
                            skipmatch = [i for i in ce.verts if i != v]
                            for ove in ov.link_edges:
                                rov = ove.other_vert(ov)
                                if rov in skipmatch:
                                    skip.append(e)

                            if e not in skip:
                                le.append(e)

                collapse_rows = tools.vertloops([e.verts for e in list(set(le))])

                for row in collapse_rows:
                    target = [i for i in row if i in start_line][0]
                    if not target:
                        target = row[0]
                    bmesh.ops.pointmerge(bm, verts=row, merge_co=target.co)
                    bmesh.update_edit_mesh(mesh)

                mesh.update()
                # trust blender to update the mesh w/o issue? nah ;P
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')

        else:
            context.tool_settings.mesh_select_mode = (True, False, False)
            if skip_linked:
                verts = sel_verts
            else:
                verts = []
                for v in sel_verts:
                    for e in v.link_edges:
                        verts.append(e.other_vert(v))

                verts += sel_verts
                verts = list(set(verts))

            merge_point = tools.get_vert_nearest_mouse(context, self.mouse_pos, verts, obj_mtx)

            if merge_point:
                if merge_point not in sel_verts:
                    sel_verts.append(merge_point)
                bmesh.ops.pointmerge(bm, verts=sel_verts, merge_co=merge_point.co)
                bm.select_flush_mode()
                bmesh.update_edit_mesh(obj.data)

            context.tool_settings.mesh_select_mode = (sel_mode[0], sel_mode[1], sel_mode[2])

        return {'FINISHED'}

class BDSM_Mesh_Merge_Active(Operator):
    bl_idname = 'mesh.bdsm_mesh_merge_active'
    bl_label = 'BDSM Mesh Merge Active'
    bl_description = 'BDSM Mesh Merge Active'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        # Sel check
        sel_verts = [v for v in bm.verts if v.select]
        if not sel_verts:
            print('Cancelled: Nothing Selected')
            return {'CANCELLED'}

        if sel_mode[1]:
            sel_edges = [e for e in bm.edges if e.select]

            if len(sel_edges) > 1:
                sh = bm.select_history.active
                ae = sh if sh in sel_edges else []
                if not ae:
                    print('Cancelled: Active Edge not found in selection')
                    return {'CANCELLED'}

                sedges = tools.vertloops([e.verts for e in sel_edges])
                start_line = []
                for line in sedges:
                    if ae.verts[0] in line:
                        start_line = line
                        break

                if not start_line:
                    print('Cancelled: Target Edge Loop not found')
                    return {'CANCELLED'}

                le = []
                for v in sel_verts:
                    for e in v.link_edges:
                        if all(i in sel_verts for i in e.verts) and e not in sel_edges:
                            # Brute linkvert back & forth to cover Triangulation
                            skip = []
                            ce = []
                            for edge in sel_edges:
                                if v in edge.verts:
                                    ce = edge
                                    break
                            ov = e.other_vert(v)
                            skipmatch = [i for i in ce.verts if i != v]
                            for ove in ov.link_edges:
                                rov = ove.other_vert(ov)
                                if rov in skipmatch:
                                    skip.append(e)

                            if e not in skip:
                                le.append(e)

                collapse_rows = tools.vertloops([e.verts for e in list(set(le))])

                for row in collapse_rows:
                    target = [i for i in row if i in start_line][0]
                    if not target:
                        target = row[0]
                    bmesh.ops.pointmerge(bm, verts=row, merge_co=target.co)
                    bmesh.update_edit_mesh(mesh)

                mesh.update()
                # still don't trust blender to update the mesh w/o issue? toggle! ;P
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')

        else:
            # Vert mode
            sh = bm.select_history.active
            ae = sh if sh in sel_verts else []
            if ae:
                bpy.ops.mesh.merge('INVOKE_DEFAULT', type='LAST')
            else:
                bpy.ops.mesh.merge('INVOKE_DEFAULT', type='COLLAPSE')

        return {'FINISHED'}

class BDSM_Mesh_Merge_NearSelected(Operator):
    bl_idname = 'mesh.bdsm_mesh_merge_nearselected'
    bl_label = 'BDSM Mesh Merge Near Selected'
    bl_description = 'BDSM Mesh Merge Near Selected'
    bl_options = {'REGISTER', 'UNDO'}

    distance: FloatProperty(min=0, max=99, default=0.01, name='Distance', step=0.001, precision=5,
                            description='Distance from each vert to merge linked verts from')
    link_level: IntProperty(min=1, max=99, default=1, name='Link Level',
                            description='The # of edge links away from each vert to process distance on')

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        if context.object.scale != Vector((1.0, 1.0, 1.0)):
            self.report({'INFO'}, 'Scale is not applied - Results may be unpredictable')

        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        sel_verts = [v for v in bm.verts if v.select]

        if not sel_verts:
            self.report({'INFO'}, 'No elements selected?')
            return {'CANCELLED'}

        # 1/2 - Get linked verts and merge them at sel_vert co - except the sel_vert, avoiding dead index nonsense
        # todo: make less crazy brutal for-loop process? Nah...
        for v in sel_verts:
            mergeverts = [v]

            for i in range(0, self.link_level):
                lvs = []

                for linkvert in mergeverts:
                    for e in linkvert.link_edges:
                        ov = e.other_vert(linkvert)
                        d = tools.get_distance(v.co, ov.co)

                        if d < self.distance:
                            other_edgevert_closer = False
                            # Check if any other sel_vert is closer 1st
                            for ole in ov.link_edges:
                                olev = ole.other_vert(ov)
                                if olev in sel_verts and olev != ov:
                                    od = tools.get_distance(olev.co, ov.co)
                                    if od < d:
                                        other_edgevert_closer = True
                                        break

                            if not other_edgevert_closer:
                                lvs.append(ov)
                            else:
                                break

                    lvs = list(set(lvs))
                mergeverts.extend(lvs)

            mergeverts = list(set(mergeverts) - set(sel_verts))
            if mergeverts:
                bmesh.ops.pointmerge(bm, verts=mergeverts, merge_co=v.co[:])

        bmesh.update_edit_mesh(mesh)

        # 2/2 - And then merge the selverts+linked to avoid processing the whole mesh:
        bm.verts.ensure_lookup_table()
        sel_verts = [v for v in bm.verts if v.select]

        linkverts = []
        for v in sel_verts:
            for e in v.link_edges:
                linkverts.extend(e.verts[:])
            linkverts.append(v)
        linkverts = list(set(linkverts))

        md = 0.0001
        if self.distance < md:
            md = self.distance
        bmesh.ops.remove_doubles(bm, verts=linkverts, dist=md)

        bmesh.update_edit_mesh(mesh)
        mesh.update()

        return {'FINISHED'}
