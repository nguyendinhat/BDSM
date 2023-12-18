import bpy,bmesh
from bpy.types import Operator
from ..utils.ngons import *


class BDSM_Mesh_Fix_Ngons(Operator):
    bl_idname = 'mesh.bdsm_mesh_face_fix_ngons'
    bl_label = 'BDSM Mesh Face Fix Ngons'
    bl_description = 'BDSM Mesh Face Fix Ngons\nFixes ngons that surround selection'
    bl_options = {'REGISTER', 'UNDO'}

    coverage_mode: bpy.props.EnumProperty(
        name='Coverage mode',
        description='What to fix',
        items=[
            ('selection', 'Only faces within selection', 'If all verts of a face are selected, they will be turned into quads (no need for all of the edges of the faces to be selected)'),
            ('relevant', 'Also faces around selection', 'Selection and the faces around it will all be turned into quads (a single selected vert is enough to quad a face)'),
            ('all', 'All', 'Everything will be turned into quads (hopefully)')
        ],
        default='selection'
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

    fix_mode: bpy.props.EnumProperty(
        name='Fixing ngons mode',
        description='The method for use when getting rid of ngons',
        items=[
            ('fast', 'Fast', 'Fast method can often introduce a triangle in place of a perfectly fitting quad'),
            ('precise', 'Precise', 'REQUIRES LOOPS SELECTION - NO FULL FACES ALLOWED! Much slower than fast but more likely to produce better results in terms of subdivision into quads - quads not guaranteed'),
            ('quads', 'Quads', 'Slower than precise but the best in terms of creating quads. Much better results if faces resemble quads (4 distinctive corners) but should work with any geometry. This will often create additional topology')
        ],
        default='quads'
    )

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
        if self.coverage_mode == 'selection':
            relevant_faces = [f for f in get_relevant_faces(bm, selected_verts_indices) if all([v.index in selected_verts_indices for v in f.verts])]
        elif self.coverage_mode == 'relevant':
            relevant_faces = get_relevant_faces(bm, selected_verts_indices)
        elif self.coverage_mode == 'all':
            relevant_faces = [f for f in bm.faces]
        relevant_faces = [f for f in relevant_faces if len(f.verts) <= max(5, self.max_verts)]

        if len(relevant_faces) < 1:
            show_message('No ngons selected.')
            free_bmesh(obj, bm)
            return {'FINISHED'}

        if self.fix_mode == 'fast':
            bmesh.ops.connect_verts_concave(bm, faces=relevant_faces)
        elif self.fix_mode == 'quads':
            FixNgonsRecursively(bm, relevant_faces, self.max_recursion_depth)
        elif self.fix_mode == 'precise':
            try:
                grouped_loops = group_loops(get_separated_sorted_loops(selected_edges), relevant_faces)
                possible = possible_edges(grouped_loops, relevant_faces)
                v_edges = viable_edges(bm, possible)
            except:
                show_message('Invalid selection (only edges, no full faces allowed) for precise fixing mode!')
                free_bmesh(obj, bm)
                return {'FINISHED'}

            for x in v_edges:
                for e in x:
                    bmesh.ops.connect_verts(bm, verts=(bm.verts[e[0]], bm.verts[e[1]]), check_degenerate=True)


        update_bmesh(obj, bm)
        free_bmesh(obj, bm)

        return {'FINISHED'}
