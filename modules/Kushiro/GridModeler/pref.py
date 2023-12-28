# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro


import bpy

from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty, FloatVectorProperty



def get_pref():
    pe = {
        'textsize' : 14,
        'textcolor': (1, 1, 1, 1),
        'default_ope': 'boolcut',
        'bool_abs' : True,
        'bool_showkey': False,
        'text_pos_x': 120,
        'line_color': (1, 1, 1, 0.2),
        'line_width': 2,
        'shape_color': (1, 1, 1, 1),
        'shape_width': 2,
        'color_cursor1':(0 ,0 ,0, 1),
        'color_cursor2':(1 ,1 ,1, 1),
        'color_construction_line': (1, 0, 0, 1),
        'color_line_selected': (1, 1, 1, 1),
        'color_pivot': (0, 0, 1, 1),
        'color_vertex': (1, 1, 1, 1),
        'color_vertex_selected': (0, 1, 1, 1),
        'color_box_select': (1, 1, 1, 1),
        'color_duplicate': (1, 1, 0, 1),
        'color_line_bevel': (1, 1, 1, 1),
        'color_circle_draw': (1, 1, 0, 1),
        'color_main_edge': (0, 1, 0, 1),
        'color_eng': (1, 0, 1, 1),
        }

    try:
        prefs = bpy.context.preferences.addons['BDSM'].preferences
        pe['textsize'] = prefs.kushiro_gridmodeler_textsize
        pe['textcolor'] = prefs.kushiro_gridmodeler_textcolor
        pe['default_ope'] = prefs.kushiro_gridmodeler_default_operation_mode
        pe['bool_abs'] = prefs.kushiro_gridmodeler_bool_abs
        pe['bool_showkey'] = prefs.kushiro_gridmodeler_bool_showkey
        pe['text_pos_x'] = prefs.kushiro_gridmodeler_text_pos_x
        pe['line_color'] = prefs.kushiro_gridmodeler_line_color
        pe['line_width'] = prefs.kushiro_gridmodeler_line_width
        pe['shape_color'] = prefs.kushiro_gridmodeler_shape_color
        pe['shape_width'] = prefs.kushiro_gridmodeler_shape_width
        pe['color_cursor1'] = prefs.kushiro_gridmodeler_color_cursor1
        pe['color_cursor2'] = prefs.kushiro_gridmodeler_color_cursor2
        pe['color_construction_line'] = prefs.kushiro_gridmodeler_color_construction_line
        pe['color_line_selected'] = prefs.kushiro_gridmodeler_color_line_selected
        pe['color_pivot'] = prefs.kushiro_gridmodeler_color_pivot
        pe['color_vertex'] = prefs.kushiro_gridmodeler_color_vertex
        pe['color_vertex_selected'] = prefs.kushiro_gridmodeler_color_vertex_selected
        pe['color_box_select'] = prefs.kushiro_gridmodeler_color_box_select
        pe['color_duplicate'] = prefs.kushiro_gridmodeler_color_duplicate
        pe['color_line_bevel'] = prefs.kushiro_gridmodeler_color_line_bevel
        pe['color_circle_draw'] = prefs.kushiro_gridmodeler_color_circle_draw
        pe['color_main_edge'] = prefs.kushiro_gridmodeler_color_main_edge
        pe['color_eng'] = prefs.kushiro_gridmodeler_color_eng
        
        return pe
    except:
        print('pref error')
        pass
    return pe
