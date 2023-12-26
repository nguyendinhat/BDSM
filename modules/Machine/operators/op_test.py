import bpy, bmesh
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils.geometry import  intersect_line_plane, normal

from ...Machine.context.items import mode_items
from ....interface.hud import draw_init, draw_title, draw_prop, init_cursor, init_status, finish_status, update_HUD_location
from ....interface.draw import draw_lines, draw_point, draw_points, draw_vector
from ..utils.property import step_enum
from ..utils.developer import output_traceback
from ..utils.math import average_locations


class BDSM_DrawTest(Operator):
    bl_idname = "view3d.bdsm_draw_test"
    bl_label = "BDSM Draw Test"
    bl_description = "BDSM Draw Test"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=mode_items,
        default="EDGE"
    )
    dissolve: BoolProperty(
        name="Dissolve",
        default=True
    )
    face_mode: BoolProperty(name="Face Mode", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        row = column.row()
        row.prop(self, "mode", expand=True)
        if self.face_mode:
            column.prop(self, "dissolve")

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)
            subtitle = "Subtitle" if self.face_mode else "Mode 2"
            draw_title(self, "Title", subtitle=subtitle, subtitleoffset=125)
            draw_prop(self, "Mode", self.mode, hint="scroll UP/DOWN")
            if self.face_mode:
                draw_prop(self, "Dissolve", self.dissolve, offset=18, hint="toggle D")

    def draw_DEBUG(self, context):
        if context.scene.MM.debug and self.coords:
            draw_lines(self.coords, mx=self.active.matrix_world, color=(0.5, 0.5, 1) if self.flatten_mode == "NORMAL" else (0.1, 0.4, 1))
            draw_points([self.coords[idx] for idx in range(0, len(self.coords), 2)], mx=self.active.matrix_world)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def invoke(self, context, event):
        self.active = context.active_object
        self.active.update_from_editmode()
        self.coords = []
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        #todo: Return HUDx, HUDy
        init_cursor(self, event)
        try:
            self.ret = self.main(self.active, modal=True)
            if not self.ret:
                self.cancel_modal(removeHUD=False)
                return {'FINISHED'}
        except Exception as e:
            if bpy.context.mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='EDIT')
            output_traceback(self, e)
            return {'FINISHED'}
        init_status(self, context, 'Flatten')
        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context, ), 'WINDOW', 'POST_PIXEL')
        self.DEBUG = bpy.types.SpaceView3D.draw_handler_add(self.draw_DEBUG, (context, ), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'MOUSEMOVE':
            update_HUD_location(self, event)

        events = ['WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'ONE', 'TWO', 'D']
        if event.type in events:
            if event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                self.mode = step_enum(self.mode, mode_items, 1)
            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                self.mode = step_enum(self.mode, mode_items, -1)
            elif event.type == 'D' and event.value == "PRESS":
                self.dissolve = not self.dissolve
            try:
                ret = self.main(self.active, modal=True)
                if ret is False:
                    self.finish()
                    return {'FINISHED'}
            except Exception as e:
                self.finish()
                output_traceback(self, e)
                return {'FINISHED'}
        #todo: Pass event
        elif event.type in {'MIDDLEMOUSE'} or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        #todo: Confirm
        elif event.type in ['LEFTMOUSE', 'SPACE']:
            self.finish()
            return {'FINISHED'}
        #todo: Quit Modal
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


    def execute(self, context):
        active = context.active_object
        try:
            self.main(active)
        except Exception as e:
            output_traceback(self, e)
        return {'FINISHED'}

    def main(self, active, modal=False):
        debug = False

        bpy.ops.object.mode_set(mode='OBJECT')
        if modal:
            self.initbm.to_mesh(active.data)

        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]
        faces = [f for f in bm.faces if f.select]

        if len(faces) > 1:
            self.face_mode = True
            self.coords = flatten_faces(bm, edges, self.mode, self.dissolve, debug=debug)
        else:
            self.face_mode = False
            self.coords = flatten_verts(bm, verts, self.mode, debug=debug)

        bm.normal_update()
        bm.to_mesh(active.data)

        bpy.ops.object.mode_set(mode='EDIT')
        return True

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            self.finish()

        bpy.ops.object.mode_set(mode='OBJECT')
        self.initbm.to_mesh(self.active.data)
        bpy.ops.object.mode_set(mode='EDIT')

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self.DEBUG, 'WINDOW')
        finish_status(self)


