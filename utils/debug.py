import bpy
from mathutils import Matrix, Vector
from bpy import context
from math import degrees, atan2, pi
import bmesh
# project into XY plane,

active_obj = bpy.context.object
if active_obj is None:
    active_obj = context.object

verts_selected = [vert for vert in active_obj.data.vertices if vert.select]
edges_selected = [edge for edge in active_obj.data.edges if edge.select]
excute_edges = [edge.index for edge in active_obj.data.edges if edge.select]

bpy.ops.object.mode_set(mode='OBJECT')

for edge_id in excute_edges:
    active_obj.data.edges[edge_id].select = False

bpy.ops.object.mode_set(mode='EDIT')
b_mesh = bmesh.from_edit_mesh(active_obj.data)
subdivide_edges = [edge for edge in b_mesh.edges if edge.index in excute_edges]

new_edges = bmesh.ops.subdivide_edges(b_mesh, edges=subdivide_edges, cuts=1, use_grid_fill=False)

for edge in new_edges['geom_inner']:
    edge.select = True
bmesh.update_edit_mesh(active_obj.data)

bpy.ops.object.mode_set(mode='OBJECT')
output_selected = [edge for edge in active_obj.data.edges if edge.select]
bpy.ops.object.mode_set(mode='EDIT')
b_mesh = bmesh.from_edit_mesh(active_obj.data)
output_selected = [edge for edge in b_mesh.edges if edge.select]
bmesh.ops.dissolve_edges(b_mesh, edges=output_selected, use_verts=True, use_face_split=False)
bmesh.update_edit_mesh(active_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
for edge in edges_selected:
    edge.select = True
bpy.ops.object.mode_set(mode='EDIT')

edges_selected[0].index




addon_name = 'BDSM'
preferences = bpy.context.preferences
addon_prefs = preferences.addons[addon_name].preferences

bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
addon_prefs.active_section = 'ADDONS'
bpy.ops.preferences.addon_expand(module = addon_name.split('.')[0])
bpy.ops.preferences.addon_show(module = addon_name.split('.')[0])

bpy.ops.preferences.addon_expand(module='BDSM')
bpy.ops.space_data.show_region_ui()
bpy.context.screen.areas




bpy.data.window_managers['WinMan'].addon_search = 'BDSM'
bpy.ops.wm.addon_expand(module = 'BDSM')




import bpy
import addon_utils

module_name = 'BDSM'
addon_utils.modules_refresh()

bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
bpy.context.user_preferences.active_section = 'ADDONS'
bpy.data.window_managers['WinMan'].addon_search = 'BDSM'

try:
    mod = addon_utils.addons_fake_modules.get(module_name)
    info = addon_utils.module_bl_info(mod)
    if not info['show_expanded']:
        info['show_expanded'] = True

except:
    import traceback
    traceback.print_exc()







for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                # True: n-panel is open
                # False: n-panel is closed
                n_panel_is_open = space.show_region_ui

                # You can even set it
                if not n_panel_is_open:
                    space.show_region_ui = True

                break

space = [space for area in bpy.context.screen.areas if area.type == 'VIEW_3D' for space in area.spaces  if space.type == 'VIEW_3D']
space[0].show_region_ui = True

bpy.context.object.update_from_editmode()
for edge in active_obj.data.edges   :
    for edge in bpy.context.active_object.data.edges:
        print(edge.index)



bpy.ops.object.mode_set(mode='OBJECT')
for edge in active_obj.data.edges:
    if edge.index in excute_edges:
        edge.select = False
bpy.ops.object.mode_set(mode='EDIT')


bpy.ops.object.mode_set(mode='OBJECT')

for polygon in bpy.context.active_object.data.polygons:
    polygon.select = False
for edge in bpy.context.active_object.data.edges:
    edge.select = False
for vertex in bpy.context.active_object.data.vertices:
    vertex.select = False

bpy.ops.object.mode_set(mode='EDIT')


b_mesh = bmesh.from_edit_mesh(active_obj.data)
b_mesh.verts.ensure_lookup_table()
b_mesh.edges.ensure_lookup_table()
b_mesh.faces.ensure_lookup_table()
selected_verts = [vert for vert in b_mesh.verts if vert.select]
selected_edges = [edge for edge in b_mesh.edges if edge.select]
subdivide_edges = [edge for edge in b_mesh.edges if edge.index in excute_edges]

bmesh.update_edit_mesh(active_obj.data)

bmesh.ops.dissolve_edges(b_mesh, edges=selected_edges, use_verts=True, use_face_split=False)

bmesh.update_edit_mesh(active_obj.data)

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type='OUTPUT')

