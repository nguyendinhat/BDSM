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
        'shape_color': (1, 1, 1, 1)
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
        pe['shape_color'] = prefs.kushiro_gridmodeler_shape_color
        return pe
    except:
        print('pref error')
        pass
    return pe
