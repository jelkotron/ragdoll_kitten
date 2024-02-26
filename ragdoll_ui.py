
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_aux import rb_constraint_collection_set, load_text, config_create, force_update_drivers, deselect_all, select_set_active

# from ragdoll import wiggle_const_update
# from ragdoll import wiggle_spring_drivers_add, wiggle_spring_drivers_remove
from ragdoll import RagDoll

from bpy_extras.io_utils import ImportHelper
import os


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
    """Update selected Armature's RagDoll"""
    bl_idname = "armature.ragdoll_update"
    bl_label = "Update Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object.type == 'ARMATURE':
            if context.object.data.ragdoll.initialized:
                if context.object.data.ragdoll.type == 'CONTROL':
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
        # if len(context.selected_pose_bones) > 1:
        #     hook_pose_bone = context.selected_pose_bones[1]
            # check if selected bone to hook to is armature transform target
            # if hook_pose_bone.ragdoll.rigid_body != None and hook_pose_bone.ragdoll.type != 'HOOK':
            #     hook_pose_bone = None
        if hook_pose_bone == None:
            bpy.ops.object.mode_set(mode='EDIT')
            hook_index = 0
            hook_bone_name = context.object.name + context.object.data.ragdoll.hooks.suffix + "." + str(hook_index).zfill(3)
            while hook_bone_name in context.object.data.bones:
                hook_index += 1
                hook_bone_name = context.object.name + context.object.data.ragdoll.hooks.suffix + "." + str(hook_index).zfill(3)

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

    bone_name : bpy.props.StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        mode_init = context.mode
        if mode_init == 'EDIT_ARMATURE':
            mode_init = 'EDIT'

        context.object.data.ragdoll.hooks.objects_remove(context, self.bone_name)

        bpy.ops.object.mode_set(mode='EDIT')
        
        if self.bone_name in context.object.data.edit_bones:
            context.object.data.ragdoll.hooks.bone_remove(context, self.bone_name)        
        
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

class PHYSICS_PT_RagDollConfig(bpy.types.Panel):
    """Configuration of RagDoll Constraints"""
    bl_label = "Settings"
    bl_idname = "OBJECT_PT_ragdoll_config"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    
    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized == False:
                    return True
                if context.object.data.ragdoll.type == 'CONTROL':
                    return True
                    

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        split = row.split(factor=0.33)
        col_0 = split.column()
        col_1 = split.column()

        row = layout.row()
        split = row.split(factor=0.33)
        col_0 = split.column(align=True)
        col_1 = split.column()
        config_label_row = col_0.row()
        config_row = col_1.row()

        if context.object.data.ragdoll.config and context.object.data.ragdoll.config.is_dirty:
            # config text is stored on disk but was modified in blender text editor
            if os.path.exists(context.object.data.ragdoll.config.filepath):
                config_label_row.label(text="Text (External, modified):")
            # config text is not stored on disk
            else:
                config_label_row.label(text="Text (Internal):")
        # config text is stored on disk and was not modified
        elif context.object.data.ragdoll.config:
            config_label_row.label(text="Text (External):")
        # config file is not set
        else:
            config_label_row.alignment = 'RIGHT'
            config_label_row.label(text="Text:")
        
        if context.object.data.ragdoll.type == 'CONTROL' or not context.object.data.ragdoll.control_rig:
            config_row.prop(context.object.data.ragdoll,"config", text="")
        else:
            config_row.prop(context.object.data.ragdoll.control_rig.data.ragdoll,"config", text="")


        config_row.operator("text.import_filebrowser", text="", icon='FILEBROWSER')
        config_row.operator("text.json_create", text="", icon='FILE_NEW')

        # default values for joint rigid body constraints if joint not in config or no text is supplied 
        default_label_row = col_0.row()
        default_label_row.alignment = 'RIGHT'
        default_label_row.label(text="Default Values:")
        default_values_row = col_1.row(align=True)
        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_distance", text="Distance")
        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_rotation",text="Angle")


        op_row = col_1.row()
        
        if context.object.data.ragdoll.initialized == False:
            op_row.operator("armature.ragdoll_add", text="Create", icon="ARMATURE_DATA")

        else:
            if context.object.data.ragdoll.type == 'CONTROL':
                op_row.operator("armature.ragdoll_extend", text="Extend", icon="ARMATURE_DATA")
                op_row.operator("armature.ragdoll_update", text="Update", icon="FILE_REFRESH")
            
            op_row.operator("armature.ragdoll_remove", text="Remove", icon="X")


