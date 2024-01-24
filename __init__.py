bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Object",
}
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_ui import *
from ragdoll import RagDollPropGroup

def register():
    #-------- register custom properties --------
    bpy.utils.register_class(RagDollPropGroup)
    bpy.types.CopyTransformsConstraint.ragdoll_bone_constraint_type = bpy.props.StringProperty(default="")
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=RagDollPropGroup)

    #-------- register UI elements --------
    bpy.utils.register_class(RagDollPanel)
    bpy.utils.register_class(RagDollSettingsPanel)
    bpy.utils.register_class(RagDollCollectionsPanel)
    bpy.utils.register_class(RagDollPostfixesPanel)

    bpy.utils.register_class(AddRigidBodyConstraintsOperator)
    bpy.utils.register_class(AddRagDollOperator)
    bpy.utils.register_class(RemoveRagDollOperator)
    bpy.utils.register_class(UpdateRagDollOperator)
    bpy.utils.register_class(OT_TextBrowse)

    
def unregister():
    del bpy.types.Armature.ragdoll
    del bpy.types.CopyTransformsConstraint.ragdoll_bone_constraint_type
    bpy.utils.unregister_class(RagDollPropGroup)

    bpy.utils.unregister_class(RagDollPanel)
    bpy.utils.register_class(RagDollSettingsPanel)
    bpy.utils.unregister_class(RagDollCollectionsPanel)
    bpy.utils.unregister_class(RagDollPostfixesPanel)
    
    bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(AddRagDollOperator)
    bpy.utils.unregister_class(RemoveRagDollOperator)
    bpy.utils.unregister_class(UpdateRagDollOperator)
    bpy.utils.unregister_class(OT_TextBrowse)
    
if __name__ == "__main__":
    register()
    
