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

    # bpy.types.Bone.const = bpy.props.PointerProperty(type=bpy.types.PoseBoneConstraints)
    #-------- initialize custom properties to be available before ragdoll creation -------- 
    # bpy.types.Armature.ragdoll_config = bpy.props.StringProperty(name="Config File", subtype='FILE_PATH')
    # bpy.types.Armature.ctrl_rig_postfix = bpy.props.StringProperty(name="Control Rig Postfix", default=".Control")
    # bpy.types.Armature.rb_postfix = bpy.props.StringProperty(name="Ragdoll Geo Postfix", default=".RigidBody")
    # bpy.types.Armature.const_postfix = bpy.props.StringProperty(name="Rigid Body Constraint Postfix", default=".Constraint")
    # bpy.types.Armature.connect_postfix = bpy.props.StringProperty(name="Connector Postfix", default=".Connect")
    # bpy.types.Armature.rb_bone_width = bpy.props.FloatProperty(name="Rigid Body Geo Width", default=0.1)

    # bpy.types.Armature.ragdoll_type = bpy.props.EnumProperty(items=[
    #                                                         ('CONTROL', "Control Rig", "Control Rig of a RagDoll"),
    #                                                         ('DEFORM', "Control Rig", "Control Rig of a RagDoll"),
    #                                                         ('None', "Control Rig", "Control Rig of a RagDoll")                                              
    #                                                         ], default='None')
    
    # bpy.types.Armature.rigid_body_collection = bpy.props.PointerProperty(type=bpy.types.Collection)
    # bpy.types.Armature.rigid_body_constraint_collection = bpy.props.PointerProperty(type=bpy.types.Collection)
    # bpy.types.Armature.rigid_body_connector_collection = bpy.props.PointerProperty(type=bpy.types.Collection)


def unregister():
    # del bpy.types.Armature.ragdoll_config
    # del bpy.types.Armature.ctrl_rig_postfix
    # del bpy.types.Armature.rd_postfix
    # del bpy.types.Armature.const_postfix
    # del bpy.types.Armature.connect_postfix
    # del bpy.types.Armature.rd_bone_width
    del bpy.types.Armature.rag_doll
    del bpy.types.PoseBoneConstraints.ragdoll_bone_constraint_type

    bpy.utils.register_class(RagDollSettingsPanel)
    bpy.utils.unregister_class(RagDollCollectionsPanel)
    bpy.utils.unregister_class(RagDollPostfixesPanel)
    bpy.utils.unregister_class(RagDollPanel)
    bpy.utils.unregister_class(AddRigidBodyConstraintsOperator)
    bpy.utils.unregister_class(AddRagDollOperator)
    bpy.utils.unregister_class(RemoveRagDollOperator)
    bpy.utils.unregister_class(UpdateRagDollOperator)
    bpy.utils.unregister_class(OT_TextBrowse)
    
if __name__ == "__main__":
    register()
    
