import bpy
from blender_ragdoll.utils import rb_constraint_collection_set, load_text, config_create, force_update_drivers, deselect_all, select_set_active
from bpy_extras.io_utils import ImportHelper

class OBJECT_OT_TextBrowseImport(bpy.types.Operator, ImportHelper): 
    bl_idname = "text.import_filebrowser" 
    bl_label = "Open the file browser to open config" 
    filter_glob: bpy.props.StringProperty( 
        default='*.json;', 
        options={'HIDDEN'} 
        ) 
    
    def execute(self, context): 
        load_text(context, self.filepath, None)
        context.view_layer.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

class OBJECT_OT_RagdollJsonAdd(bpy.types.Operator): 
    bl_idname = "text.json_create" 
    bl_label = "New Text"
    bl_options = {'UNDO'}
      
    def execute(self, context): 
        config = config_create(context.object)
        load_text(context, None, config)
        return {'FINISHED'}
    

class OBJECT_OT_AddRigidBodyConstraints(bpy.types.Operator):
    """Creates an Operator to add Rigid Body Constraint Group"""
    bl_idname = "scene.rbconstraints"
    bl_label = "Add Rigid Body Constraints"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rb_constraint_collection_set('RigidBodyConstraints')
        bpy.context.view_layer.update()
        return {'FINISHED'}


class OBJECT_OT_AddRagDoll(bpy.types.Operator):
    """Creates Ragdoll objects for selected Armature"""
    bl_idname = "armature.ragdoll_add"
    bl_label = "Add Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            return True
            # TODO: cleanup
            # if not context.object.data.ragdoll.initialized:
            #     return True
        else:
            return False

    def execute(self, context):
        context.object.data.ragdoll.new(context)
        bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.update()
        return {'FINISHED'}
    

class OBJECT_OT_ExtendRagDoll(bpy.types.Operator):
    """Creates Ragdoll objects for selected Armature"""
    bl_idname = "armature.ragdoll_extend"
    bl_label = "Extend Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.initialized:
                return True
        else:
            return False

    def execute(self, context):
        # main(context.object.data.ragdoll_config)
        context.object.data.ragdoll.extend(context)
        
        return {'FINISHED'}


class OBJECT_OT_RemoveRagDoll(bpy.types.Operator):
    """Removes Ragdoll from selected Armature"""
    bl_idname = "armature.ragdoll_remove"
    bl_label = "Remove Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.object.data.ragdoll.remove(context)
        
        return {'FINISHED'}


class OBJECT_OT_UpdateRagDoll(bpy.types.Operator):
    """Update selected Armature's RagDoll Joint Constraint Limits from Text"""
    bl_idname = "armature.ragdoll_update"
    bl_label = "Update Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.initialized:
                if context.object.data.ragdoll.type == 'CONTROL':
                    if context.object.data.ragdoll.config:
                        return True
        else:
            return False

    def execute(self, context):
        context.object.data.ragdoll.update_constraints(context)
        print("Info: ragdoll constraints updated")
        return {'FINISHED'}


class OBJECT_OT_UpdateDrivers(bpy.types.Operator):
    """Update all armatures Drivers"""
    bl_idname = "armature.update_drivers"
    bl_label = "Update Drivers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        force_update_drivers(context)
        return {'FINISHED'}


class OBJECT_OT_UpdateWiggles(bpy.types.Operator):
    """Update selected Armature's RagDoll"""
    bl_idname = "armature.wiggle_update"
    bl_label = "Update Wiggles"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # wiggle_const_update(context)
        return {'FINISHED'}


class OBJECT_OT_AddWiggleDrivers(bpy.types.Operator):
    """Add drivers to wiggle constraints"""
    bl_idname = "armature.wiggle_drivers_add"
    bl_label = "Add Drivers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.object.data.ragdoll.wiggles.constraints.spring_drivers_add(context.object)
        context.object.data.ragdoll.wiggles.constraints.drivers = True
        print("Info: Added Drivers to Rigid Body Constraints' Spring Settings.")
        return {'FINISHED'}


class OBJECT_OT_RemoveWiggleDrivers(bpy.types.Operator):
    """Add drivers to wiggle constraints"""
    bl_idname = "armature.wiggle_drivers_remove"
    bl_label = "Add Drivers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.object.data.ragdoll.wiggles.constraints.spring_drivers_remove(context.object)
        context.object.data.ragdoll.wiggles.constraints.drivers = False
        
        print("Info: Removed Drivers from Rigid Body Constraints' Spring Settings.")
        return {'FINISHED'}


class OBJECT_OT_HookAdd(bpy.types.Operator):
    """Add Hook to Control Rig"""
    bl_idname = "armature.hook_add"
    bl_label = "Add Hook"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.type == 'CONTROL':
                if bpy.context.mode == 'POSE':
                    if len(bpy.context.selected_pose_bones) > 0:
                        return True
        return False
    
    def execute(self, context):
        # store current mode
        mode_init = bpy.context.mode
        
        # store selected pose bone to add hook to
        pose_bone = bpy.context.active_pose_bone
        hook_pose_bone = None
        # add hook (bone + mesh + rigid body constraint), (bone) edit mode needs to active
        if len(context.selected_pose_bones) > 1:
            hook_pose_bone = context.selected_pose_bones[1]
            hook_pose_bone.ragdoll.type = 'HOOK'

        if hook_pose_bone == None:
            bpy.ops.object.mode_set(mode='EDIT')
            hook_index = 0
            hook_bone_name = pose_bone.name + context.object.data.ragdoll.hooks.suffix + "." + str(hook_index).zfill(3)  
            
            while hook_bone_name in context.object.data.bones:
                print(hook_bone_name)
                hook_index += 1
                hook_bone_name = pose_bone.name + context.object.data.ragdoll.hooks.suffix + "." + str(hook_index).zfill(3)
            bpy.ops.armature.bone_primitive_add(name=hook_bone_name)
        
            # restore previouse mode if possible
            if mode_init != 'EDIT_ARMATURE':
                bpy.ops.object.mode_set(mode=mode_init)
            else:
                # new (pose)bone is found only after edit mode ends. 
                # bones.update() or pose.bones.update() do not change this behaviour
                bpy.ops.object.mode_set(mode='OBJECT')
                context.object.data.bones[hook_bone_name].use_deform = False

            hook_pose_bone = context.object.pose.bones[hook_bone_name]

        # set hook properties to bone
        context.object.data.ragdoll.hooks.add(context, pose_bone, hook_pose_bone)

        print("Info: Hook added")
        
        return {'FINISHED'}


