import bpy
from bpy.props import BoolProperty, FloatProperty, EnumProperty
import bmesh

from . import util
from . import op_set_edge_flow


class BDSM_Mesh_Edge_Linear(bpy.types.Operator, op_set_edge_flow.SetEdgeLoopBase):
    bl_idname = 'mesh.bdsm_mesh_edge_linear'
    bl_label = 'BDSM Mesh Edge Linear'
    bl_description = 'BDSM Mesh Edge Linear\n'\
                    'Makes edge loops linear between start and end vertices'
    bl_options = {'REGISTER', 'UNDO'}

    space_evenly : BoolProperty(name="Space evenly", default=False, description="Spread the vertices in even distances")
   
    def invoke(self, context, event):
       
        super(BDSM_Mesh_Edge_Linear, self).invoke(context)
        return self.execute(context)

    def can_straighten(self):
        for obj in self.objects:
            for edgeloop in self.edgeloops[obj]:
                if len(edgeloop.edges) != 1:
                    return False

        return True

    def execute(self, context):
        #print("execute")
      
        if not self.is_invoked:        
            return self.invoke(context, None)
        else:
            self.revert()

        for obj in self.objects:
            for edgeloop in self.edgeloops[obj]:               
                edgeloop.set_linear(self.space_evenly)

            self.bm[obj].normal_update()
            bmesh.update_edit_mesh(obj.data)

        self.is_invoked = False
        return {'FINISHED'}
