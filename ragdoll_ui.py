
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_aux import rb_constraint_collection_set, load_text, config_create, force_update_drivers

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
            if not context.object.data.ragdoll.initialized:
                return True
        else:
            return False

    def execute(self, context):
        # main(context.object.data.ragdoll_config)
        context.object.data.ragdoll.new()
        
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
        RagDoll.remove(context.object)
        
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
        # add hook (bone + mesh + rigid body constraint), (bone) edit mode needs to active
        bpy.ops.object.mode_set(mode='EDIT')
        hook_bone = context.object.data.ragdoll.hooks.bone_add(context, pose_bone, 0.666) # TODO: user input for hook object dimensions
        bone_name = hook_bone.name
        # restore previouse mode if possible
        if mode_init != 'EDIT_ARMATURE':
            bpy.ops.object.mode_set(mode=mode_init)
        else:
            # new (pose)bone is found only after edit mode ends. 
            # bones.update() or pose.bones.update() do not change this behaviour
            bpy.ops.object.mode_set(mode='OBJECT')

        hook_pose_bone = context.object.pose.bones[bone_name]

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
            context.scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
        print("Info: Rigid Body World added.")
        return {'FINISHED'}


class OBJECT_PT_RagDollCollections(bpy.types.Panel):
    """Subpanel to Ragdoll"""
    bl_label = "Collections"
    bl_idname = "OBJECT_PT_ragdollcollections"
    bl_parent_id = "OBJECT_PT_ragdoll"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:         
            layout = self.layout
            row = layout.row()
            split = row.split(factor=0.25)
            col_0 = split.column()
            col_1 = split.column()
            col_0.label(text="Geometry")
            col_1.prop(context.object.data.ragdoll.rigid_bodies,"collection", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_2 = split.column()
            col_3 = split.column()
            col_2.label(text="Constraints")
            col_3.prop(context.object.data.ragdoll.rigid_bodies.constraints,"collection", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Connectors")
            col_5.prop(context.object.data.ragdoll.rigid_bodies.connectors,"collection", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Wiggles")
            col_5.prop(context.object.data.ragdoll.wiggles,"collection", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Wiggle Constraints")
            col_5.prop(context.object.data.ragdoll.wiggles.constraints,"collection", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Hooks")
            col_5.prop(context.object.data.ragdoll.hooks,"collection", text="")
        

class OBJECT_PT_RagDollSuffixes(bpy.types.Panel):
    """Naming Suffixes for Ragdoll"""
    bl_label = "Suffixes"
    bl_idname = "OBJECT_PT_ragdollsuffixes"
    bl_parent_id = "OBJECT_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:

            layout = self.layout
            row = layout.row()
            
            split = row.split(factor=0.25)
            col_0 = split.column()
            col_1 = split.column()
            col_0.label(text="Control Rig")
            col_1.prop(context.object.data.ragdoll,"ctrl_rig_suffix", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_2 = split.column()
            col_3 = split.column()
            col_2.label(text="Geometry")
            col_3.prop(context.object.data.ragdoll.rigid_bodies,"suffix", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Constraints")
            col_5.prop(context.object.data.ragdoll.rigid_bodies.constraints,"suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Connectors")
            col_7.prop(context.object.data.ragdoll.rigid_bodies.connectors,"suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Wiggles")
            col_7.prop(context.object.data.ragdoll.wiggles,"suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Wiggle Constraints")
            col_7.prop(context.object.data.ragdoll.wiggles.constraints,"suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Hooks")
            col_7.prop(context.object.data.ragdoll.hooks,"suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Hook Constraints")
            col_7.prop(context.object.data.ragdoll.hooks.constraints,"suffix", text="")



class OBJECT_PT_RagDoll(bpy.types.Panel):
    """Creates a Panel in the Object Data properties window"""
    bl_label = "Ragdoll"
    bl_idname = "OBJECT_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):
        obj = context.object
        if obj.type == 'ARMATURE':
            layout = self.layout

            if not context.scene.rigidbody_world:
                box = layout.box()
                row = box.row()
                row.label(text="Please add rigid body world first.", icon="ERROR")
                row = box.row()
                row.operator("rigidbody.world_add_custom", text="Add Rigid Body World")
                
            elif not context.scene.rigidbody_world.constraints:
                box = layout.box()
                row = box.row()
                row.label(text="Please add rigid body constraints first.", icon="ERROR")
                row = box.row()
                row.operator("scene.rbconstraints")

            else:
                if context.object.type == 'ARMATURE' and context.object.data.ragdoll != None:
                    if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints: 
                        layout = self.layout        

                        #-------- Config --------
                        config_box = layout.box()
                        config_header_row = config_box.row()
                        config_header_row.label(text="Constraints")
                        row = config_box.row()
                        split = row.split(factor=0.33)
                        col_0 = split.column()
                        col_1 = split.column()

                        row = config_box.row()
                        split = row.split(factor=0.33)
                        col_0 = split.column(align=True)
                        col_1 = split.column()
                        config_label_row = col_0.row()
                        config_text_row = col_1.row()
                        
                        # TODO: fix this mess
                        if context.object.data.ragdoll.config and context.object.data.ragdoll.config.is_dirty:
                            if os.path.exists(context.object.data.ragdoll.config.filepath):
                                config_label_row.label(text="Text (External, modified):")
                            else:
                                config_label_row.label(text="Text (Internal):")

                        elif context.object.data.ragdoll.config:
                            config_label_row.label(text="Text (External):")

                        else:
                            config_label_row.label(text="Text:")
                        
                        if context.object.data.ragdoll.type == 'CONTROL' or not context.object.data.ragdoll.control_rig:
                            config_text_row.prop(context.object.data.ragdoll,"config", text="")
                        else:
                            config_text_row.prop(context.object.data.ragdoll.control_rig.data.ragdoll,"config", text="")

                        config_text_row.operator("text.import_filebrowser", text="", icon='FILEBROWSER')
                        config_text_row.operator("text.json_create", text="", icon='FILE_NEW')

                        default_label_row = col_0.row()
                        default_label_row.label(text="Default Values:")
                        default_values_row = col_1.row(align=True)
                        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_distance", text="Distance")
                        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_rotation",text="Angle")

                        text_ops_row = col_1.row()
                        if context.object.data.ragdoll.initialized == False:
                            text_ops_row.operator("armature.ragdoll_add", text="Create Ragdoll")
                        else:
                            split = text_ops_row.split(factor=0.5)
                            update_rd_row = split.column().row()
                            # update_drivers_row = split.column().row()
                            delete_ragdoll_row = split.column().row()

                            update_rd_row.operator("armature.ragdoll_update", text="Update Ragdoll")
                            # update_drivers_row.operator("armature.update_drivers", text="Update Drivers")
                            delete_ragdoll_row.operator("armature.ragdoll_remove", text="Remove Ragdoll")

                        #-------- Geometry --------
                        if context.object.data.ragdoll.initialized:
                            if context.object.data.ragdoll.type == 'CONTROL':
                                geo_box = layout.box()
                                row = geo_box.row()
                                row.label(text="Geometry")
                                
                                row = geo_box.row()
                                row.prop(context.object.data.ragdoll.rigid_bodies, "width_relative", text="Relative Width")
                                row.prop(context.object.data.ragdoll.rigid_bodies, "length_relative", text="Relative Length")
                                
                                row = geo_box.row()
                                row.prop(context.object.data.ragdoll.rigid_bodies, "width_min", text="Minimum Width")
                                row.prop(context.object.data.ragdoll.rigid_bodies, "width_max", text="Maximum Width")

                                row = geo_box.row()
                                split = row.split(factor=0.33)
                                col_0 = split.column()
                                col_1 = split.column()
                                row = col_0.row()
                                row.label(text="Target Mesh:")
                                row = col_1.row()
                                row.prop(context.object.data.ragdoll, "deform_mesh", text="")


                                row = col_0.row()
                                row.label(text="Offset:")
                                row = col_1.row(align=True)
                                row.prop(context.object.data.ragdoll, "deform_mesh_offset", index=0, text="X:")
                                row.prop(context.object.data.ragdoll, "deform_mesh_offset", index=2, text="Z:")
                                
                                row = col_0.row()
                                row.label(text="Projection:")

                                row = col_1.row()
                                row.prop(context.object.data.ragdoll, "deform_mesh_projection_threshold", text="Threshold:")
                                
                                row = col_1.row()
                                row.operator("mesh.rd_approximate")

                                row = col_1.row()
                                row.operator("mesh.rd_approximate_reset", text="Reset")


                        if context.object.data.ragdoll.initialized == True:
                            if context.object.data.ragdoll.type == 'DEFORM':
                                row = layout.row()
                                row.label(text="Info: Please select Control Armature for RagDoll Controls: %s"%context.object.data.ragdoll.control_rig.name)
                                
                            else:
                                #-------- Animation --------
                                animated_box = layout.box()
                                row = animated_box.row()
                                row.label(text="Animation")
                                split = animated_box.split(factor=0.33)
                                col_1 = split.column()
                                col_2 = split.column()
                                kinematic_row = col_1.row()
                                kinematic_row.prop(context.object.data.ragdoll, "kinematic", text="Animated")
                                anim_override_row = col_2.row()
                                anim_override_row.prop(context.object.data.ragdoll, "simulation_influence", text="Override")

                                #-------- Wiggle --------
                                wiggle_box = layout.box()
                                wiggle_label_row = wiggle_box.row()
                                wiggle_label_row.label(text="Wiggle")
                                wiggle_checkbox_row = wiggle_box.row()
                                wiggle_checkbox_row.prop(context.object.data.ragdoll.wiggles.constraints, "enabled", text="Enabled")
                                
                                #------------------------ Constraint Limits ------------------------
                                wiggle_limit_row = wiggle_box.row()
                                split = wiggle_limit_row.split(factor=0.33)
                                wiggle_limit_col_0 = split.column()
                                wiggle_limit_col_1 = split.column()
                                
                                wiggle_restric_lin_row = wiggle_limit_col_0.row()
                                wiggle_restric_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_linear", text="Limit Linear")

                                wiggle_restric_ang_row = wiggle_limit_col_0.row()
                                wiggle_restric_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_angular", text="Limit Angular")

                                wiggle_limits_row = wiggle_limit_col_1.row()
                                wiggle_limit_lin_row = wiggle_limits_row.row()
                                wiggle_limit_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_distance", text="Distance")

                                wiggle_limits_row = wiggle_limit_col_1.row()
                                wiggle_limit_ang_row = wiggle_limits_row.row()
                                wiggle_limit_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_rotation", text="Rotation")
                                
                                #------------------------ Constraint Springs ------------------------
                                wiggle_spring_row = wiggle_box.row()
                                split = wiggle_spring_row.split(factor=0.33)
                                wiggle_spring_col_0 = split.column()
                                wiggle_spring_col_1 = split.column()
                                wiggle_spring_row_left_0 = wiggle_spring_col_0.row()
                                wiggle_spring_row_right_0 = wiggle_spring_col_1.row()
                                wiggle_spring_row_left_0.prop(context.object.data.ragdoll.wiggles.constraints, "use_springs", text="Springs")
                                wiggle_spring_row_right_0.prop(context.object.data.ragdoll.wiggles.constraints, "stiffness", text="Stiffness")
                                wiggle_spring_row_right_0.prop(context.object.data.ragdoll.wiggles.constraints, "damping", text="Damping")
                                
                                wiggle_spring_row_right_1 = wiggle_spring_col_1.row()
                                split = wiggle_spring_row_right_1.split(factor=0.5)
                                wiggle_spring_col_0 = split.column()
                                wiggle_spring_col_1 = split.column()
                                wiggle_spring_add_drivers = wiggle_spring_col_0.row()
                                wiggle_spring_remove_drivers = wiggle_spring_col_1.row()
                                wiggle_spring_add_drivers.operator("armature.wiggle_drivers_add", text="Add Spring Drivers", icon='DECORATE_DRIVER')
                                wiggle_spring_remove_drivers.operator("armature.wiggle_drivers_remove", text="Remove Drivers", icon='PANEL_CLOSE')

                                #------------------------ Falloff ------------------------
                                wiggle_falloff_row = wiggle_box.row()
                                split = wiggle_falloff_row.split(factor=0.33)
                                wiggle_falloff_col_0 = split.column()
                                wiggle_falloff_col_1 = split.column()

                                wiggle_falloff_checkbox_row = wiggle_falloff_col_0.row()
                                wiggle_falloff_checkbox_row.prop(context.object.data.ragdoll.wiggles.constraints, "use_falloff", text="Falloff")

                                wiggle_falloff_settings_row_0 = wiggle_falloff_col_1.row()
                                wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_mode", text="")
                                wiggle_falloff_settings_row_0.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_factor", text="Factor")

                                wiggle_falloff_settings_row_1 = wiggle_falloff_col_1.row()
                                split = wiggle_falloff_settings_row_1.split(factor=0.5)
                                col_0 = split.column()
                                col_1 = split.column()
                                wiggle_falloff_settings_row_0b = col_0.row()
                                wiggle_falloff_settings_row_0b.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_invert", text="Invert")
                                wiggle_falloff_settings_row_0b.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_chain_ends", text="Ends")

                                #-------- Hooks --------
                                hooks = layout.box()
                                hook_header_row = hooks.row()
                                hook_header_row.label(text="Hooks")

                                for i in range(len(context.object.pose.bones)):
                                    pose_bone = context.object.pose.bones[i]
                                    if pose_bone.ragdoll.type == 'HOOK' and pose_bone.ragdoll.hook_constraint != None:
                                        hook_box = hooks.box() 
                                        row = hook_box.row()
                                        row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "enabled", text="")
                                        row.label(text="%s"%pose_bone.ragdoll.hook_constraint.name)
                                        ####################################################################################
                                        ####################################################################################
                                        ####################################################################################
                                        ####################################################################################
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


                                row = hooks.row()
                                row.operator("armature.hook_add")



                                wiggle_falloff_settings_row_1 = col_1.row()
                                wiggle_falloff_settings_row_1.prop(context.object.data.ragdoll.wiggles.constraints, "falloff_offset", text="Offset")

                                #-------- UI States --------
                                wiggle_limit_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
                                wiggle_spring_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
                                wiggle_falloff_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
                                
                                wiggle_limit_lin_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_linear
                                wiggle_limit_ang_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_angular
                                wiggle_falloff_settings_row_0.enabled = context.object.data.ragdoll.wiggles.constraints.use_falloff
                                wiggle_falloff_settings_row_1.enabled = context.object.data.ragdoll.wiggles.constraints.use_falloff
                                wiggle_falloff_settings_row_0b.enabled = context.object.data.ragdoll.wiggles.constraints.use_falloff
                                wiggle_spring_row_right_0.enabled = context.object.data.ragdoll.wiggles.constraints.use_springs
                                wiggle_spring_row_right_1.enabled = context.object.data.ragdoll.wiggles.constraints.use_springs
                                anim_override_row.enabled = not context.object.data.ragdoll.kinematic
                                wiggle_spring_add_drivers.enabled = not context.object.data.ragdoll.wiggles.constraints.drivers
                                wiggle_spring_remove_drivers.enabled = context.object.data.ragdoll.wiggles.constraints.drivers