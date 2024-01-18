bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Object",
}
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_ui import *

def register():
    #-------- initialize custom property to be available before ragdoll creation -------- 
    bpy.types.Armature.ragdoll_config = bpy.props.StringProperty(name="Config File", subtype='FILE_PATH')
    bpy.types.Armature.ctrl_rig_postfix = bpy.props.StringProperty(name="Control Rig Postfix", default=".CTRL")
    bpy.types.Armature.rd_postfix = bpy.props.StringProperty(name="Ragdoll Geo Postfix", default=".RB")
    bpy.types.Armature.const_postfix = bpy.props.StringProperty(name="Rigid Body Constraint Postfix", default=".CONST")
    bpy.types.Armature.connect_postfix = bpy.props.StringProperty(name="Connector Postfix", default=".CONST")
    bpy.types.Armature.rd_bone_width = bpy.props.FloatProperty(name="Rigid Body Geo Width", default=0.1)
    #-------- register UI elements --------
    bpy.utils.register_class(RagDollPanel)
    bpy.utils.register_class(AddRigidBodyConstraintsOperator)
    bpy.utils.register_class(AddRagDollOperator)

def unregister():
    del bpy.types.Armature.ragdoll_config
    del bpy.types.Armature.ctrl_rig_postfix
    del bpy.types.Armature.rd_postfix
    del bpy.types.Armature.const_postfix
    del bpy.types.Armature.connect_postfix
    del bpy.types.Armature.rd_bone_width
    bpy.utils.unregister_class(RagDollPanel)
    bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(AddRagDollOperator)

if __name__ == "__main__":
    register()
    