class PHYSICS_PT_RagDollGeometry(bpy.types.Panel):
    """Configuration of RagDoll Geometry"""
    bl_label = "Geometry"
    bl_idname = "OBJECT_PT_ragdoll_geometry"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    
    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized == False:
                    return True
                if context.object.data.ragdoll.type == 'CONTROL':
                    return True
                    

    def draw(self, context):
        layout = self.layout
       
        row = layout.row()
        split = row.split(factor=0.33)
        col_0 = split.column() 
        col_1 = split.column()

        label_row = col_0.row(align=True)
        label_row.alignment = 'RIGHT'
        label_row.label(text="Relative Scale")
        prop_row = col_1.row(align=True)
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "width_relative", text="Width")
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "length_relative", text="Length")
        
        label_row = col_0.row()
        label_row.alignment = 'RIGHT'
        label_row.label(text="Width Limits")
        prop_row = col_1.row(align=True)
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "width_min", text="Minimum")
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "width_max", text="Maximum")


        if context.object.data.ragdoll.initialized:
            row = layout.row()
            row = layout.row()
            
            split = row.split(factor=0.33)
            col_0 = split.column() 
            col_1 = split.column()
            row = col_0.row()
            row.alignment = 'RIGHT'
            row.label(text="Deform Mesh")
            row = col_1.row()
            row.prop(context.object.data.ragdoll, "deform_mesh", text="")

            row = col_0.row()
            row.alignment = 'RIGHT'
            row.label(text="Offset")
            row.enabled =  context.object.data.ragdoll.deform_mesh != None
            row = col_1.row(align=True)
            row.prop(context.object.data.ragdoll, "deform_mesh_offset", index=0, text="X:")
            row.prop(context.object.data.ragdoll, "deform_mesh_offset", index=2, text="Z:")
            row.enabled =  context.object.data.ragdoll.deform_mesh != None

            row = col_0.row()
            row.alignment = 'RIGHT'
            row.label(text="Projection")
            row.enabled =  context.object.data.ragdoll.deform_mesh != None
            row = col_1.row()
            row.prop(context.object.data.ragdoll, "deform_mesh_projection_threshold", text="Threshold")
            row.enabled =  context.object.data.ragdoll.deform_mesh != None

            label_row = col_0.row()
            label_row.alignment = 'RIGHT'
            label_row.label(text="Rigid Bodies")
            label_row.enabled =  context.object.data.ragdoll.deform_mesh != None
            row = col_1.row()
            row.operator("mesh.rd_approximate", text="Approximate", icon="SNAP_ON")
            row.operator("mesh.rd_approximate_reset", text="Reset", icon="FILE_REFRESH")

    
class PHYSICS_PT_RagDollAnimation(bpy.types.Panel):
    """Configuration of RagDoll Animation"""
    bl_label = "Animated"
    bl_idname = "OBJECT_PT_ragdoll_animation"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    
    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized == True:
                    if context.object.data.ragdoll.type == 'CONTROL':
                        return True        

    def draw_header(self, context):
        self.layout.prop(context.object.data.ragdoll, "kinematic", text="")

    def draw(self, context):
        layout = self.layout
        split = layout.split(factor=0.33)
        col_1 = split.column()
        col_2 = split.column()
        anim_override_row = col_2.row()
        anim_override_row.prop(context.object.data.ragdoll, "simulation_influence", text="Override")
        anim_override_row.enabled = not context.object.data.ragdoll.kinematic


