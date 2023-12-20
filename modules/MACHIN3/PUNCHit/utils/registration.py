import bpy
from bpy.utils import register_class, unregister_class, previews
import os

def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_prefs():
    return bpy.context.preferences.addons['BDSM'].preferences
