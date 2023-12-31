# This example assumes we have a mesh object in edit-mode

import bpy
import bmesh
from mathutils import Matrix, Vector

from bpy_extras import view3d_utils

from bpy.props import (
        FloatProperty,
        IntProperty,
        BoolProperty,
        EnumProperty,
        )

class BDSM_Mesh_Face_Attach_Align_Slide(bpy.types.Operator):
    bl_idname = "mesh.bdsm_mesh_face_attach_align_slide"
    bl_label = "BDSM Mesh Face Attach Align (Slide)"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    ready = False
    backup = None
    pos = None
    vector = None

    def restore(self):
        bpy.ops.object.editmode_toggle()
        self.backup.to_mesh(bpy.context.object.data)
        bpy.ops.object.editmode_toggle()


    def get_location(self, context, mouse_pos):
        object = context.edit_object
        region = context.region
        region3D = context.space_data.region_3d
        view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, mouse_pos)
        loc = view3d_utils.region_2d_to_location_3d(region, region3D, mouse_pos, view_vector)
        loc = object.matrix_world.inverted() @ loc
        return loc


    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            self.restore()

            delta = (event.mouse_region_x - self.first_x)/100 * self.delta.length
            obj = context.edit_object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            for v in bm.verts:
                if v.select:
                    v.co = v.co + (self.vector * delta)

            bmesh.update_edit_mesh(me)


        elif event.type == 'LEFTMOUSE':
            # we could handle PRESS and RELEASE individually if necessary
            #self.lmb = event.value == 'PRESS'
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            #context.object.location.x = self.first_value
            self.restore()
            self.backup.free()

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def setup_state(self, context):
        obj = context.edit_object
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)

        #bm.faces.active = None
        source = None
        for f1 in bm.edges:
            if f1.select:
                source = f1
                break
        if source == None:
            self.ready = False
            return
        p1 = source.verts[0].co
        p2 = source.verts[1].co
        self.vector = p1 - p2
        bpy.ops.mesh.select_linked()

        bpy.context.object.update_from_editmode()
        self.backup = bmesh.new()
        self.backup.from_mesh(context.object.data)

        self.ready = True


    def invoke(self, context, event):
        # variable to remember left mouse button state
        self.lmb = False

        if context.object:
            #self.first_mouse = self.get_location(context, event)
            testp = self.get_location(context, [0, 0])
            self.delta = self.get_location(context, [100, 100]) - testp
            self.first_x = event.mouse_region_x

            #self.first_mouse_x = event.mouse_region_x
            #self.first_value = context.object.location.x
            self.setup_state(context)
            if self.ready == False:
                return {'CANCELLED'}

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}



def ShowMessageBox(messages = "", title = "Attach Align addon :", icon = 'BLENDER'):
    def draw(self, context):
        for s in messages:
            self.layout.label(text=s)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def vs_midpoint(v1, v2):
    return (v1.co + v2.co)/2

def rotate_vector(v, center, q):
    v2 = v.copy()
    v2 = v2 - center
    v2.rotate(q)
    v2 = v2 + center
    return v2


def move_to_edge(bm, source, target):
    if source == None or target == None:
        return
    moveverts = []
    for v1 in bm.verts:
        if v1.select:
            moveverts.append(v1)

    center = Vector((0.0, 0.0, 0.0))
    for v1 in moveverts:
        center = center + v1.co

    center = center / len(moveverts)
    #print(dir(source.verts[0]))

    sv = source.verts[0].co - source.verts[1].co
    tv = target.verts[0].co - target.verts[1].co

    sv2 = sv * -1

    ro1 = sv.rotation_difference(tv)
    ro2 = sv2.rotation_difference(tv)

    c1 = vs_midpoint(source.verts[0], source.verts[1])
    c2 = vs_midpoint(target.verts[0], target.verts[1])

    result1 = rotate_vector(c1, center, ro1) - c2
    result2 = rotate_vector(c1, center, ro2) - c2
    if result1.length < result2.length:
        ro3 = ro1
    else:
        ro3 = ro2
    #if invert_direction:
    #    sv = sv * -1
    #ro1 = sv.rotation_difference(tv)

    matro = ro3.to_matrix()
    bmesh.ops.rotate(bm, cent=center, matrix=matro, verts=moveverts)



def move_to(bm, source, target):
    if source == None or target == None:
        return
    moveverts = []
    for v1 in bm.verts:
        if v1.select:
            moveverts.append(v1)

    sp = source.calc_center_median()
    tp = target.calc_center_median()

    norm = target.normal * -1
    rodif = source.normal.rotation_difference(norm)
    matro = rodif.to_matrix()

    bmesh.ops.rotate(bm, cent=sp, matrix=matro, verts=moveverts)
    movedif = tp - sp
    bmesh.ops.translate(bm, vec=movedif, verts=moveverts)
    #move_to_edge(bm, source.edges[0], target.edges[0], False)



