bl_info = {
    "name": "Ragdoll",
    "blender": (4, 0, 1),
    "category": "Physics",
    "author": "Oliver Jelko"
}

import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
import ragdoll_ui
import ragdoll
import ragdoll_aux


def register():
    #-------- register custom properties --------
    bpy.utils.register_class(ragdoll.RdConnectors)
    bpy.utils.register_class(ragdoll.RdRigidBodyConstraints)
    bpy.utils.register_class(ragdoll.RdHookConstraints)
    bpy.utils.register_class(ragdoll.RdHooks)
    bpy.utils.register_class(ragdoll.RdRigidBodies)
    bpy.utils.register_class(ragdoll.RagDollBone)
    bpy.utils.register_class(ragdoll.RdWiggleConstraints)
    bpy.utils.register_class(ragdoll.RdWiggles)
    bpy.utils.register_class(ragdoll.RagDoll)

    #-------- set custom properties --------
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDoll)
    bpy.types.PoseBone.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollBone)
    bpy.types.Object.ragdoll_bone_name = bpy.props.StringProperty()
    
    #-------- register UI elements --------
    bpy.utils.register_class(ragdoll_ui.Scene_OT_RigidBodyWorldAddCustom)
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
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_HookRemove)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_MeshApproximate)
    bpy.utils.register_class(ragdoll_ui.OBJECT_OT_MeshApproximateReset)


def unregister():
    #-------- unset custom properties --------
    if bpy.types.Armature.ragdoll: 
        del bpy.types.Armature.ragdoll
    if bpy.types.Bone.ragdoll: 
        del bpy.types.Bone.ragdoll
    if bpy.types.Object.ragdoll_bone_name: 
        del bpy.types.Object.ragdoll_bone_name 

    #-------- unregister custom properties --------
    bpy.utils.unregister_class(ragdoll_ui.Scene_OT_RigidBodyWorldAddCustom)
    bpy.utils.unregister_class(ragdoll.RdConnectors)
    bpy.utils.unregister_class(ragdoll.RdRigidBodyConstraints)
    bpy.utils.unregister_class(ragdoll.RdRigidBodies)
    bpy.utils.unregister_class(ragdoll.RdRigidBodies)
    bpy.utils.unregister_class(ragdoll.RagDollBone)
    bpy.utils.unregister_class(ragdoll.RagDoll)
    bpy.utils.unregister_class(ragdoll.RdWiggleConstraints)
    bpy.utils.unregister_class(ragdoll.RdWiggles)
    
    #-------- unregister UI elements --------
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
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_HookRemove)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_MeshApproximate)
    bpy.utils.unregister_class(ragdoll_ui.OBJECT_OT_MeshApproximateReset)


if "bpy" in locals():
    import importlib
    importlib.reload(ragdoll)
    importlib.reload(ragdoll_ui)
    importlib.reload(ragdoll_aux)


if __name__ == "__main__":
    register()