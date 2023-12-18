import bpy
import rna_keymap_ui

def prefs_ui(self, layout):
    col = layout.column()
    col.scale_y = 1.2
    col.use_property_split = False
    col.prop(self, "show_shortcuts", icon='DISCLOSURE_TRI_DOWN' if self.show_shortcuts else 'DISCLOSURE_TRI_RIGHT')
    if self.show_shortcuts:
        shortcuts_box = col.row().box()
        bdsm_entries = []
        conflicts = {}
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        for km in kc.keymaps:
            entry = []
            for i in km.keymap_items:
                if ".bdsm_" in i.idname or i.idname.startswith("bdsm."):
                    entry.append(i)
                    if self.show_conflicts:
                        found = find_conflict(km, i)
                        if found:
                            for cat in found:
                                existing = conflicts.get(cat[0], None)
                                if existing is None:
                                    conflicts[cat[0]] = cat[1]
                                else:
                                    new = list(set(existing + cat[1]))
                                    conflicts[cat[0]] = new
            if entry:
                bdsm_entries.append((km, entry))
        if bdsm_entries:
            for km, kmi in bdsm_entries:
                col = shortcuts_box.column()
                col.label(text=str(km.name))
                for i in kmi:
                    row = col.row()
                    row.context_pointer_set("keymap", km)
                    rna_keymap_ui.draw_kmi([], kc, km, i, row, 0)
        col.separator()
        col.prop(self, "show_conflicts", icon='DISCLOSURE_TRI_DOWN' if self.show_conflicts else 'DISCLOSURE_TRI_RIGHT')
        if self.show_conflicts:
            conflicts_box = col.row().box()
            if conflicts:
                col = conflicts_box.column()
                for k in conflicts.keys():
                    col.label(text=str(k.name))
                    for i in conflicts[k]:
                        row = col.row()
                        col.context_pointer_set("keymap", k)
                        rna_keymap_ui.draw_kmi([], kc, k, i, row, 0)

def find_conflict(skm, i):
    ku = bpy.context.window_manager.keyconfigs.user
    usual_suspects = ['Screen', '3D View', '3D View Generic', 'Object Mode', 'Mesh', 'Curve', 'Armature', 'Window']
    conflicts = []
    for km in ku.keymaps:
        entry = []
        if km == skm or km.name in usual_suspects:
            for item in km.keymap_items:
                if item.name != i.name and item.active:
                    if (item.type, item.value, item.ctrl, item.alt, item.shift) == \
                            (i.type, i.value, i.ctrl, i.alt, i.shift):
                        entry.append(item)
            if entry:
                conflicts.append((km, entry))
    return conflicts
