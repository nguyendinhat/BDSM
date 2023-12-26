import bpy, blf, rna_keymap_ui
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar

from mathutils import Vector
from time import time

def get_prefs():
    return bpy.context.preferences.addons['BDSM'].preferences

#FIXME: Utils
def init_cursor(self, event, offsetx=0, offsety=20):
    self.last_mouse_x = event.mouse_x
    self.last_mouse_y = event.mouse_y
    self.region_offset_x = event.mouse_x - event.mouse_region_x
    self.region_offset_y = event.mouse_y - event.mouse_region_y
    self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety

def update_HUD_location(self, event, offsetx=0, offsety=20):
    if get_prefs().modal_hud_follow_mouse:
        self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
        self.HUD_y = event.mouse_y - self.region_offset_y + offsety

def get_mouse_pos(self, context, event, hud=True, hud_offset=(20, 20)):
    prefs = bpy.context.preferences.addons['BDSM'].preferences
    self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
    if hud:
        scale = context.preferences.system.ui_scale * get_prefs().machin3_punchit_modal_hud_scale
        self.HUD_x = self.mouse_pos.x + hud_offset[0] * scale
        self.HUD_y = self.mouse_pos.y + hud_offset[1] * scale




#HUD
def draw_init(self):
    self.font_id = 1
    self.offset = 0

def draw_title(self, title, subtitle=None, subtitleoffset=125, HUDcolor=None, HUDalpha=0.5, shadow=True):
    if not HUDcolor:
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    scale = bpy.context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    if shadow:
        blf.color(self.font_id, *shadow, HUDalpha * 0.7)
        blf.position(self.font_id, self.HUD_x - 7 + 1, self.HUD_y - 1, 0)
        blf.size(self.font_id, int(20 * scale))
        blf.draw(self.font_id, "• " + title)

    blf.color(self.font_id, *HUDcolor, HUDalpha)
    blf.position(self.font_id, self.HUD_x - 7, self.HUD_y, 0)
    blf.size(self.font_id, int(20 * scale))
    blf.draw(self.font_id, f"» {title}")

    if subtitle:
        if shadow:
            blf.color(self.font_id, *shadow, HUDalpha / 2 * 0.7)
            blf.position(self.font_id, self.HUD_x - 7 + int(subtitleoffset * scale), self.HUD_y, 0)
            blf.size(self.font_id, int(15 * scale))
            blf.draw(self.font_id, subtitle)

        blf.color(self.font_id, *HUDcolor, HUDalpha / 2)
        blf.position(self.font_id, self.HUD_x - 7 + int(subtitleoffset * scale), self.HUD_y, 0)
        blf.size(self.font_id, int(15 * scale))
        blf.draw(self.font_id, subtitle)
    return blf.dimensions(self.font_id, str(title))

def draw_prop(self, name, value, offset=0, decimal=2, active=True, HUDcolor=None, prop_offset=120, hint="", hint_offset=200, shadow=True, value_color=None):
    if not HUDcolor:
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)
    alpha = 0.4
    if active:
        alpha = 1

    scale = bpy.context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    offset = self.offset + int(offset * scale)
    self.offset = offset

    if shadow:
        blf.color(self.font_id, *shadow, alpha * 0.7)
        blf.position(self.font_id, self.HUD_x + int(20 * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
        blf.size(self.font_id, int(11 * scale))
        blf.draw(self.font_id, name)

    blf.color(self.font_id, *HUDcolor, alpha)
    blf.position(self.font_id, self.HUD_x + int(20 * scale), self.HUD_y - int(20 * scale) - offset, 0)
    blf.size(self.font_id, int(11 * scale))
    blf.draw(self.font_id, name)

    #todo: Value String
    if type(value) is str:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(14 * scale))
            blf.draw(self.font_id, value)
        if not value_color:
            value_color = HUDcolor
        blf.color(self.font_id, *value_color, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale))
        blf.draw(self.font_id, value)

    #todo: Value Boolean
    elif type(value) is bool:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(14 * scale))
            blf.draw(self.font_id, str(value))
        if value:
            blf.color(self.font_id, 0.5, 1, 0.5, alpha)
        else:
            blf.color(self.font_id, 1, 0.3, 0.3, alpha)

        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale))
        blf.draw(self.font_id, str(value))

    #todo: Value Numeric INT
    elif type(value) is int:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(20 * scale))
            blf.draw(self.font_id, "%d" % (value))
        if not value_color:
            value_color = HUDcolor
        blf.color(self.font_id, *value_color, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(20 * scale))
        blf.draw(self.font_id, "%d" % (value))

    #todo: Value Numeric Float
    elif type(value) is float:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(16 * scale))
            blf.draw(self.font_id, "%.*f" % (decimal, value))
        if not value_color:
            value_color = HUDcolor
        blf.color(self.font_id, *value_color, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(16 * scale))
        blf.draw(self.font_id, "%.*f" % (decimal, value))

    if get_prefs().modal_hud_hints and hint:
        if shadow:
            blf.color(self.font_id, *shadow, 0.6 * 0.7)
            blf.position(self.font_id, self.HUD_x + int(hint_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(11 * scale))
            blf.draw(self.font_id, "%s" % (hint))

        blf.color(self.font_id, *HUDcolor, 0.6)
        blf.position(self.font_id, self.HUD_x + int(hint_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(11 * scale))
        blf.draw(self.font_id, "%s" % (hint))

    return blf.dimensions(self.font_id, str(value))



def draw_label(context, title='', coords=None, offset=0, center=True, size=12, color=(1, 1, 1), alpha=1):
    if not coords:
        region = context.region
        width = region.width / 2
        height = region.height / 2
    else:
        width, height = coords

    scale = context.preferences.system.ui_scale * get_prefs().machin3_punchit_modal_hud_scale

    font = 1
    fontsize = int(size * scale)

    blf.size(font, fontsize)
    blf.color(font, *color, alpha)

    if center:
        dims = blf.dimensions(font, title)
        blf.position(font, width - (dims[0] / 2), height - (offset * scale), 1)

    else:
        blf.position(font, width, height - (offset * scale), 1)

    blf.draw(font, title)

    return blf.dimensions(font, title)



#Startusbar
def draw_basic_status(self, context, title):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text=title)

        row.label(text="", icon='MOUSE_LMB')
        row.label(text="Finish")

        if context.window_manager.keyconfigs.active.name.startswith('blender'):
            row.label(text="", icon='MOUSE_MMB')
            row.label(text="Viewport")

        row.label(text="", icon='MOUSE_RMB')
        row.label(text="Cancel")

    return draw

def init_status(self, context, title='', func=None):
    self.bar_orig = statusbar.draw

    if func:
        statusbar.draw = func
    else:
        statusbar.draw = draw_basic_status(self, context, title)

def finish_status(self):
    statusbar.draw = self.bar_orig





