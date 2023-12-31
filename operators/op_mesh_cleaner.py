import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from .. utils.tools import flattened, is_bmvert_collinear


class BDSM_Mesh_Clean(Operator):
    bl_idname = 'view3d.bdsm_mesh_clean'
    bl_label = 'BDSM Mesh Clean'
    bl_description = 'BDSM Mesh Clean\n'\
                    'All the important cleaning operations in one click. Select or Clean.\n' \
                    'Note: Object mode (also multiple objects). Scale will be applied.'
    bl_options = {'REGISTER', 'UNDO'}

    select_only: BoolProperty(default=True, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.select_get() and context.object.type == 'MESH')

    def execute(self, context):
        props = context.window_manager.BDSM_Context
        # props
        doubles = props.clean_doubles
        doubles_val = props.clean_doubles_val
        loose = props.clean_loose
        interior = props.clean_interior
        degenerate = props.clean_degenerate
        collinear = props.clean_collinear
        tinyedges = props.clean_tinyedge
        tinyedges_val = props.clean_tinyedge_val
        tv = 3.1415 - (props.clean_collinear_val * 0.0031415)

        # PRESELECTION
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            return {"CANCELLED"}

        report = {}
        mes_found = ""

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')

        for o in sel_obj:
            # SELECT
            o.select_set(state=True)
            context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.mode_set(mode="EDIT")

            sel_count = 0
            precount = int(len(o.data.vertices))

            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_mode(type='VERT')

            bm_select = []
            bm_dissolve = []
            bm_delete = []
            mes = []

            if interior:
                bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_multi_face=True,
                                                 use_non_contiguous=True, use_verts=True, use_boundary=False)
                sel_count += len([v for v in o.data.vertices if v.select])
                if not self.select_only:
                    bpy.ops.mesh.delete(type='FACE')

            # And the rest in BMesh
            me = o.data
            bm = bmesh.from_edit_mesh(me)

            if doubles:
                result = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=doubles_val)
                verts = [i for i in result['targetmap'] if isinstance(i, bmesh.types.BMVert)]
                bm_select.extend(verts)
                if not self.select_only:
                    bmesh.ops.weld_verts(bm, targetmap=result['targetmap'])
                    bm.verts.ensure_lookup_table()

            if loose:
                lv = [v for v in bm.verts if len(v.link_edges) <= 1]
                bm_select.extend(lv)
                bm_dissolve.extend(lv)

            if degenerate:
                de = flattened([e.verts for e in bm.edges if e.calc_length() < doubles_val])
                df = flattened([f.verts for f in bm.faces if f.calc_area() < doubles_val])
                dv = list(set(de + df))
                bm_select.extend(dv)
                if not self.select_only and dv:
                    result = bmesh.ops.find_doubles(bm, verts=dv, dist=doubles_val)
                    verts = [i for i in result['targetmap'] if isinstance(i, bmesh.types.BMVert)]
                    if verts:
                        bmesh.ops.weld_verts(bm, targetmap=result['targetmap'])
                        bm.verts.ensure_lookup_table()
                    else:
                        bm_delete.extend(dv)

            if collinear:
                cvs = [v for v in bm.verts if is_bmvert_collinear(v, tolerance=tv)]
                bm_select.extend(cvs)
                bm_dissolve.extend(cvs)

            if tinyedges:
                mes = flattened([e.verts for e in bm.edges if e.calc_length() < tinyedges_val])
                bm_select.extend(mes)

            # PROCESS
            if not self.select_only:
                bm_dissolve = list(set(bm_dissolve))
                bmesh.ops.dissolve_verts(bm, verts=bm_dissolve)

                bm_delete = [v for v in bm_delete if v.is_valid]
                bm_delete = list(set(bm_delete))
                bmesh.ops.delete(bm, geom=bm_delete)
                if tinyedges:
                    mes = [v for v in mes if v.is_valid]
                    if len(mes) > 1:
                        mes_found = "-Tiny Edges (sel only) Found & Selected!-"
                        for v in mes:
                            v.select_set(True)
                bmesh.update_edit_mesh(me)
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bm_select = list(set(bm_select))
                for v in bm_select:
                    v.select_set(True)
                bmesh.update_edit_mesh(me)
                bpy.ops.object.mode_set(mode="EDIT")

            # TALLY
            sel_count += len(bm_select)
            postcount = int(len(o.data.vertices))
            vert_count = precount - postcount
            if vert_count > 0:
                self.report("Removed %s verts from %s" % ((precount - postcount), o.name))
                report[o.name] = vert_count
            if sel_count > 0:
                self.report("Found %s verts in %s" % (sel_count, o.name))
                report[o.name] = sel_count

            o.select_set(state=False)

        for o in sel_obj:
            o.select_set(state=True)

        # bpy.ops.object.mode_set(mode=og_mode)
        if report:
            tot = "Total: " + str(sum(report.values()))
            final_report = str(report)
            if len(final_report) > 64:
                final_report = final_report[:62] + "..."
            if mes_found:
                tot = mes_found + tot
            self.report({"INFO"}, "%s, %s" % (tot, final_report))
        else:
            self.report({"INFO"}, "All Good!")

        return {"FINISHED"}


class BDSM_Mesh_Clean_Purge(Operator):
    bl_idname = 'view3d.bdsm_mesh_clean_purge'
    bl_label = 'BDSM Mesh Clean Purge'
    bl_description = 'BDSM Mesh Clean Purge\n'\
                    'Purge specific unused data blocks\n' \
                    'Note: Deleted meshes will still use materials: Purge meshes first'
    bl_options = {'REGISTER', 'UNDO'}

    block_type: EnumProperty(
        items=[('MESH', 'Mesh', '', 1),
               ('MATERIAL', 'Materials', '', 2),
               ('TEXTURE', 'Textures', '', 3),
               ('IMAGE', 'Images', '', 4)],
        name='Purge Data',
        default='MATERIAL')

    def execute(self, context):
        if self.block_type == 'MESH':
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)
        elif self.block_type == 'MATERIAL':
            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)
        elif self.block_type == 'TEXTURE':
            for block in bpy.data.textures:
                if block.users == 0:
                    bpy.data.textures.remove(block)
        elif self.block_type == 'IMAGE':
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)

        return {'FINISHED'}


