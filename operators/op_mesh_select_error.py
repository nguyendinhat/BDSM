import bmesh
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from mathutils import kdtree
import numpy as np

from .. utils.tools import is_bmvert_collinear, average_vector, mesh_world_coords, mesh_select_all, mesh_hide_all, dupe, shred


class BDSM_Mesh_Select_Vert_Collinear(Operator):
    bl_idname = "mesh.bdsm_mesh_select_vert_collinear"
    bl_label = "BDSM Mesh Select Vert Collinear"
    bl_description = "BDSM Mesh Select Vert Collinear"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        props = context.window_manager.BDSM_Context
        tv = 3.1415 - (props.clean_collinear_val * 0.0031415)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        obj = context.active_object
        if not obj:
            obj = sel_obj[0]

        og_mode = [b for b in context.tool_settings.mesh_select_mode]
        context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='DESELECT')

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.select_mode = {'VERT'}

        count = 0
        for v in bm.verts:
            if is_bmvert_collinear(v, tolerance=tv):
                v.select = True
                count += 1

        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)

        if count > 0:
            self.report({"INFO"}, "Total Collinear Verts Found: %s" % count)
        else:
            context.tool_settings.mesh_select_mode = og_mode
            self.report({"INFO"}, "No Collinear Verts Found")

        return {"FINISHED"}

class BDSM_Mesh_Select_Flip_Normal(Operator):
    bl_idname = "mesh.bdsm_mesh_select_flip_normal"
    bl_label = "BDSM Mesh Select Flip Normal"
    bl_description = 'BDSM Mesh Select Flip Normal\n'\
                    "Selects flipped normal faces (the 'red' faces in 'face orientation' overlay)"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        items=[("CONNECTED", "Connected", "", 1),
               ("AVERAGE", "Average", "", 2)
               ],
        name="Method", 
        default="CONNECTED",
        description="Choose which method used to find flipped faces.\n"
                    "Average works better for (mostly flat) disconnected mesh islands.\n"
                    "Connected works best in most other cases.")
    invert : BoolProperty(
        name="Invert Selection", 
        default=False
    )

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "mode", expand=True)
        layout.separator(factor=0.5)
        layout.prop(self, "invert", toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        if self.mode == "AVERAGE":
            avg_normal = average_vector([f.normal for f in bm.faces])
            if self.invert:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) > 0:
                        f.select_set(True)
            else:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) < 0:
                        f.select_set(True)
        else:
            cbm = bm.copy()
            bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
            if self.invert:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal == of.normal:
                        of.select_set(True)
            else:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal != of.normal:
                        of.select_set(True)
            cbm.free()
        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}

class BDSM_Mesh_Select_Snapping(Operator):
    bl_idname = "view3d.bdsm_mesh_select_snapping"
    bl_label = "BDSM Mesh Select Snapping"
    bl_description = "BDSM Mesh Select Snapping\n"\
                    "Selects (2+) mesh objects verts that (are supposed to) share coords (='Snapped')"
    bl_options = {'REGISTER', 'UNDO'}

    epsilon : FloatProperty(
        precision=6,
        min=0.000001,
        default=0.00001,
        name="Threshold",
        description="Distance tolerance for coordinates (or floating point rounding)"
    )

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.selected_objects)

    def execute(self, context):
        # CHECK MESH
        if len(context.selected_objects) < 2 or any([o for o in context.selected_objects if o.type != "MESH"]):
            self.report({"ERROR"}, "Select at least 2 Mesh Objects!")
            return {"CANCELLED"}

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # GET 'OBJECT AND COORDS' LOOP PAIRS
        oac = []
        for obj in context.selected_objects:
            wcos = mesh_world_coords(obj)
            oac.append([obj, wcos])
            mesh_select_all(obj, False)

        # FIND MATCHING CO'S
        for obj, coords in oac:
            # SETUP K-DIMENSIONAL TREE SPACE-PARTITIONING DATA STRUCTURE
            cmp_co = np.concatenate([i[1] for i in oac if i[0].name != obj.name])
            size = len(cmp_co)
            kd = kdtree.KDTree(size)
            for i, v in enumerate(cmp_co):
                kd.insert(v, i)
            kd.balance()

            # FIND MATCHING CO'S IN K-D TREE & SELECT
            sel_mask = [bool(kd.find_range(co, self.epsilon)) for co in coords]
            obj.data.vertices.foreach_set("select", sel_mask)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        return {"FINISHED"}

