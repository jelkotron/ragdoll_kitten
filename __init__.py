bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Object",
}
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_ui import *

#-------- (un-)register UI elements --------
def register():
    #-------- initialize custom property to be available before ragdoll creation -------- 
    bpy.types.Armature.ragdoll_config = bpy.props.StringProperty(name="Config File", subtype='FILE_PATH')
    bpy.utils.register_class(RagDollPanel)
    bpy.utils.register_class(AddRigidBodyConstraintsOperator)
    bpy.utils.register_class(AddRagDollOperator)

def unregister():
    del bpy.types.Armature.ragdoll_config
    bpy.utils.unregister_class(RagDollPanel)
    bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(AddRagDollOperator)

if __name__ == "__main__":
    register()
    
