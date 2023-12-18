import bpy

tools_dic = {'selected_verts': [],
              'selected_edges': [],
              'selected_faces': []}


def write(data_block, values, obj=''):
    if obj == '':
        obj = bpy.context.active_object

    if 'tools' not in bpy.context.object:
        obj['tools'] = tools_dic

    obj['itools'][data_block] = values


def read(data_block, obj=''):
    if obj == '':
        obj = bpy.context.active_object

    if 'tools' in bpy.context.object:
        return obj['tools'][data_block]

    else:
        return ''
