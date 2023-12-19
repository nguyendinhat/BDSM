import bpy

keymap = []


def register():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
    #todo: Transform
        #Hotkey W - mesh.bdsm_transform_move
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('mesh.bdsm_transform_move','W', 'PRESS')
        keymap.append([km, kmi])

        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_transform_move','W', 'PRESS')
        keymap.append([km, kmi])

        #Hotkey E - mesh.bdsm_transform_move
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('mesh.bdsm_transform_rotate','E', 'PRESS')
        keymap.append([km, kmi])

        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_transform_rotate','E', 'PRESS')
        keymap.append([km, kmi])
        #Hotkey R - mesh.bdsm_transform_move
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('mesh.bdsm_transform_scale','R', 'PRESS')
        keymap.append([km, kmi])
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_transform_scale','R', 'PRESS')
        keymap.append([km, kmi])

        #todo: switchmode [Tab]
        # Hotkey tab - bdsm_control_object_modeset
        km = kc.keymaps.new(name='Object Non-modal', space_type='EMPTY')
        kmi = km.keymap_items.new('object.bdsm_control_object_modeset', 'TAB', 'PRESS')
        keymap.append([km, kmi])

        # Hotkey 1 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'ONE', 'PRESS')
        kmi.properties.type = 'SELECT_VERT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 2 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'TWO', 'PRESS')
        kmi.properties.type = 'SELECT_EDGE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 3 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'THREE', 'PRESS')
        kmi.properties.type = 'SELECT_FACE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 4 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Non-modal', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'FOUR', 'PRESS')
        kmi.properties.type = 'SELECT_OBJECT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 5 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'FIVE', 'PRESS')
        kmi.properties.type = 'SELECT_ELEMEMT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 6 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'SIX', 'PRESS')
        kmi.properties.type = 'SELECT_BORDER'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])

        # Hotkey 1 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'ONE', 'PRESS')
        kmi.properties.type = 'SELECT_VERT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 2 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'TWO', 'PRESS')
        kmi.properties.type = 'SELECT_EDGE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey 3 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'THREE', 'PRESS')
        kmi.properties.type = 'SELECT_FACE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])

        # Hotkey 5 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'FIVE', 'PRESS')
        kmi.properties.type = 'SELECT_ELEMEMT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])

        # Hotkey 6 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'SIX', 'PRESS')
        kmi.properties.type = 'SELECT_BORDER'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = False
        keymap.append([km, kmi])

        # Hotkey cmd 1 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'ONE', 'PRESS',oskey=True)
        kmi.properties.type = 'SELECT_VERT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = True
        keymap.append([km, kmi])
        # Hotkey cmd 2 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'TWO', 'PRESS',oskey=True)
        kmi.properties.type = 'SELECT_EDGE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = True
        keymap.append([km, kmi])
        # Hotkey cmd 3 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'THREE', 'PRESS',oskey=True)
        kmi.properties.type = 'SELECT_FACE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = False
        kmi.properties.use_expand = True
        keymap.append([km, kmi])

        # Hotkey shift 1 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'ONE', 'PRESS',shift=True)
        kmi.properties.type = 'SELECT_VERT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey shift 2 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'TWO', 'PRESS',shift=True)
        kmi.properties.type = 'SELECT_EDGE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = False
        keymap.append([km, kmi])
        # Hotkey shift 3 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'THREE', 'PRESS',shift=True)
        kmi.properties.type = 'SELECT_FACE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = False
        keymap.append([km, kmi])

        # Hotkey shift cmd 1 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'ONE', 'PRESS',oskey=True, shift=True)
        kmi.properties.type = 'SELECT_VERT'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = True
        keymap.append([km, kmi])
        # Hotkey shift cmd 2 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'TWO', 'PRESS',oskey=True, shift=True)
        kmi.properties.type = 'SELECT_EDGE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = True
        keymap.append([km, kmi])
        # Hotkey shift cmd 3 - bdsm_control_mesh_modeset
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.bdsm_control_mesh_modeset', 'THREE', 'PRESS',oskey=True, shift=True)
        kmi.properties.type = 'SELECT_FACE'
        kmi.properties.action = 'TOGGLE'
        kmi.properties.use_extend = True
        kmi.properties.use_expand = True
        keymap.append([km, kmi])

        # Hotkey cmd 6 - mesh.select_mirror
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.select_mirror', 'SIX', 'PRESS',oskey=True)
        kmi.properties.extend = True
        keymap.append([km, kmi])

        # Hotkey cmd 7 - mesh.bdsm_select_similar
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_select_similar', 'SEVEN', 'PRESS',oskey=True)
        keymap.append([km, kmi])

        # Hotkey COMMA - mesh.select_less
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.select_less','COMMA', 'PRESS',repeat=True)
        keymap.append([km, kmi])

        # Hotkey PERIOD - mesh.select_less
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.select_more','PERIOD', 'PRESS',repeat=True)
        keymap.append([km, kmi])

        # Hotkey cmd L - mesh.loop_multi_select
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.loop_multi_select', 'L', 'PRESS',oskey=True ,repeat=True)
        kmi.properties.ring = False
        keymap.append([km, kmi])

        # Hotkey cmd R - mesh.loop_multi_select - Ring
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.loop_multi_select', 'R', 'PRESS',oskey=True ,repeat=True)
        kmi.properties.ring = True
        keymap.append([km, kmi])


        #todo: Mesh
        #Extrude
        #Hotkey shift drag-mid - view3d.edit_mesh_extrude_move_normal
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_mesh_extrude', 'LEFTMOUSE', 'PRESS', ctrl=True)
        keymap.append([km, kmi])
        #Hotkey cmd E - wm.tool_set_by_id('builtin.extrude_region')
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.tool_set_by_id', 'E', 'PRESS', oskey=True)
        kmi.properties.name = 'builtin.extrude_region'
        kmi.properties.cycle = True
        kmi.properties.as_fallback = False
        keymap.append([km, kmi])
        #Bevel
        #Hotkey cmd B - mesh.bdsm_mesh_bevel
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_mesh_bevel', 'B', 'PRESS', oskey=True)
        keymap.append([km, kmi])
        #Connect
        #Hotkey shift cmd E - mesh.bdsm_mesh_connect
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_mesh_connect', 'E', 'PRESS', oskey=True, shift=True)
        keymap.append([km, kmi])
        #Split
        #Hotkey Y - mesh.bdsm_mesh_split
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_mesh_split', 'Y', 'PRESS')
        keymap.append([km, kmi])
        #Target Weld
        #Hotkey cmd T - view3d.bdsm_targetweld
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_targetweld', 'T', 'PRESS', oskey=True)
        kmi.properties.toggle = True
        keymap.append([km, kmi])

        #Set Flow
        #Hotkey option 1 - mesh.bdsm_mesh_flow_mode
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('mesh.bdsm_mesh_flow_mode', 'ONE', 'PRESS', alt=True, repeat=True)
        keymap.append([km, kmi])




        #Delete
        #Hotkey backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS')
        kmi.properties.hierarchy = False
        kmi.properties.expand = False
        kmi.properties.smart = False
        keymap.append([km, kmi])
        #Hotkey shift backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', shift=True)
        kmi.properties.hierarchy = False
        kmi.properties.expand = True
        kmi.properties.smart = False
        keymap.append([km, kmi])
        #Hotkey cmd backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', oskey=True)
        kmi.properties.hierarchy = False
        kmi.properties.expand = False
        kmi.properties.smart = True
        keymap.append([km, kmi])
        #Hotkey shift cmd backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', oskey=True, shift=True)
        kmi.properties.hierarchy = False
        kmi.properties.expand = True
        kmi.properties.smart = True
        keymap.append([km, kmi])
        #Hotkey alt backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', alt=True)
        kmi.properties.hierarchy = True
        kmi.properties.expand = False
        kmi.properties.smart = False
        keymap.append([km, kmi])
        #Hotkey shift alt backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', shift=True, alt=True)
        kmi.properties.hierarchy = True
        kmi.properties.expand = True
        kmi.properties.smart = False
        keymap.append([km, kmi])
        #Hotkey shift alt cmd backspace - view3d.bdsm_delete
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_delete', 'BACK_SPACE', 'PRESS', shift=True, alt=True, oskey=True)
        kmi.properties.hierarchy = True
        kmi.properties.expand = True
        kmi.properties.smart = True
        keymap.append([km, kmi])

        #todo: Pivot - Origin
        #Hotkey cmd 8 / ctrl COMMA - view3d.bdsm_origin_set
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_origin_set', 'EIGHT', 'PRESS',oskey=True)
        kmi.properties.toggle = False
        kmi.properties.set = True
        keymap.append([km, kmi])
        kmi = km.keymap_items.new('view3d.bdsm_origin_set', 'COMMA', 'PRESS',ctrl=True)
        kmi.properties.toggle = True
        kmi.properties.set = False
        keymap.append([km, kmi])

        #todo: Pivot - Point
        #Hotkey option ACCENT_GRAVE - view3d.bdsm_pivot_set
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('view3d.bdsm_pivot_set', 'ACCENT_GRAVE', 'PRESS',alt=True)
        kmi.properties.mode = 'CYCLE'
        keymap.append([km, kmi])
        #Hotkey option ACCENT_GRAVE - view3d.bdsm_pivot_set
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('view3d.bdsm_pivot_set', 'ACCENT_GRAVE', 'PRESS',alt=True)
        kmi.properties.mode = 'TYPE_3'
        keymap.append([km, kmi])


        #todo: Pivot - Oriental
        #Hotkey ctrl ACCENT_GRAVE - view3d.bdsm_oriental_set
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('view3d.bdsm_oriental_set', 'ACCENT_GRAVE', 'PRESS',ctrl=True)
        kmi.properties.mode = 'CYCLE'
        keymap.append([km, kmi])
        #Hotkey ctrl ACCENT_GRAVE - view3d.bdsm_oriental_set
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new('view3d.bdsm_oriental_set', 'ACCENT_GRAVE', 'PRESS',ctrl=True)
        kmi.properties.mode = 'TYPE_1'
        keymap.append([km, kmi])


        #todo: Drop it
        #Hotkey  cmd DOWN_ARROW - object.bdsm_object_drop_it
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('object.bdsm_object_drop_it', 'DOWN_ARROW', 'PRESS', oskey=True)
        keymap.append([km, kmi])

        #Debug

        #todo: Snap Tool
        #Hotkey S - view3d.bdsm_snap_tool
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.bdsm_snap_tool', 'S', 'PRESS')
        keymap.append([km, kmi])

        #todo: Rename - F2
        # Hotkey F2 - wm.batch_rename
        km = kc.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
        kmi = km.keymap_items.new('wm.batch_rename', 'F2', 'PRESS')
        keymap.append([km, kmi])
        #outliner.item_rename
        km = kc.keymaps.new(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
        kmi = km.keymap_items.new('outliner.item_rename', 'LEFTMOUSE', 'DOUBLE_CLICK')
        keymap.append([km, kmi])
        km = kc.keymaps.new(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
        kmi = km.keymap_items.new('outliner.item_rename', 'F2', 'PRESS')
        keymap.append([km, kmi])
        kmi.properties.use_active = True

def unregister():
    for km,kmi in keymap:
        km.keymap_items.remove(kmi)
    keymap.clear()