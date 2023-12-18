import bpy, math
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty
from .. lib.setflow import SetEdgeLoopBase

class BDSM_Mesh_Edge_Flow(Operator, SetEdgeLoopBase):
    bl_idname = 'mesh.bdsm_mesh_edge_flow'
    bl_label = 'BDSM Mesh Edge Flow'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'BDSM Mesh Edge Flow \nadjust edge loops to curvature'

    tension : IntProperty(name='Tension', default=180, min=-500, max=500)
    iterations : IntProperty(name='Iterations', default=1, min=1, soft_max=32)
    min_angle : IntProperty(name='Min Angle', default=0, min=0, max=180, subtype='FACTOR' )


    def execute(self, context):
        # print ('execute')
        # print(f'Tension:{self.tension} Iterations:{self.iterations}')

        if not self.is_invoked:
            return self.invoke(context, None)

        bpy.ops.object.mode_set(mode='OBJECT')

        self.revert()

        for obj in self.objects:
            for i in range(self.iterations):
                for edgeloop in self.edgeloops[obj]:
                    edgeloop.set_flow(self.tension / 100.0, math.radians(self.min_angle) )

            self.bm[obj].to_mesh(obj.data)

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    def invoke(self, context, event):
        # print('invoke')

        if event:
            self.tension = 180
            self.iterations = 1
            self.bias = 0
            #self.min_angle = 0

        super(BDSM_Mesh_Edge_Flow, self).invoke(context)
        return self.execute(context)

class BDSM_Mesh_Edge_Linear(Operator, SetEdgeLoopBase):
    bl_idname = 'mesh.bdsm_mesh_edge_linear'
    bl_label = 'BDSM Mesh Edge Linear'
    bl_description = 'BDSM Mesh Edge Linear'
    bl_options = {'REGISTER', 'UNDO'}

    space_evenly : BoolProperty(name='Space evenly', default=False)
    distance : FloatProperty(name='Distance', default=1.0, min=0)

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        if self.do_straighten:
            column.prop(self, 'distance')
        else:
            column.prop(self, 'space_evenly')

    def invoke(self, context, event):
        super(BDSM_Mesh_Edge_Linear, self).invoke(context)

        self.do_straighten = self.can_straighten()
        if self.do_straighten:
            distance = 0
            edge_count = 0
            for obj in self.objects:
                for edgeloop in self.edgeloops[obj]:
                    distance += edgeloop.get_average_distance()

                edge_count += len(self.edgeloops[obj])

            distance /= edge_count

            self.distance = distance * 0.35

        return self.execute(context)

    def can_straighten(self):
        for obj in self.objects:
            for edgeloop in self.edgeloops[obj]:
                if len(edgeloop.edges) != 1:
                    return False

        return True
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        #print('execute')
        if not hasattr(self, 'objects') or not self.objects:
            return self.invoke(context, None)

        bpy.ops.object.mode_set(mode='OBJECT')

        self.revert()

        for obj in self.objects:
            for edgeloop in self.edgeloops[obj]:
                if self.do_straighten:
                    edgeloop.straighten(self.distance)
                else:
                    edgeloop.set_linear(self.space_evenly)

            self.bm[obj].to_mesh(obj.data)

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class BDSM_Mesh_Edge_Flow_Mode(Operator):
    bl_idname = 'mesh.bdsm_mesh_edge_flow_mode'
    bl_label = 'BDSM Mesh Edge Set Flow Mode'
    bl_description = 'BDSM Mesh Set Flow Mode'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        select_mode = bpy.context.tool_settings.mesh_select_mode
        if select_mode[0]:
            # bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.bdsm_mesh_smooth_laplacian()
            self.report({'INFO'}, 'Set Flow: VERTEX +1')
        if select_mode[1] and not select_mode[2]:
            # bpy.ops.mesh.edge_split(type='EDGE')
            bpy.ops.mesh.bdsm_mesh_edge_flow()
            self.report({'INFO'}, 'Set Flow: EDGE +1')
        if select_mode[2] and not select_mode[1]:
            # bpy.ops.mesh.split()
            bpy.ops.mesh.bdsm_mesh_edge_flow()
            self.report({'INFO'}, 'Set Flow: FACE +1')
        return {'FINISHED'}
