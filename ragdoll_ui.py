
import bpy
import sys
sys.path.append("/home/schnollie/Work/bpy/ragdoll_tools")
from ragdoll_aux import rb_constraint_collection_set, load_text

from ragdoll import rag_doll_create, rag_doll_remove, rag_doll_update, wobbles_update
from bpy_extras.io_utils import ImportHelper
import os


class OT_TextBrowse(bpy.types.Operator, ImportHelper): 
    bl_idname = "text.open_filebrowser" 
    bl_label = "Open the file browser to open config" 
    filter_glob: bpy.props.StringProperty( 
        default='*.json;', 
        options={'HIDDEN'} 
        ) 
    
    def execute(self, context): 
        load_text(context, self.filepath)
        context.view_layer.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class AddRigidBodyConstraintsOperator(bpy.types.Operator):
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


class AddRagDollOperator(bpy.types.Operator):
    """Creates Ragdoll objects for selected Armature"""
    bl_idname = "armature.ragdoll_add"
    bl_label = "Add Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # main(context.object.data.ragdoll_config)
        rag_doll_create(context.object)
        
        return {'FINISHED'}


class RemoveRagDollOperator(bpy.types.Operator):
    """Removes Ragdoll from selected Armature"""
    bl_idname = "armature.ragdoll_remove"
    bl_label = "Remove Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rag_doll_remove(context.object)
        
        return {'FINISHED'}


class UpdateRagDollOperator(bpy.types.Operator):
    """Update selected Armature's RagDoll"""
    bl_idname = "armature.ragdoll_update"
    bl_label = "Update Ragdoll"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rag_doll_update(context)
        return {'FINISHED'}


class UpdateWobblesOperator(bpy.types.Operator):
    """Update selected Armature's RagDoll"""
    bl_idname = "armature.wobbles_update"
    bl_label = "Update Wobbles"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wobbles_update(context)
        return {'FINISHED'}