class PHYSICS_PT_RagDollWiggles(bpy.types.Panel):
    """Configuration of RagDoll Wiggles"""
    bl_label = "Wiggle"
    bl_idname = "OBJECT_PT_ragdoll_wiggles"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    
    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized == True:
                    if context.object.data.ragdoll.type == 'CONTROL':
                        return True        

    def draw_header(self, context):
        self.layout.prop(context.object.data.ragdoll.wiggles.constraints, "enabled", text="")

    def draw(self, context):
        layout = self.layout
        #------------------------ Constraint Limits ------------------------
        # use wiggles
        wiggle_limit_row = layout.row()
        wiggle_limit_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_limit_row.split(factor=0.33)
        wiggle_limit_col_0 = split.column()
        wiggle_limit_col_1 = split.column()
        
        # limit linear
        wiggle_restrict_lin_row = wiggle_limit_col_0.row()
        wiggle_restrict_lin_row.alignment = 'RIGHT'
        wiggle_restrict_lin_row.label(text="Limit Linear")
        wiggle_restrict_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_linear", text="")
        # limit angular
        wiggle_restrict_ang_row = wiggle_limit_col_0.row()
        wiggle_restrict_ang_row.alignment = 'RIGHT'
        wiggle_restrict_ang_row.label(text="Limit Angular")
        wiggle_restrict_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_angular", text="")
        # linear limits
        wiggle_limits_row = wiggle_limit_col_1.row()
        wiggle_limit_lin_row = wiggle_limits_row.row()
        wiggle_limit_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_distance", text="Distance")
        wiggle_limit_lin_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_linear
        # angular limits
        wiggle_limits_row = wiggle_limit_col_1.row()
        wiggle_limit_ang_row = wiggle_limits_row.row()
        wiggle_limit_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_rotation", text="Rotation")
        wiggle_limit_ang_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_angular

        #------------------------ Constraint Springs ------------------------
        wiggle_spring_row = layout.row()
        wiggle_spring_row.enabled = wiggle_limit_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_spring_row.split(factor=0.33)
        wiggle_spring_col_0 = split.column()
        wiggle_spring_col_1 = split.column()
        wiggle_spring_row_left_0 = wiggle_spring_col_0.row()
        wiggle_spring_row_left_0.alignment = 'RIGHT'
        wiggle_spring_row_left_0.label(text="Springs")
        wiggle_spring_row_left_0.prop(context.object.data.ragdoll.wiggles.constraints, "use_springs", text="")
        wiggle_spring_row_right_0 = wiggle_spring_col_1.row()
        wiggle_spring_row_right_0.enabled = context.object.data.ragdoll.wiggles.constraints.use_springs
        wiggle_spring_row_right_0.prop(context.object.data.ragdoll.wiggles.constraints, "stiffness", text="Stiffness")
        wiggle_spring_row_right_0.prop(context.object.data.ragdoll.wiggles.constraints, "damping", text="Damping")
        
        wiggle_spring_row_right_1 = wiggle_spring_col_1.row()
        wiggle_spring_row_right_1.enabled = context.object.data.ragdoll.wiggles.constraints.use_springs
        split = wiggle_spring_row_right_1.split(factor=0.5)
        wiggle_spring_col_0 = split.column()
        wiggle_spring_col_1 = split.column()
        wiggle_spring_add_drivers = wiggle_spring_col_0.row()
        wiggle_spring_remove_drivers = wiggle_spring_col_1.row()
        wiggle_spring_add_drivers.operator("armature.wiggle_drivers_add", text="Add Spring Drivers", icon='DECORATE_DRIVER')
        wiggle_spring_remove_drivers.operator("armature.wiggle_drivers_remove", text="Remove Drivers", icon='PANEL_CLOSE')

        #------------------------ Falloff ------------------------
        # use falloff
        wiggle_falloff_row = layout.row()
        wiggle_falloff_row.enabled = wiggle_limit_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_falloff_row.split(factor=0.33)
        wiggle_falloff_col_0 = split.column()
        wiggle_falloff_col_1 = split.column()
        wiggle_falloff_col_1.enabled = context.object.data.ragdoll.wiggles.constraints.enabled

        wiggle_falloff_checkbox_row = wiggle_falloff_col_0.row()
        wiggle_falloff_checkbox_row.alignment = 'RIGHT'
        wiggle_falloff_checkbox_row.label(text="Falloff")
        wiggle_falloff_checkbox_row.prop(context.object.data.ragdoll.wiggles.constraints, "use_falloff", text="")

        wiggle_falloff_settings_row_0 = wiggle_falloff_col_1.row()
        wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_mode", text="")
        wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_factor", text="Factor")
        wiggle_falloff_settings_row_0.enabled = context.object.data.ragdoll.wiggles.constraints.use_falloff

        wiggle_falloff_settings_row_1 = wiggle_falloff_col_1.row()
        split = wiggle_falloff_settings_row_1.split(factor=0.5)
        col_0 = split.column()
        col_1 = split.column()
        wiggle_falloff_settings_row_0 = col_1.row()
        wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_invert", text="Invert")
        wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_chain_ends", text="Ends")
        wiggle_falloff_settings_row_0.enabled = context.object.data.ragdoll.wiggles.constraints.use_falloff

                            
