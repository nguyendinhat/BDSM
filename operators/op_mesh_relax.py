import bpy
from bpy.types import Operator
from bpy.props import IntProperty

def relax_mesh(context):

    # deselect everything that's not related
    for obj in context.selected_objects:
        obj.select_set(False)

    # get active object
    obj = context.active_object

    # duplicate the object so it can be used for the shrinkwrap modifier
    obj.select_set(True) # make sure the object is selected!
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.duplicate()
    target = context.active_object

    # remove all other modifiers from the target
    for m in range(0, len(target.modifiers)):
        target.modifiers.remove(target.modifiers[0])

    context.view_layer.objects.active = obj

    sw = obj.modifiers.new(type='SHRINKWRAP', name='relax_target')
    sw.target = target

    # run smooth operator to relax the mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.vertices_smooth(factor=0.5)
    bpy.ops.object.mode_set(mode='OBJECT')

    # apply the modifier
    bpy.ops.object.modifier_apply(modifier='relax_target')

    # delete the target object
    obj.select_set(False)
    target.select_set(True)
    bpy.ops.object.delete()

    # go back to initial state
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

class BDSM_Mesh_Relax(Operator):
    '''Relaxes selected vertices while retaining the shape ''' \
    '''as much as possible'''
    bl_idname = 'mesh.bdsm_mesh_relax'
    bl_label = 'BDSM Mesh Relax'
    bl_description= 'Relax the selected verts while retaining the shape'
    bl_options = {'REGISTER', 'UNDO'}

    iterations: IntProperty(name='Relax iterations',
                default=1, min=0, max=100, soft_min=0, soft_max=10)


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.mode == 'EDIT' and obj.type == 'MESH')

    def execute(self, context):
        for i in range(0,self.iterations):
            relax_mesh(context)
        return {'FINISHED'}