def compose_mat(loc, rot, sca):
    mloc = Matrix.Translation(loc)
    mrot = rot.to_matrix().to_4x4()
    msca = (Matrix.Scale(sca[0],4,(1,0,0)) @
        Matrix.Scale(sca[1],4,(0,1,0)) @
        Matrix.Scale(sca[2],4,(0,0,1)))
    return mloc @ mrot @ msca


def arrow(pos, normal):
    o = bpy.data.objects.new( "empty", None )
    # due to the new mechanism of "collection"
    bpy.context.scene.collection.objects.link( o )
    # empty_draw was replaced by empty_display
    o.empty_display_size = 2
    o.empty_display_type = 'SINGLE_ARROW'

    q = Vector((0.0, 0.0, 1.0)).rotation_difference(normal)
    mat = q.to_matrix().to_4x4()
    o.matrix_world = mat @ o.matrix_world
    o.matrix_world.translation += pos



def multi_object_attach(context, source, target, p1, p2):
    sm = source.matrix_world
    tm = target.matrix_world
    c1, normal_1 = p1
    c2, normal_2 = p2
    wc1 = sm @ c1
    wc2 = tm @ c2
    wnormal_1 = (sm @ normal_1 - sm @ Vector()).normalized()
    wnormal_2 = (tm @ normal_2 - tm @ Vector()).normalized()

    offset1 = Matrix.Translation(wc1)
    offset1.invert()
    sm2 = offset1 @ sm
    norm = wnormal_2 * -1
    rodif = wnormal_1.rotation_difference(norm)
    romat = rodif.to_matrix().to_4x4()
    sm2 = romat @ sm2
    offset2 = Matrix.Translation(wc2)
    sm2 = offset2 @ sm2
    source.matrix_world = sm2



def multi_object_align(context, source, target, p1, p2):
    sm = source.matrix_world
    tm = target.matrix_world

    center = Vector((0.0, 0.0, 0.0))

    for p in source.bound_box:
        center += Vector(p)

    center = center / len(source.bound_box)
    center = sm @ center

    p1[0] = sm @ p1[0]
    p1[1] = sm @ p1[1]
    p2[0] = tm @ p2[0]
    p2[1] = tm @ p2[1]

    #print(dir(source.verts[0]))

    sv = p1[0] - p1[1]
    tv = p2[0] - p2[1]

    sv2 = sv * -1
    ro1 = sv.rotation_difference(tv)
    ro2 = sv2.rotation_difference(tv)

    c1 = (p1[0] + p1[1])/2
    c2 = (p2[0] + p2[1])/2

    result1 = rotate_vector(c1, center, ro1) - c2
    result2 = rotate_vector(c1, center, ro2) - c2
    if result1.length < result2.length:
        ro3 = ro1
    else:
        ro3 = ro2
    #if invert_direction:
    #    sv = sv * -1
    #ro1 = sv.rotation_difference(tv)

    matro = ro3.to_matrix().to_4x4()
    matcen = Matrix.Translation(center)
    matcen2 = Matrix.Translation(center)
    matcen2.invert()
    sm2 = matcen2 @ sm
    sm2 = matro @ sm2
    sm2 = matcen @ sm2
    source.matrix_world = sm2





def bridge_two(bm, source, target):
    edges1 = [e for e in source.edges]
    edges2 = [e for e in target.edges]
    edges3 = edges1 + edges2
    for e in edges3:
        if edges3.count(e) > 1:
            return

    bmesh.ops.delete(bm, geom=[source, target], context='FACES_ONLY')
    bmesh.ops.bridge_loops(bm, edges=edges3)


def job_move_face(context, connect_geometry):
    obj = context.edit_object

    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)

    #bm.faces.active = None
    selected = []
    for f1 in bm.faces:
        if f1.select:
            selected.append(f1)

    if len(selected) != 2:
        p = ['Thanks for using Attach Align addon!','',
            'Please select two faces, the source and destination.',
            'All conncted faces of source face, will be moved to ',
            'the top of destination face.']
        ShowMessageBox(p)
        return

    source = None
    target = bm.select_history.active
    for f1 in selected:
        if f1.index != target.index:
            source = f1
            f1.select = True
        else:
            f1.select = False

    bpy.ops.mesh.select_linked()
    move_to(bm, source, target)
    if connect_geometry:
        bridge_two(bm, source, target)
    #ShowMessageBox(['Move success !'])
    print('finished.')
    # Show the updates in the viewport
    # and recalculate n-gon tessellation.
    bmesh.update_edit_mesh(me)