class PHYSICS_PT_RagDollHooks(bpy.types.Panel):
    """Configuration of RagDoll Hooks"""
    bl_label = "Hooks"
    bl_idname = "OBJECT_PT_ragdoll_hooks"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    
    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized == True:
                    if context.object.data.ragdoll.type == 'CONTROL':
                        return True        

    def draw(self, context):
        layout = self.layout

        for i in range(len(context.object.pose.bones)):
            pose_bone = context.object.pose.bones[i]
            if pose_bone.ragdoll.type == 'HOOK' and pose_bone.ragdoll.hook_constraint != None:
                hook_box = layout.box() 
                row = hook_box.row()
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "enabled", text="")
                row.label(text="%s"%pose_bone.ragdoll.hook_constraint.name)
                
                row.operator("armature.hook_remove", text="", icon='X').bone_name = pose_bone.name
                row = hook_box.row()
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "object1", text="")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "object2", text="")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.enabled

                split = hook_box.split(factor=0.333)
                l_col = split.column(align=True)
                r_col = split.column(align=True)
                l_col.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.enabled
                r_col.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.enabled

                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_lin_x", text="X Linear")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_x_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_x_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_lin_x

                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_lin_y", text="Y")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_y_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_y_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_lin_y

                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_lin_z", text="Z")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_z_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_lin_z_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_lin_z

                split = hook_box.split(factor=0.333)
                l_col = split.column(align=True)
                r_col = split.column(align=True)
                l_col.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.enabled
                r_col.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.enabled


                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_ang_x", text="X Angular")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_x_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_x_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_ang_x

                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_ang_y", text="Y")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_y_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_y_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_ang_y

                row = l_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "use_limit_ang_z", text="Z")
                row = r_col.row(align=True)
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_z_lower")
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "limit_ang_z_upper")
                row.enabled = pose_bone.ragdoll.hook_constraint.rigid_body_constraint.use_limit_ang_z


        row = layout.row()
        row.operator("armature.hook_add")


