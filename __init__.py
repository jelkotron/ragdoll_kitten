bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Object",
}

import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
import ragdoll_ui
import ragdoll
import ragdoll_aux


def register():
    #-------- register custom properties --------
    bpy.utils.register_class(ragdoll.RagDollPropGroup)
    bpy.utils.register_class(ragdoll.RagDollBonePropGroup)

    #-------- set custom properties --------
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollPropGroup)
    bpy.types.PoseBone.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollBonePropGroup)
   
    #-------- register UI elements --------
    bpy.utils.register_class(ragdoll_ui.RagDollPanel)
    bpy.utils.register_class(ragdoll_ui.RagDollCollectionsPanel)
    bpy.utils.register_class(ragdoll_ui.RagDollSuffixesPanel)
    bpy.utils.register_class(ragdoll_ui.AddRigidBodyConstraintsOperator)
    bpy.utils.register_class(ragdoll_ui.AddRagDollOperator)
    bpy.utils.register_class(ragdoll_ui.RemoveRagDollOperator)
    bpy.utils.register_class(ragdoll_ui.UpdateRagDollOperator)
    bpy.utils.register_class(ragdoll_ui.UpdateWigglesOperator)
    bpy.utils.register_class(ragdoll_ui.UpdateDriversOperator)
    bpy.utils.register_class(ragdoll_ui.AddWiggleDriversOperator)
    bpy.utils.register_class(ragdoll_ui.RemoveWiggleDriversOperator)
    bpy.utils.register_class(ragdoll_ui.OT_TextBrowse)

    
def unregister():
    # del bpy.types.Armature.ragdoll
    # del bpy.types.Bone.ragdoll
    bpy.utils.unregister_class(ragdoll.RagDollPropGroup)
    bpy.utils.unregister_class(ragdoll.RagDollBonePropGroup)

    bpy.utils.unregister_class(ragdoll_ui.RagDollPanel)
    bpy.utils.unregister_class(ragdoll_ui.RagDollCollectionsPanel)
    bpy.utils.unregister_class(ragdoll_ui.RagDollSuffixesPanel)
    
    bpy.utils.unregister_class(ragdoll_ui.AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(ragdoll_ui.AddRagDollOperator)
    bpy.utils.unregister_class(ragdoll_ui.RemoveRagDollOperator)
    bpy.utils.unregister_class(ragdoll_ui.UpdateRagDollOperator)
    bpy.utils.unregister_class(ragdoll_ui.UpdateWigglesOperator)
    bpy.utils.unregister_class(ragdoll_ui.UpdateDriversOperator)
    bpy.utils.unregister_class(ragdoll_ui.AddWiggleDriversOperator)
    bpy.utils.unregister_class(ragdoll_ui.RemoveWiggleDriversOperator)
    bpy.utils.unregister_class(ragdoll_ui.OT_TextBrowse)
    
if "bpy" in locals():
    import importlib
    importlib.reload(ragdoll)
    importlib.reload(ragdoll_ui)
    importlib.reload(ragdoll_aux)


if __name__ == "__main__":
    register()
    