class BDSM_Mesh_Select_Vert_Occluded(Operator):
    bl_idname = "view3d.bdsm_mesh_select_vert_occluded"
    bl_label = "BDSM Mesh Select Vert Occluded"
    bl_description = "BDSM Mesh Select Vert Occluded\n"\
                    "Selects verts of selected object(s) that are occluded ('inside') the Active Object"
    bl_options = {'REGISTER', 'UNDO'}

    epsilon = 0.0001
    surface_offset = -0.001

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.object is not None and
                context.mode == "OBJECT")

    def execute(self, context):
        # CHECK MESH
        if len(context.selected_objects) < 2 or any([o for o in context.selected_objects if o.type != "MESH"]):
            self.report({"ERROR"}, "Select at least 2 Mesh Objects!")
            return {"CANCELLED"}

        # PREP OBJECTS & SELECTIONS
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

        og_active = context.object
        og_sel_obj = [o for o in context.selected_objects if o != og_active]

        for o in context.selected_objects:
            o.select_set(False)

        # TEMP-BOOL OCCLUDED INTERSECTION MESH & USE TO FIND MATCHING CO'S
        for obj in og_sel_obj:
            # CREATE TEMP DUPES FOR BOOLEAN
            o = dupe(obj)
            active = dupe(og_active)

            # SET SELECTIONS
            o.select_set(True)
            mesh_select_all(o, True)
            mesh_hide_all(o, False)
            context.view_layer.objects.active = active
            override = {'object': active}

            # SHRINK / ON-SURFACE OFFSET
            mod = active.modifiers.new("KeTempDisp", "DISPLACE")
            mod.show_viewport = False
            mod.strength = self.surface_offset
            with bpy.context.temp_override(**override):
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # INTERSECTION BOOLEAN
            mod = active.modifiers.new("KeTempBool", "BOOLEAN")
            mod.show_viewport = False
            mod.operation = "INTERSECT"
            mod.solver = 'EXACT'
            # mod.use_hole_tolerant = True
            mod.object = o
            with bpy.context.temp_override(**override):
                bpy.ops.object.modifier_apply(modifier=mod.name)

            # FIND MATCHING CO'S
            imesh = context.object

            if len(imesh.data.vertices) != 0:
                mesh_select_all(obj, False)
                obj_cos = mesh_world_coords(obj)
                imesh_cos = mesh_world_coords(imesh)

                # SETUP K-DIMENSIONAL TREE SPACE-PARTITIONING DATA STRUCTURE
                size = len(imesh_cos)
                kd = kdtree.KDTree(size)
                for i, v in enumerate(imesh_cos):
                    kd.insert(v, i)
                kd.balance()

                # FIND MATCHING CO'S IN K-D TREE & SELECT VERTS
                sel_mask = [bool(kd.find_range(co, self.epsilon)) for co in obj_cos]
                obj.data.vertices.foreach_set("select", sel_mask)

            else:
                self.report({"ERROR"}, "%s - Failed to boolean intersection mesh!" % obj.name)

            # CLEANUP TEMP MESH
            shred(imesh)
            shred(o)

        # FINALIZE
        for o in og_sel_obj:
            o.select_set(True)

        context.view_layer.objects.active = og_sel_obj[0]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        return {"FINISHED"}

class BDSM_Mesh_Select_Vert_Counter(Operator):
    bl_idname = "view3d.bdsm_mesh_select_vert_counter"
    bl_label = "BDSM Mesh Select Vert Counter"
    bl_description = "BDSM Mesh Select Vert Counter \nSelect geo by vert count in selected Object(s) in Edit or Object Mode. (Note: Ngons are 5+)"
    bl_options = {'REGISTER', 'UNDO'}

    sel_count: EnumProperty(
        items=[("0", "Loose Vert", "", 1),
               ("1", "Loose Edge", "", 2),
               ("2", "2 Edges", "", 3),
               ("3", "Tri", "", 4),
               ("4", "Quad", "", 5),
               ("5", "Ngon", "", 6)],
        name="Select Geo by Vert Count",
        default="3")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        nr = int(self.sel_count)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]

        if not sel_obj:
            self.report({"INFO"}, "Object must be selected!")
            return {"CANCELLED"}

        if context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

        for o in sel_obj:
            me = o.data
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()
            selection = []

            if nr <= 2:
                bm.select_mode = {'VERT'}
                for v in bm.verts:
                    le = len(v.link_edges)
                    if le == nr:
                        selection.append(v)

            elif nr >= 3:
                bm.select_mode = {'FACE'}
                for p in bm.faces:
                    pv = len(p.verts)
                    if nr == 5 and pv >= nr:
                        selection.append(p)
                    elif pv == nr:
                        selection.append(p)

            if selection:
                for v in selection:
                    v.select = True

            bm.select_flush_mode()
            bmesh.update_edit_mesh(o.data)

        if nr >= 3:
            context.tool_settings.mesh_select_mode = (False, False, True)
        else:
            context.tool_settings.mesh_select_mode = (True, False, False)

        return {'FINISHED'}