class RagDollCollectionsPanel(bpy.types.Panel):
    """Subpanel to Ragdoll"""
    bl_label = "Collections"
    bl_idname = "OBJECT_PT_ragdollcollections"
    bl_parent_id = "OBJECT_PT_ragdoll"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:         
            layout = self.layout
            row = layout.row()
            split = row.split(factor=0.25)
            col_0 = split.column()
            col_1 = split.column()
            col_0.label(text="Geometry")
            col_1.prop(context.armature.ragdoll,"rigid_bodies", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_2 = split.column()
            col_3 = split.column()
            col_2.label(text="Constraints")
            col_3.prop(context.armature.ragdoll,"constraints", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Connectors")
            col_5.prop(context.armature.ragdoll,"connectors", text="")
        

class RagDollSuffixesPanel(bpy.types.Panel):
    """Naming Suffixes for Ragdoll"""
    bl_label = "Postifxes"
    bl_idname = "OBJECT_PT_ragdollsuffixes"
    bl_parent_id = "OBJECT_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints:

            layout = self.layout
            row = layout.row()
            
            split = row.split(factor=0.25)
            col_0 = split.column()
            col_1 = split.column()
            col_0.label(text="Control Rig")
            col_1.prop(context.armature.ragdoll,"ctrl_rig_suffix", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_2 = split.column()
            col_3 = split.column()
            col_2.label(text="Geometry")
            col_3.prop(context.armature.ragdoll,"rb_suffix", text="")
            
            row = layout.row()
            split = row.split(factor=0.25)
            col_4 = split.column()
            col_5 = split.column()
            col_4.label(text="Constraints")
            col_5.prop(context.armature.ragdoll,"const_suffix", text="")

            row = layout.row()
            split = row.split(factor=0.25)
            col_6 = split.column()
            col_7 = split.column()
            col_6.label(text="Connectors")
            col_7.prop(context.armature.ragdoll,"connect_suffix", text="")



class RagDollPanel(bpy.types.Panel):
    """Creates a Panel in the Object Data properties window"""
    bl_label = "Ragdoll"
    bl_idname = "OBJECT_PT_ragdoll"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        obj = context.object
        if obj.type == 'ARMATURE':
            layout = self.layout

            if not context.scene.rigidbody_world:
                box = layout.box()
                row = box.row()
                row.label(text="Please add rigid body world first.", icon="ERROR")
                row = box.row()
                row.operator("rigidbody.world_add")
                
            elif not context.scene.rigidbody_world.constraints:
                box = layout.box()
                row = box.row()
                row.label(text="Please add rigid body constraints first.", icon="ERROR")
                row = box.row()
                row.operator("scene.rbconstraints")

            else:
                if context.object.type == 'ARMATURE':
                    if context.scene.rigidbody_world and context.scene.rigidbody_world.constraints: 
                        layout = self.layout        
                        box = layout.box()

                        row = box.row()
                        split = row.split(factor=0.25)
                        col_1 = split.column()
                        col_2 = split.column()
                        col_1.label(text="Rig Type")
                        if context.armature.ragdoll.initialized:
                            col_2.label(text=context.armature.ragdoll.type)
                        else:
                            col_2.prop(context.armature.ragdoll,"type", text="")
                        

                        row = box.row()
                        split = row.split(factor=0.25)
                        col_1 = split.column()
                        col_2 = split.column()
                        col_1.label(text="Config")
                        if context.armature.ragdoll.type == 'CONTROL' or not context.armature.ragdoll.control_rig:
                            col_2.prop(context.armature.ragdoll,"config", text="")
                        else:
                            col_2.prop(context.armature.ragdoll.control_rig.data.ragdoll,"config", text="")

                        row.operator("text.open_filebrowser", text="", icon='FILEBROWSER')
                        
                        box = layout.box()
                        row = box.row()
                        row.label(text="Geometry")
                        row = box.row()
                        row.prop(context.armature.ragdoll, "rb_bone_width_relative", text="Relative Bone Width")
                        row = box.row()
                        row.prop(context.armature.ragdoll, "rb_bone_width_min", text="Minimum Width")
                        row.enabled = False

                        row = box.row()
                        row.prop(context.armature.ragdoll, "rb_bone_width_max", text="Maximum Width")
                        row.enabled = False
                        
                        if context.armature.ragdoll.initialized == False:
                            row = layout.row()
                            row.operator("armature.ragdoll_add", text="Create Ragdoll")
                        else:
                            row = layout.row()
                            split = layout.split(factor=0.33)
                            col_1 = split.column()
                            col_2 = split.column()
                            col_1_row_0 = col_1.row()
                            col_1_row_0.prop(context.object.data.ragdoll, "kinematic", text="Animated")
                            col_2_row_0 = col_2.row()
                            col_2_row_0.prop(context.armature.ragdoll, "kinematic_influence", text="Override")

                            row = layout.row()
                            row.prop(context.armature.ragdoll, "wobble", text="Wobble")
                            
                            split = layout.split(factor=0.33)
                            col_1 = split.column()
                            col_2 = split.column()
                            
                            
                            
                            col_1_row_2 = col_1.row()
                            col_1_row_2.prop(context.armature.ragdoll, "wobble_restrict_linear", text="")

                            col_1_row_3 = col_1.row()
                            col_1_row_3.prop(context.armature.ragdoll, "wobble_restrict_angular", text="")

                            col_2_row_0 = col_2.row()
                            col_2_row_1 = col_2.row()
                            col_2_row_1.prop(context.armature.ragdoll, "wobble_distance", text="Distance")

                            col_2_row_2 = col_2.row()
                            col_2_row_2.prop(context.armature.ragdoll, "wobble_rotation", text="Rotation")

                            col_2_row_3 = col_2.row()
                            col_2_row_3.operator("armature.wobbles_update", text="Update")

                            if context.armature.ragdoll.wobble == False:
                                col_1.enabled = False
                                col_2.enabled = False
                            else:
                                col_1.enabled = True
                                col_2.enabled = True

                            if context.armature.ragdoll.wobble_restrict_linear == False:
                                col_2_row_1.enabled = False
                            else:
                                col_2_row_1.enabled = True
                            
                            if context.armature.ragdoll.wobble_restrict_angular == False:
                                col_2_row_2.enabled = False
                            else:
                                col_2_row_2.enabled = True
                            
                            
                            
                            # row2 = col_2.row()
                            # row2.prop(context.armature.ragdoll, "kinematic_influence", text="Override")
                            # row3 = col_2.row()
                            # row3.prop(context.armature.ragdoll, "wobble_restrict_linear", text="")
                            # row3.prop(context.armature.ragdoll, "wobble_distance", text="Distance")
                            # row4 = col_2.row()
                            # row4.prop(context.armature.ragdoll, "wobble_restrict_angular", text="")
                            # row4.prop(context.armature.ragdoll, "wobble_rotation", text="Rotation")

                            
                            # row1.enabled = not context.armature.ragdoll.kinematic
                                

                            # if context.armature.ragdoll.wobble == False:
                            #     row2.enabled = False
                            #     row3.enabled = False
                            # else:
                            #     row2.enabled = True
                            #     row3.enabled = True


                            row = layout.row()
                            row = layout.row()
                            row.operator("armature.ragdoll_update", text="Update Ragdoll")
                            row.operator("armature.ragdoll_remove", text="Remove Ragdoll")
                    
