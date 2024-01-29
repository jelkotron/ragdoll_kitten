bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Object",
}

import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_ui import *
from ragdoll import RagDollPropGroup, RagDollBonePropGroup

def register():
    #-------- register custom properties --------
    bpy.utils.register_class(RagDollPropGroup)
    bpy.utils.register_class(RagDollBonePropGroup)
    bpy.types.CopyTransformsConstraint.ragdoll_bone_constraint_type = bpy.props.StringProperty(default="")
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=RagDollPropGroup)
    bpy.types.Bone.ragdoll = bpy.props.PointerProperty(type=RagDollBonePropGroup)
    #-------- register UI elements --------
    bpy.utils.register_class(RagDollPanel)
    bpy.utils.register_class(RagDollCollectionsPanel)
    bpy.utils.register_class(RagDollSuffixesPanel)

    bpy.utils.register_class(AddRigidBodyConstraintsOperator)
    bpy.utils.register_class(AddRagDollOperator)
    bpy.utils.register_class(RemoveRagDollOperator)
    bpy.utils.register_class(UpdateRagDollOperator)
    bpy.utils.register_class(UpdateWigglesOperator)
    bpy.utils.register_class(UpdateDriversOperator)
    bpy.utils.register_class(OT_TextBrowse)

    
def unregister():
    del bpy.types.Armature.ragdoll
    del bpy.types.Bone.ragdoll
    del bpy.types.CopyTransformsConstraint.ragdoll_bone_constraint_type
    bpy.utils.unregister_class(RagDollPropGroup)
    bpy.utils.unregister_class(RagDollBonePropGroup)

    bpy.utils.unregister_class(RagDollPanel)
    bpy.utils.unregister_class(RagDollCollectionsPanel)
    bpy.utils.unregister_class(RagDollSuffixesPanel)
    
    bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(AddRagDollOperator)
    bpy.utils.unregister_class(RemoveRagDollOperator)
    bpy.utils.unregister_class(UpdateRagDollOperator)
    bpy.utils.unregister_class(UpdateWigglesOperator)
    bpy.utils.unregister_class(UpdateDriversOperator)
    bpy.utils.unregister_class(OT_TextBrowse)
    
if __name__ == "__main__":
    register()
    
