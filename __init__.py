bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Physics",
}

import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
import ragdoll_ui
import ragdoll
import ragdoll_aux


def register():
    #-------- register custom properties --------
    # bpy.utils.register_class(ragdoll.RagDollHook)
    bpy.utils.register_class(ragdoll.RagDollPropGroup)
    bpy.utils.register_class(ragdoll.RagDollBonePropGroup)


    #-------- set custom properties --------
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollPropGroup)
    bpy.types.PoseBone.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollBonePropGroup)
    # bpy.types.Armature.ragdoll.hooks = bpy.props.PointerProperty(type=ragdoll.RagDollBonePropGroup)

    #-------- register UI elements --------
    bpy.utils.register_class(ragdoll_ui.OBJECT_PT_RagDoll)
    bpy.utils.register_class(ragdoll_ui.OBJECT_PT_RagDollCollections)
    bpy.utils.register_class(ragdoll_ui.OBJECT_PT_RagDollSuffixes)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_AddRigidBodyConstraints)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_AddRagDoll)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_RemoveRagDoll)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_UpdateRagDoll)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_UpdateWiggles)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_UpdateDrivers)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_AddWiggleDrivers)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_RemoveWiggleDrivers)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_TextBrowseImport)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_RagdollJsonAdd)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_HookAdd)

def unregister():
    if bpy.types.Armature.ragdoll: del bpy.types.Armature.ragdoll
    if bpy.types.Bone.ragdoll: del bpy.types.Bone.ragdoll
    bpy.utils.unregister_class(ragdoll.RagDollPropGroup)
    bpy.utils.unregister_class(ragdoll.RagDollBonePropGroup)
    # bpy.utils.unregister_class(ragdoll.RagDollHook)

    bpy.utils.unregister_class(ragdoll_ui.OBJECT_PT_RagDoll)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_PT_RagDollCollections)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_PT_RagDollSuffixes)
    
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_AddRigidBodyConstraints)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_AddRagDoll)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_RemoveRagDoll)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_UpdateRagDoll)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_UpdateWiggles)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_UpdateDrivers)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_AddWiggleDrivers)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_RemoveWiggleDrivers)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_TextBrowseImport)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_RagdollJsonAdd)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_HookAdd)

if "bpy" in locals():
    import importlib
    importlib.reload(ragdoll)
    importlib.reload(ragdoll_ui)
    importlib.reload(ragdoll_aux)


if __name__ == "__main__":
    register()
    