class OBJECT_OT_HookRemove(bpy.types.Operator):
    """Remove Hook from Control Rig"""
    bl_idname = "armature.hook_remove"
    bl_label = "Remove Hook"
    bl_options = {'UNDO'}

    hooked_bone_name : bpy.props.StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        mode_init = context.mode
        if mode_init == 'EDIT_ARMATURE':
            mode_init = 'EDIT'

        rig = context.object
        hooked_bone = rig.pose.bones[self.hooked_bone_name]
        hook_bone = rig.pose.bones[hooked_bone.ragdoll.hook_bone_name]
        num_users = hook_bone.ragdoll.hook_users

        rig.data.ragdoll.hooks.objects_remove(context, self.hooked_bone_name)
        
        if num_users == 0:
            bpy.ops.object.mode_set(mode='EDIT')
            if hook_bone.name in context.object.data.edit_bones:
                context.object.data.ragdoll.hooks.bone_remove(context, hook_bone.name)        
        
        bpy.ops.object.mode_set(mode=mode_init)

        print("Info: Hook removed.")
        return {'FINISHED'}


class OBJECT_OT_MeshApproximate(bpy.types.Operator):
    """Approximate RagDoll Rigid Body Shapes"""
    bl_idname = "mesh.rd_approximate"
    bl_label = "Approximate Rigid Bodies"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.type == 'CONTROL':
                if context.mode == 'POSE' or context.mode == 'OBJECT':
                    if context.object.data.ragdoll.deform_mesh:
                        return True
        return False
    
    def execute(self, context):
        context.object.data.ragdoll.rigid_bodies.geometry_approximate(context)
        context.object.data.ragdoll.wiggles.update_scale(context)
        
        print("Info: Rigid Body Shapes approximated.")
        return {'FINISHED'}
    

class OBJECT_OT_MeshApproximateReset(bpy.types.Operator):
    """Reset approximate RagDoll Rigid Body Shapes"""
    bl_idname = "mesh.rd_approximate_reset"
    bl_label = "Approximate Rigid Bodies"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.type == 'CONTROL':
                if context.mode == 'POSE' or context.mode == 'OBJECT':
                    if context.object.data.ragdoll.deform_mesh:
                        return True
        return False
    
    def execute(self, context):
        context.object.data.ragdoll.rigid_bodies.approximated_reset(context)
        print("Info: Rigid Body Shapes reset.")
        return {'FINISHED'}


class Scene_OT_RigidBodyWorldAddCustom(bpy.types.Operator):
    """Add Rigid Body World, set Collection"""
    bl_idname = "rigidbody.world_add_custom"
    bl_label = "Add Rigid Body World and set collection"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.ops.rigidbody.world_add()
        if not context.scene.rigidbody_world.collection:
            if "RigidBodyWorld" in bpy.data.collections:
                context.scene.rigidbody_world.collection = bpy.data.collections["RigidBodyWorld"]
            else:
                context.scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
        print("Info: Rigid Body World added.")
        return {'FINISHED'}


class Scene_OT_RagDollControlRigSelect(bpy.types.Operator):
    """Add Rigid Body World, set Collection"""
    bl_idname = "armature.ragdoll_ctrl_select"
    bl_label = "Select Control Armature of RagDoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        control_rig = context.object.data.ragdoll.control_rig
        deselect_all(context)
        select_set_active(context, control_rig)
        return {'FINISHED'}
    

class Object_OT_RagDollNamesReplaceSubstring(bpy.types.Operator):
    """Add Rigid Body World, set Collection"""
    bl_idname = "object.name_substring_replace"
    bl_label = "Replace substring in Bone Names and RagDoll Objects"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        context.object.data.ragdoll.bone_names_substring_replace(context)
        print("Info: Object Names replaced.")
        return {'FINISHED'}


classes = ( OBJECT_OT_AddRigidBodyConstraints,
            OBJECT_OT_AddRagDoll,
            OBJECT_OT_ExtendRagDoll,
            OBJECT_OT_RemoveRagDoll,
            OBJECT_OT_UpdateRagDoll,
            OBJECT_OT_UpdateWiggles,
            OBJECT_OT_UpdateDrivers,
            OBJECT_OT_AddWiggleDrivers,
            OBJECT_OT_RemoveWiggleDrivers,
            OBJECT_OT_TextBrowseImport,
            OBJECT_OT_RagdollJsonAdd,
            OBJECT_OT_HookAdd,
            OBJECT_OT_HookRemove,
            OBJECT_OT_MeshApproximate,
            OBJECT_OT_MeshApproximateReset,
            Scene_OT_RagDollControlRigSelect,
            Object_OT_RagDollNamesReplaceSubstring,
            )

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()