#excute func

def flatten_verts(bm, verts, flatten_mode, debug=False):
    face = [f for v in verts for f in v.link_faces if f in verts[0].link_faces and f in verts[1].link_faces and f in verts[2].link_faces][0]

    flat_verts = [v for v in face.verts if v not in verts]

    if debug:
        print("face:", face.index)
        print("flat verts:", [v.index for v in flat_verts])

    nrm = normal(verts[0].co, verts[1].co, verts[2].co)

    if debug:
        mx = bpy.context.active_object.matrix_world
        midpoint = average_locations([v.co for v in verts])
        draw_vector(nrm, origin=midpoint, mx=mx, color=(0.5, 0.5, 1), modal=False)

    initial_coords = [v.co.copy() for v in face.verts if v not in verts]

    if flatten_mode == 'EDGE':

        vert_pairs = [(v, e.other_vert(v).co.copy()) for v in face.verts if v not in verts for e in v.link_edges if e not in face.edges]

        if debug:
            draw_points([v.co.copy() for v, _ in vert_pairs], mx=mx, color=(0, 1, 0), modal=False)
            draw_points([co for _, co in vert_pairs], mx=mx, color=(0.2, 0.5, 1), modal=False)

        flattened_coords = flatten_along_edges(vert_pairs, verts[0].co, nrm, debug=debug)

    else:
        flattened_coords = flatten_along_normal(bm, flat_verts, verts[0].co, nrm, debug=debug)

    coords = []
    for ico, fco in zip(initial_coords, flattened_coords):
        coords.extend([ico, fco])

    return coords

def flatten_faces(bm, edges, flatten_mode, dissolve=True, debug=False):
    flat = bm.faces.active
    faces = [f for f in bm.faces if f.select and f != flat]

    if debug:
        print()

    if debug:
        print("    flat:", flat.index)
        print("selected:", [f.index for f in faces])

        mx = bpy.context.active_object.matrix_world
        draw_vector(flat.normal.copy(), origin=flat.calc_center_median(), mx=mx, color=(0.5, 0.5, 1), modal=False)

    verts = {v for f in faces for v in f.verts if v not in flat.verts}

    if debug:
        print("verts to flatten:", [v.index for v in verts])

    if flatten_mode == 'EDGE':
        vert_pairs = [(v, e.other_vert(v).co.copy()) for v in verts for e in v.link_edges if e not in edges]

        initial_coords = [v.co.copy() for v, _ in vert_pairs]

    else:

        initial_coords = [v.co.copy() for v in verts]

    if flatten_mode == "EDGE":
        flattened_coords = flatten_along_edges(vert_pairs, flat.verts[0].co, flat.normal, debug=debug)

    elif flatten_mode == "NORMAL":
        flattened_coords = flatten_along_normal(bm, verts, flat.verts[0].co, flat.normal, debug=debug)

    coords = []

    for ico, fco in zip(initial_coords, flattened_coords):
        coords.extend([ico, fco])

    if dissolve:

        geo = bmesh.ops.dissolve_faces(bm, faces=faces + [flat])

        if geo['region']:
            newface = geo['region'][0]
            newface.select = True

    return coords

def flatten_along_edges(vert_pairs, plane_co, plane_normal, debug=False):
    coords = []

    for v, co in vert_pairs:
        ico = intersect_line_plane(v.co, co, plane_co, plane_normal)

        if ico:
            v.co = ico

            if debug:
                mx = bpy.context.active_object.matrix_world
                draw_point(ico, mx=mx, color=(1, 1, 1), modal=False)

            coords.append(ico)

    return coords

def flatten_along_normal(bm, verts, plane_co, plane_normal, debug=False):
    coords = []

    for v in verts:
        perpco = v.co + plane_normal

        if debug:
            mx = bpy.context.active_object.matrix_world
            draw_vector(plane_normal.copy(), origin=v.co.copy(), mx=mx, color=(0.5, 0.5, 1), modal=False)

        ico = intersect_line_plane(v.co, perpco, plane_co, plane_normal)

        if ico:
            v.co = ico

            coords.append(ico)

    return coords