def connect_faces_by_edges(bm, source, target):
    fs1 = source.link_faces
    fs2 = target.link_faces
    found = False
    sf = None
    tf = None
    for f1 in fs1:
        for f2 in fs2:
            v1 = f1.calc_center_median()
            k1 = f2.verts[0].co
            k2 = f2.verts[1].co
            vector_a = v1 - k1
            vector_b = v1 - k2
            cr = vector_a.cross(vector_b)
            print(f2.normal.angle(cr))
            if f2.normal.angle(cr) < 0.05:
                found = True
                sf = f1
                tf = f2
    if found:
        bridge_two(bm, sf, tf)



def job_align_edge(bm, selected, connect_geometry):
    source = None
    target = bm.select_history.active
    for f1 in selected:
        if f1.index != target.index:
            source = f1
            f1.select = True
        else:
            f1.select = False

    bpy.ops.mesh.select_linked()
    move_to_edge(bm, source, target)

    if connect_geometry:
        connect_faces_by_edges(bm, source, target)


def job_slide_edge(bm, selected):
    bpy.ops.mesh.attach_align_slide_operator('INVOKE_DEFAULT')


def job_move_edge(context, connect_geometry):
    obj = context.edit_object
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)

    #bm.faces.active = None
    selected = []
    for f1 in bm.edges:
        if f1.select:
            selected.append(f1)

    if len(selected) == 1:
        job_slide_edge(bm, selected)
    elif len(selected) == 2:
        job_align_edge(bm, selected, connect_geometry)
    else:
        p = ['Thanks for using Attach Align addon!','',
            'Please select two edges, the source and destination.',
            'All conncted edges of source edge, will be aligned to ',
            'the orientation of destination edge.']
        ShowMessageBox(p)
        return

    #ShowMessageBox(['Move success !'])
    print('finished.')
    # Show the updates in the viewport
    # and recalculate n-gon tessellation.
    bmesh.update_edit_mesh(me)


def single_object_job(context, connect_geometry):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        job_move_face(context, connect_geometry)
    else:
        job_move_edge(context, connect_geometry)


def get_face_data(f1):
    p = f1.calc_center_median()
    return [p, f1.normal]

def get_edge_data(e1):
    p1 = e1.verts[0].co
    p2 = e1.verts[1].co
    return [p1, p2]


def selected_faces(obj):
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    p = []
    for f1 in bm.faces:
        if f1.select:
            p.append( get_face_data(f1))
    return p

def selected_edges(obj):
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    p = []
    for f1 in bm.edges:
        if f1.select:
            p.append( get_edge_data(f1))
    return p



def multi_object_job(context, source, target):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        faces1 = selected_faces(source)
        faces2 = selected_faces(target)
        if len(faces1) == 1 and len(faces2) == 1:
            multi_object_attach(context, source, target, faces1[0], faces2[0])
        else:
            p = ['Thanks for using Attach Align addon!','',
                'Please select only one face in each editing object,',
                'for source and destination.']
            ShowMessageBox(p)
    elif is_edge_mode:
        edges1 = selected_edges(source)
        edges2 = selected_edges(target)
        if len(edges1) == 1 and len(edges2) == 1:
            multi_object_align(context, source, target, edges1[0], edges2[0])
        else:
            p = ['Thanks for using Attach Align addon!','',
                'Please select only one edge in each editing object,',
                'for source and destination.']
            ShowMessageBox(p)



def switch_mode(context, connect_geometry):
    oblen = len(context.objects_in_mode)

    if oblen == 1:
        single_object_job(context, connect_geometry)
    elif oblen == 2:
        source = None
        target = None
        for o in context.objects_in_mode:
            if o.name == context.active_object.name:
                target = o
            else:
                source = o
        multi_object_job(context, source, target)
    else:
        p = ['Thanks for using Attach Align addon!','',
            'Please select two objects, enter to edit mode,',
            'then select one face or edge on each objects',
            'respectively.']
        ShowMessageBox(p)


class BDSM_Mesh_Face_Attach_Align(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.bdsm_mesh_face_attach_align"
    bl_label = "Attach Align"
    bl_options = {"REGISTER", "UNDO"}

    connect_geometry: BoolProperty(
            name="Connect geometries",
            description="Connect two geometries together",
            default=False
            )

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'
        editing = context.mode == 'EDIT_MESH'
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing and (is_face_mode or is_edge_mode)


    def execute(self, context):
        switch_mode(context, self.connect_geometry)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Options:")
        row = layout.row()
        row.prop(self, "connect_geometry")




def menu_func(self, context):
    self.layout.operator(BDSM_Mesh_Face_Attach_Align.bl_idname)


# Get the active mesh

