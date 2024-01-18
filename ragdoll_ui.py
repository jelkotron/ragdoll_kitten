
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_aux import rb_constraint_collection_set
from ragdoll_main import main

class AddRigidBodyConstraintsOperator(bpy.types.Operator):
    """Creates an Operator to add Rigid Body Constraint Group"""
    bl_idname = "scene.rbconstraints"
    bl_label = "Add Rigid Body Constraints"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rb_constraint_collection_set('RigidBodyConstraints')
        return {'FINISHED'}


class AddRagDollOperator(bpy.types.Operator):
    """Creates Ragdoll objects for selected Armature"""
    bl_idname = "armature.ragdoll"
    bl_label = "Add Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        main()
        print("Info: added ragdoll")
        return {'FINISHED'}


class RagDollPanel(bpy.types.Panel):
    """Creates a Panel in the Object Data properties window"""
    bl_label = "Ragdoll"
    bl_idname = "OBJECT_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        obj = context.object
        if obj.type == 'ARMATURE':
            layout = self.layout
            if not context.scene.rigidbody_world:
                row = layout.row()
                row.label(text="Please add rigid body world first.", icon="ERROR")
                row = layout.row()
                row.operator("rigidbody.world_add")
                
            elif not context.scene.rigidbody_world.constraints:
                row = layout.row()
                row.label(text="Please add rigid body constraints first.", icon="ERROR")
                row = layout.row()
                row.operator("scene.rbconstraints")
            else:

                row = layout.row()
                row.operator("armature.ragdoll")


# def register():
#     bpy.utils.register_class(RagDollPanel)
#     bpy.utils.register_class(AddRigidBodyConstraintsOperator)
#     bpy.utils.register_class(AddRagDollOperator)

# def unregister():
#     bpy.utils.unregister_class(RagDollPanel)
#     bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
#     bpy.utils.unregister_class(AddRagDollOperator)

# if __name__ == "__main__":
#     register()
