import bpy
import bmesh
import math
import mathutils

from ..utils.setflow import get_edgeloops, hermite_3d


class SetEdgeLoopBase():

    def __init__(self):
        self.is_invoked = False

    def get_bm(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()
        return bm

    def revert(self):
        # print('reverting vertex positions')
        for obj in self.objects:
            if  obj in self.vert_positions:
                for vert, pos in self.vert_positions[obj].items():
                    # print('revert: %s -> %s' % (vert.index, pos))
                    vert.co = pos
    
    @classmethod
    def poll(cls, context):
        return (
            context.space_data.type == 'VIEW_3D'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.mode == 'EDIT')

    def invoke(self, context):
        # print('base invoke')
        self.is_invoked = True

        self.objects = set(context.selected_editable_objects)
        self.bm = {}
        self.edgeloops = {}
        self.vert_positions = {}

        bpy.ops.object.mode_set(mode='OBJECT')

        ignore = set()

        for obj in self.objects:
            self.bm[obj] = self.get_bm(obj)

            edges = [e for e in self.bm[obj].edges if e.select]

            if len(edges) == 0:
                ignore.add(obj)
                continue
            self.vert_positions[obj] = {}
            for e in edges:
                for v in e.verts:
                    if v not in self.vert_positions[obj]:
                        # print('storing: %s ' % v.co)
                        p = v.co.copy()
                        p = p.freeze()
                        self.vert_positions[obj][v] = p

            self.edgeloops[obj] = get_edgeloops(self.bm[obj], edges)

        self.objects = self.objects - ignore






