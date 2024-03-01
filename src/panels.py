
import bpy
import os

class PHYSICS_PT_RagDollConfig(bpy.types.Panel):
    """Configuration of RagDoll Constraints"""
    bl_label = "Constraints"
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
        config_label_row.alignment = 'RIGHT'
        config_row = col_1.row()

        if context.object.data.ragdoll.config and context.object.data.ragdoll.config.is_dirty:
            # config text is stored on disk but was modified in blender text editor
            if os.path.exists(context.object.data.ragdoll.config.filepath):
                config_label_row.label(text="JSON (External, modified)")
            # config text is not stored on disk
            else:
                config_label_row.label(text="JSON (Internal, modified)")
        # config text is stored on disk and was not modified
        elif context.object.data.ragdoll.config:
            config_label_row.label(text="JSON  (External)")
        # config file is not set
        else:
            config_label_row.alignment = 'RIGHT'
            config_label_row.label(text="JSON")
        
        if context.object.data.ragdoll.type == 'CONTROL' or not context.object.data.ragdoll.control_rig:
            config_row.prop(context.object.data.ragdoll,"config", text="")
        else:
            config_row.prop(context.object.data.ragdoll.control_rig.data.ragdoll,"config", text="")


        config_row.operator("text.import_filebrowser", text="", icon='FILEBROWSER')
        config_row.operator("text.json_create", text="", icon='FILE_NEW')
        config_row.operator("armature.ragdoll_update", text="", icon="FILE_REFRESH")

        # default values for joint rigid body constraints if joint not in config or no text is supplied 
        default_label_row = col_0.row()
        default_label_row.alignment = 'RIGHT'
        default_label_row.label(text="Default Values")
        default_values_row = col_1.row(align=True)
        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_distance", text="Distance")
        default_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "default_rotation",text="Angle")


        size_label_row = col_0.row()
        size_label_row.alignment = 'RIGHT'
        size_label_row.label(text="Display Size")
        size_values_row = col_1.row(align=True)
        size_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "scale_factor", text="Factor")
        size_values_row.prop(context.object.data.ragdoll.rigid_bodies.constraints, "scale_offset", text="Offset")


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
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "width_min", text="Min")
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "width_max", text="Max")

        label_row = col_0.row()
        label_row.alignment = 'RIGHT'
        label_row.label(text="Viewport Display")
        prop_row = col_1.row(align=True)
        prop_row.prop(context.object.data.ragdoll.rigid_bodies, "display_type", text="")
        
        

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
    bl_options = {'DEFAULT_CLOSED'}
    
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
    bl_options = {'DEFAULT_CLOSED'}

    
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
        top_row = layout.row()
        split = top_row.split(factor=0.33)
        wiggle_display_l = split.column()
        wiggle_display_r = split.column()

        wigge_display_label = wiggle_display_l.row()
        wigge_display_label.alignment = 'RIGHT'
        wigge_display_label.label(text="Display As")

        wigge_display = wiggle_display_r.row()
        wigge_display.prop(context.object.data.ragdoll.wiggles, "display_type", text="")


        wiggle_settings_row = layout.row()
        # wiggle_settings_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_settings_row.split(factor=0.33)
        wiggle_options_l = split.column()
        wiggle_options_r = split.column()
        
        wigge_scale_label = wiggle_options_l.row()
        wigge_scale_label.alignment = 'RIGHT'
        wigge_scale_label.label(text="Scale")
        wigge_scale = wiggle_options_r.row()
        wigge_scale.prop(context.object.data.ragdoll.wiggles, "scale_relative", text="")

        wiggle_limits_row = layout.row()
        wiggle_limits_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_limits_row.split(factor=0.33)
        wiggle_options_l = split.column()
        wiggle_options_r = split.column()

        # limit linear
        wiggle_restrict_lin_row = wiggle_options_l.row()
        wiggle_restrict_lin_row.alignment = 'RIGHT'
        wiggle_restrict_lin_row.label(text="Limit Linear")
        wiggle_restrict_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_linear", text="")
        # limit angular
        wiggle_restrict_ang_row = wiggle_options_l.row()
        wiggle_restrict_ang_row.alignment = 'RIGHT'
        wiggle_restrict_ang_row.label(text="Limit Angular")
        wiggle_restrict_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "restrict_angular", text="")
        # linear limits
        wiggle_limits_row = wiggle_options_r.row()
        wiggle_limit_lin_row = wiggle_limits_row.row()
        wiggle_limit_lin_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_distance", text="Distance")
        wiggle_limit_lin_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_linear
        # angular limits
        wiggle_limits_row = wiggle_options_r.row()
        wiggle_limit_ang_row = wiggle_limits_row.row()
        wiggle_limit_ang_row.prop(context.object.data.ragdoll.wiggles.constraints, "default_rotation", text="Rotation")
        wiggle_limit_ang_row.enabled = context.object.data.ragdoll.wiggles.constraints.restrict_angular

        #------------------------ Constraint Springs ------------------------
        wiggle_spring_row = layout.row()
        wiggle_spring_row.enabled = context.object.data.ragdoll.wiggles.constraints.use_springs and context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_spring_row.split(factor=0.33)
        wiggle_spring_col_0 = split.column()
        wiggle_spring_col_1 = split.column()
        wiggle_spring_row_left_0 = wiggle_spring_col_0.row()
        wiggle_spring_row_left_0.alignment = 'RIGHT'
        wiggle_spring_row_left_0.label(text="Springs")
        wiggle_spring_row_left_0.prop(context.object.data.ragdoll.wiggles.constraints, "use_springs", text="")
        wiggle_spring_row_right_0 = wiggle_spring_col_1.row()
       
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
        # use falloff
        wiggle_falloff_row = layout.row()
        wiggle_falloff_row.enabled = context.object.data.ragdoll.wiggles.constraints.enabled
        split = wiggle_falloff_row.split(factor=0.33)
        wiggle_falloff_col_0 = split.column()
        wiggle_falloff_col_1 = split.column()
        
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
    bl_options = {'DEFAULT_CLOSED'}
    
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
            if pose_bone.ragdoll.hook_bone_name != '' and pose_bone.ragdoll.hook_constraint != None:
                hook_box = layout.box() 
                row = hook_box.row()
                row.prop(pose_bone.ragdoll.hook_constraint.rigid_body_constraint, "enabled", text="")
                txt = pose_bone.name.rstrip(".0123456789%s").replace(context.object.data.ragdoll.hooks.suffix, "")
                row.label(text=txt)
                
                row.operator("armature.hook_remove", text="", icon='X').hooked_bone_name = pose_bone.name
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
            if context.object.ragdoll.object_type == 'RIGID_BODY_PRIMARY':
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

                    elif context.object.data.ragdoll.type == 'CONTROL':
                        layout = self.layout
                        row = layout.row()
                        split = layout.split(factor=0.33)
                        l_row = split.column().row()
                        r_row = split.column().row(align=True)
                        r_row.operator("armature.ragdoll_extend", text="Extend", icon="ARMATURE_DATA")
                        r_row.operator("armature.ragdoll_remove", text="Remove", icon="FILE_REFRESH")

                else:
                    layout = self.layout
                    row = layout.row()
                    split = layout.split(factor=0.33)
                    l_col = split.column()
                    r_col = split.column()
                    r_col.operator("armature.ragdoll_add", text="Create", icon="ARMATURE_DATA")


                    
            elif context.object.type == 'MESH':
                layout = self.layout
                row = layout.row()
                split = row.split(factor=0.4)
                col_0 = split.column()
                col_1 = split.column()
                label_row = col_0.row()
                label_row.label(text="Protect:")
                prop_row = col_1.row()
                prop_row.prop(context.object.ragdoll, "protect_approx", text="Approximation") 
                prop_row.prop(context.object.ragdoll, "protect_custom", text="Custom Shape") 

classes = (
    PHYSICS_PT_RagDoll,
    PHYSICS_PT_RagDollConfig,
    PHYSICS_PT_RagDollGeometry,
    PHYSICS_PT_RagDollAnimation,
    PHYSICS_PT_RagDollWiggles,
    PHYSICS_PT_RagDollHooks,
    PHYSICS_PT_RagDollNames,
    PHYSICS_PT_RagDollCollections
    )

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()