class PHYSICS_PT_RagDollNames(bpy.types.Panel):
    """Naming Suffixes for Ragdoll"""
    bl_label = "Naming"
    bl_idname = "OBJECT_PT_ragdollnames"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.type == 'CONTROL':
                    return True
                if context.object.data.ragdoll.initialized == False:
                    return True

    def draw(self, context):

            layout = self.layout
            row = layout.row()
            
            split = row.split(factor=0.33)
            col_0 = split.column()
            col_1 = split.column()

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Control Rig")
            row_1.prop(context.object.data.ragdoll,"ctrl_rig_suffix", text="")
            
            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Geometry")
            row_1.prop(context.object.data.ragdoll.rigid_bodies,"suffix", text="")
            
            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Constraints")
            row_1.prop(context.object.data.ragdoll.rigid_bodies.constraints,"suffix", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Connectors")
            row_1.prop(context.object.data.ragdoll.rigid_bodies.connectors,"suffix", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Wiggles")
            row_1.prop(context.object.data.ragdoll.wiggles,"suffix", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Wiggle Constraints")
            row_1.prop(context.object.data.ragdoll.wiggles.constraints,"suffix", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Hooks")
            row_1.prop(context.object.data.ragdoll.hooks,"suffix", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Hook Constraints")
            row_1.prop(context.object.data.ragdoll.hooks.constraints,"suffix", text="")
            
            # # cheap spacing
            row_0 = col_0.row()
            row_1 = col_1.row()

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Replace")
            row_1.prop(context.object.data.ragdoll,"substring_replace_source", text="")
            row_1.prop(context.object.data.ragdoll,"substring_replace_target", text="")
            row_1.prop(context.object.data.ragdoll,"substring_replace_suffix", text="")
            row_1.operator("object.name_substring_replace", text="", icon="EVENT_RETURN")

class PHYSICS_PT_RagDollCollections(bpy.types.Panel):
    """Subpanel to Ragdoll"""
    bl_label = "Collections"
    bl_idname = "OBJECT_PT_ragdollcollections"
    bl_parent_id = "PHYSICS_PT_ragdoll"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    @classmethod
    def poll(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:         
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.type == 'CONTROL':
                    return True
                if context.object.data.ragdoll.initialized == False:
                    return True

    def draw(self, context):
            layout = self.layout
            row = layout.row()
            split = row.split(factor=0.33)
            col_0 = split.column()
            col_1 = split.column()
            col_1.enabled = False

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Rigid Bodies")
            row_1.prop(context.object.data.ragdoll.rigid_bodies,"collection", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Constraints")
            row_1.prop(context.object.data.ragdoll.rigid_bodies.constraints,"collection", text="")
            
            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Connectors")
            row_1.prop(context.object.data.ragdoll.rigid_bodies.connectors,"collection", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Wiggles")
            row_1.prop(context.object.data.ragdoll.wiggles,"collection", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Wiggle Constraints")
            row_1.prop(context.object.data.ragdoll.wiggles.constraints,"collection", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Hooks")
            row_1.prop(context.object.data.ragdoll.hooks,"collection", text="")

            row_0 = col_0.row()
            row_0.alignment = 'RIGHT'
            row_1 = col_1.row()
            row_0.label(text="Hook Constraints")
            row_1.prop(context.object.data.ragdoll.hooks.constraints,"collection", text="")

            row = layout.row()
            split = row.split(factor=0.33)
            col_0 = split.column()
            col_1 = split.column()
            row_info = col_1.row()
            row_info.label(text="Info: Display only, RagDoll Collections Locked.")
            
        
class PHYSICS_PT_RagDoll(bpy.types.Panel):
    """Creates a Panel in the Object Data properties window"""
    bl_label = "RagDoll"
    bl_idname = "PHYSICS_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    @classmethod
    def poll(self, context):            
        if context.object.type == 'ARMATURE':
            return True
        if context.object.type == 'MESH':
            if context.object.ragdoll_object_type == 'RIGID_BODY_PRIMARY':
                return True
   
    def draw(self, context):

        if not context.scene.rigidbody_world or not context.scene.rigidbody_world.constraints: 
            layout = self.layout
            if not context.scene.rigidbody_world:
                row = layout.row()
                row.label(text="Please add rigid body world", icon="ERROR")
                row = layout.row()
                row.operator("rigidbody.world_add_custom", text="Add Rigid Body World")
                
            elif not context.scene.rigidbody_world.constraints:
                row = layout.row()
                row.label(text="Please add rigid body constraints", icon="ERROR")
                row = layout.row()
                row.operator("scene.rbconstraints")

        else:
            if context.object.type == 'ARMATURE':
                if context.object.data.ragdoll.initialized:
                    if context.object.data.ragdoll.type == 'DEFORM':
                        layout = self.layout
                        info_row = layout.row()
                        info_row.label(text="Please select Control Armature for RagDoll Settings")
                        op_row_0 = layout.row()
                        op_row_0.operator("armature.ragdoll_ctrl_select", text="Select Armature ", icon="ARMATURE_DATA")
                        op_row_1 = layout.row()
                        op_row_1.operator("armature.ragdoll_remove", text="Remove Ragdoll", icon="X")
                    
            elif context.object.type == 'MESH':
                layout = self.layout
                row = layout.row()
                split = row.split(factor=0.4)
                col_0 = split.column()
                col_1 = split.column()
                label_row = col_0.row()
                label_row.label(text="Protect:")
                prop_row = col_1.row()
                prop_row.prop(context.object, "ragdoll_protect_approx", text="Approximation") 
                prop_row.prop(context.object, "ragdoll_protect_custom", text="Custom Shape") 


