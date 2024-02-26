import bpy
import math
import mathutils
import ragdoll_aux

#---- Polling Functions to specify subtypes for object PointerProperties ---- 
def armature_poll(self, object):
    return object.type == 'ARMATURE'

def mesh_poll(self, object):
     return object.type == 'MESH'

def empty_poll(self, object):
    return object.type == 'EMPTY'

###########################################################################################################################
################################ (Rigid Body Constraint) Properties for Empty Type Objects ################################

#------------------------ baseclass for objects used as rigid body constraints ------------------------
class RdRigidBodyConstraintsBase(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Ragdoll Ridig Body Suffix", default="", update = lambda self, context: self.update_suffix(context)) # type: ignore 
    suffix_previous: bpy.props.StringProperty(name="Previous Ragdoll Ridig Body Suffix") # type: ignore 
    
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll) # type: ignore
    deform_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll) # type: ignore
    default_distance: bpy.props.FloatProperty(name="Maximum Constraint Translation", default=0) # type: ignore
    default_rotation: bpy.props.FloatProperty(name="Maximum Constraint Rotation", subtype="ANGLE", default=math.radians(22.5)) # type: ignore
    restrict_linear: bpy.props.BoolProperty(default=True) # type: ignore
    restrict_angular: bpy.props.BoolProperty(default=True) # type: ignore

    # name, create and return an empty collection (empty as in containing no objects). properties are set in subclasses.
    def add(self, deform_rig, bones, control_rig):
        self.suffix_previous = self.suffix
        self.deform_rig = deform_rig
        self.control_rig = control_rig
        collection_name = deform_rig.name + self.suffix
        collection = ragdoll_aux.object_add_to_collection(collection_name, None)
        self.collection = collection
        return collection
    
    # add empty object to scene's rigid body constraint collection, constrain mesh objects
    def constraint_set(self, empty, mesh_1, mesh_2, constraint_type='GENERIC_SPRING', enabled = True):
        if empty.name not in bpy.context.scene.rigidbody_world.constraints.objects: 
            bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
        empty.rigid_body_constraint.type = constraint_type
        empty.rigid_body_constraint.object1 = mesh_1
        empty.rigid_body_constraint.object2 = mesh_2
        empty.rigid_body_constraint.enabled = enabled
    
    # create single empty object, apply bone's transform, return empty object  
    def add_single(self, bone, deform_rig_name = ''):
        name = deform_rig_name + "." + bone.name + self.suffix
        empty = bpy.data.objects.new(name, None)
        empty.ragdoll_object_type = "RIGID_BODY_EMPTY"
        empty.matrix_world = self.control_rig.matrix_world @ bone.matrix
        bpy.context.scene.collection.objects.link(empty)
        empty.empty_display_size = 0.1
        return empty
    
    # set parent to object, correct transform induced by parent
    def parent_set(self, child, parent, parent_bone=None):
        child.parent = parent
        if not parent_bone:
            child.parent_type = 'OBJECT'
        else:
            child.parent_type = 'BONE'
            child.parent_bone = parent_bone.name
        
        child.matrix_world @= parent.matrix_parent_inverse
        
    # set rigid body constraint restrictions & apply default values to linear and angular limits 
    def default_set(self, obj, max_lin=None, max_ang=None):
        if not max_lin:
            max_lin = self.default_distance

        if not max_ang:
            max_ang = math.degrees(self.default_rotation)

        if obj.rigid_body_constraint:
            if obj.rigid_body_constraint.type == 'GENERIC' or obj.rigid_body_constraint.type == 'GENERIC_SPRING':
                # restrict linear movement
                obj.rigid_body_constraint.use_limit_lin_x = self.restrict_linear
                obj.rigid_body_constraint.use_limit_lin_y = self.restrict_linear
                obj.rigid_body_constraint.use_limit_lin_z = self.restrict_linear
                # restrict angular movement
                obj.rigid_body_constraint.use_limit_ang_x = self.restrict_angular
                obj.rigid_body_constraint.use_limit_ang_y = self.restrict_angular
                obj.rigid_body_constraint.use_limit_ang_z = self.restrict_angular
                # limit linear movement
                obj.rigid_body_constraint.limit_lin_x_lower = -max_lin
                obj.rigid_body_constraint.limit_lin_x_upper = max_lin
                obj.rigid_body_constraint.limit_lin_y_lower = -max_lin
                obj.rigid_body_constraint.limit_lin_y_upper = max_lin
                obj.rigid_body_constraint.limit_lin_z_lower = -max_lin
                obj.rigid_body_constraint.limit_lin_z_upper = max_lin
                # limit angular movement
                obj.rigid_body_constraint.limit_ang_x_lower = math.radians(-max_ang)
                obj.rigid_body_constraint.limit_ang_x_upper = math.radians(max_ang)
                obj.rigid_body_constraint.limit_ang_y_lower = math.radians(-max_ang)
                obj.rigid_body_constraint.limit_ang_y_upper = math.radians(max_ang)
                obj.rigid_body_constraint.limit_ang_z_lower = math.radians(-max_ang)
                obj.rigid_body_constraint.limit_ang_z_upper = math.radians(max_ang) 

    # update name suffix of objects in collection
    def update_suffix(self, context):
        if self.collection:
            for obj in self.collection.objects:
                obj.name = obj.name.replace(self.suffix_previous, self.suffix)
            self.collection.name = self.collection.name.replace(self.suffix_previous, self.suffix)
            self.suffix_previous = self.suffix

#------------------------ constraints connecting mesh representations of bones ------------------------       
class RdJointConstraints(RdRigidBodyConstraintsBase):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Ragdoll Rigid Body Constraint Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Rigid Body Constraint Suffix", default=".Constraint", update=lambda self, context: super().update_suffix(context)) # type: ignore

    def add(self, deform_rig, bones, control_rig, constraint_type):
        self.deform_rig = deform_rig
        self.control_rig = control_rig
        super().add(deform_rig, bones, control_rig)

        for bone in bones:
            for child in bone.children:
                if child in bones:
                    empty = super().add_single(child, deform_rig.name)
                    ragdoll_aux.object_add_to_collection(self.collection.name, empty)
                    ragdoll_aux.object_remove_from_collection(bpy.context.scene.collection, empty)
                    super().constraint_set(empty, child.ragdoll.rigid_body, bone.ragdoll.rigid_body)
                    super().parent_set(empty, control_rig, child)
                    super().default_set(empty)
                    
                    child.ragdoll.constraint = empty
                    if child.name in control_rig.pose.bones:
                        control_rig.pose.bones[child.name].ragdoll.constraint = empty

        if control_rig.data.ragdoll.config:
            self.limits_set(self.collection, control_rig.data.ragdoll.config)
    

    def limits_set(self, collection, config):
        config_data = None
        
        if config:
            config_data = ragdoll_aux.config_load(config)
          
        for obj in collection.objects:
            if obj.rigid_body_constraint:
                constraint = obj.rigid_body_constraint
                stripped_name = obj.name.rstrip(self.suffix)       
                bone_data = None

                if config_data:
                    if "strip" in config_data:
                        for i in range(len(config_data["strip"])):
                            stripped_name = stripped_name.replace(config_data["strip"][i],"")

                    bone_data = config_data.get("bones").get(stripped_name)

                if bone_data:
                    lin_x_lower = bone_data.get("limit_lin_x_lower")
                    if lin_x_lower:
                        constraint.limit_lin_x_lower = lin_x_lower
                    lin_x_upper = bone_data.get("limit_lin_x_upper")
                    if lin_x_upper:
                        constraint.limit_lin_x_lower = lin_x_upper
                    lin_y_lower = bone_data.get("limit_lin_y_lower")
                    if lin_y_lower:
                        constraint.limit_lin_y_lower = lin_y_lower
                    lin_y_upper = bone_data.get("limit_lin_y_upper")
                    if lin_x_lower:
                        constraint.limit_lin_y_upper = lin_y_upper
                    lin_z_lower = bone_data.get("limit_lin_z_lower")
                    if lin_z_lower:
                        constraint.limit_lin_z_lower = lin_z_lower
                    lin_z_upper = bone_data.get("limit_lin_z_upper")
                    if lin_z_upper:
                        constraint.limit_lin_z_upper = lin_z_upper
                    ang_x_lower = bone_data.get("limit_ang_x_lower")
                    if ang_x_lower:
                        constraint.limit_ang_x_lower = math.radians(ang_x_lower)
                    ang_x_upper = bone_data.get("limit_ang_x_upper")
                    if ang_x_upper:
                        constraint.limit_ang_x_upper = math.radians(ang_x_upper)
                    ang_y_lower = bone_data.get("limit_ang_y_lower")
                    if ang_y_lower:
                        constraint.limit_ang_y_lower = math.radians(ang_y_lower)
                    ang_y_upper = bone_data.get("limit_ang_y_upper")
                    if ang_y_upper:
                        constraint.limit_ang_y_upper = math.radians(ang_y_upper)
                    ang_z_lower = bone_data.get("limit_ang_z_lower")
                    if lin_x_lower:
                        constraint.limit_ang_z_lower = math.radians(ang_z_lower)
                    ang_z_upper = bone_data.get("limit_ang_z_upper")
                    if ang_z_upper:
                        constraint.limit_ang_z_upper = math.radians(ang_z_upper)

                else:
                    super().default_set(obj)

#------------------------ constraints connecting mesh representations of bones to ------------------------
#------------------------ another set of meshes bound to control armature to allow -----------------------   
#------------------------ for simulation atop of animation                  
class RdWiggleConstraints(RdRigidBodyConstraintsBase):
    suffix: bpy.props.StringProperty(name="Rigid Body Constraint Suffix", default=".WiggleConstraint", update= lambda self, context: super().update_suffix(context)) # type: ignore

    enabled: bpy.props.BoolProperty(name="Use Constraints", default=False, update=lambda self, context: self.update(context)) # type: ignore
    default_distance: bpy.props.FloatProperty(name="Maximum Wiggle Translation",min=0.0, max=16.0, default=0, update=lambda self, context: self.update(context)) # type: ignore
    default_rotation: bpy.props.FloatProperty(name="Maximum Wiggle Rotation", subtype="ANGLE", min=0.0, max=math.radians(360.0), default=math.radians(0), update=lambda self, context: self.update(context)) # type: ignore
    restrict_linear: bpy.props.BoolProperty(name="Limit Wiggle Translation", default=True, update=lambda self, context: self.update(context)) # type: ignore
    restrict_angular: bpy.props.BoolProperty(name="Limit Wiggle Rotation", default=False, update=lambda self, context: self.update(context)) # type: ignore

    use_falloff: bpy.props.BoolProperty(name="Use Wiggle Falloff", default=False, update=lambda self, context: self.update(context)) # type: ignore
    falloff_invert: bpy.props.BoolProperty(name="Invert Falloff", default=False, update=lambda self, context: self.update(context)) # type: ignore
    falloff_chain_ends: bpy.props.BoolProperty(name="Chain Ends", default=True, update=lambda self, context: self.update(context)) # type: ignore
    falloff_mode: bpy.props.EnumProperty(items=[
                                                            ('LINEAR', "Linear", "Linear bone chain based falloff in wiggle"),
                                                            ('QUADRATIC', "Quadratic", "Quadratic bone chain based falloff in wiggle") 
                                                            ], default='QUADRATIC', name="Falloff Mode", update=lambda self, context: self.update(context)) # type: ignore
    
    falloff_factor: bpy.props.FloatProperty(name="wiggle_falloff_factor", min=0.0, max=10.0, default=1.0, update=lambda self, context: self.update(context)) # type: ignore
    falloff_offset: bpy.props.FloatProperty(name="wiggle_falloff_factor", min=-10.0, max=10.0, update=lambda self, context: self.update(context)) # type: ignore
    use_springs: bpy.props.BoolProperty(name="Use Springs", default=True, update=lambda self, context: self.update(context)) # type: ignore
    stiffness: bpy.props.FloatProperty(name="Stiffnesss", min=0, max=1000, update=lambda self, context: self.update(context)) # type: ignore
    damping: bpy.props.FloatProperty(name="Damping", min=0, max=1000, update=lambda self, context: self.update(context)) # type: ignore
    drivers: bpy.props.BoolProperty(name="Wiggle has Drivers", default=False) # type: ignore

    def add(self, deform_rig, bones, control_rig):
        super().add(deform_rig, bones, control_rig)
        self.control_rig = control_rig
        self.deform_rig = deform_rig

        for bone in bones:
            empty = super().add_single(bone, deform_rig.name)
            ragdoll_aux.object_add_to_collection(self.collection.name, empty)
            ragdoll_aux.object_remove_from_collection(bpy.context.scene.collection, empty)
            super().parent_set(empty, control_rig, bone)
            super().constraint_set(empty, bone.ragdoll.rigid_body, bone.ragdoll.wiggle, 'GENERIC_SPRING', self.enabled)
            super().default_set(empty, self.default_distance, self.default_rotation)
            self.enabled_driver_add(control_rig, empty)
            
            bone.ragdoll.wiggle_constraint = empty
            if control_rig.pose.bones[bone.name]: 
                control_rig.pose.bones[bone.name].ragdoll.wiggle_constraint = empty
        self.update(bpy.context)

    def enabled_driver_add(self, control_rig, obj):
        driven_value = obj.rigid_body_constraint.driver_add("enabled")
        driven_value.driver.type = 'SCRIPTED'
        driven_value.driver.expression = "enabled"
        driver_var = driven_value.driver.variables.new()
        driver_var.name = "enabled"
        driver_var.type = 'SINGLE_PROP'
        target = driver_var.targets[0]
        target.id_type = 'ARMATURE'
        target.id = control_rig.data
        target.data_path = 'ragdoll.wiggles.constraints.enabled'

    def update(self, context):
        control_rig = ragdoll_aux.validate_selection(context.object)
        if control_rig:
            if control_rig.data.ragdoll.type == 'DEFORM':
                control_rig = control_rig.data.ragdoll.control_rig
            if control_rig:
                # limits
                limit_lin = control_rig.data.ragdoll.wiggles.constraints.restrict_linear
                limit_ang = control_rig.data.ragdoll.wiggles.constraints.restrict_angular
                global_max_lin = control_rig.data.ragdoll.wiggles.constraints.default_distance
                global_max_ang = control_rig.data.ragdoll.wiggles.constraints.default_rotation
                # settings
                use_wiggle = control_rig.data.ragdoll.wiggles.constraints.enabled
                use_falloff = control_rig.data.ragdoll.wiggles.constraints.use_falloff
                use_springs = control_rig.data.ragdoll.wiggles.constraints.use_springs
                falloff_mode = control_rig.data.ragdoll.wiggles.constraints.falloff_mode
                falloff_factor = control_rig.data.ragdoll.wiggles.constraints.falloff_factor
                falloff_offset = control_rig.data.ragdoll.wiggles.constraints.falloff_offset
                falloff_invert = control_rig.data.ragdoll.wiggles.constraints.falloff_invert
                bone_level_max = control_rig.data.ragdoll.bone_level_max
                wiggle_falloff_chain_ends = control_rig.data.ragdoll.wiggles.constraints.falloff_chain_ends

                for i in range(len(control_rig.pose.bones)):
                    pbone = control_rig.pose.bones[i]
                    max_lin = global_max_lin
                    max_ang = global_max_ang
                    
                    if pbone.ragdoll.wiggle_constraint != None:
                        wiggle_const = pbone.ragdoll.wiggle_constraint.rigid_body_constraint
                        
                        if wiggle_const:
                            if not use_wiggle:
                                wiggle_const.enabled = False
                            else:
                                wiggle_const.enabled = True
                                if use_falloff:
                                    tree_level = pbone.ragdoll.tree_level
                                    bone_name = wiggle_const.object1.parent_bone
                                    
                                    visible_bones = ragdoll_aux.get_visible_posebones(control_rig)
                                    if wiggle_falloff_chain_ends == True:
                                        last_in_chain = True
                                        for child in control_rig.pose.bones[bone_name].children:
                                            if child in visible_bones:
                                                last_in_chain = False
                                        if last_in_chain:
                                            tree_level = bone_level_max 
                            
                                    if falloff_invert:
                                        # reverse falloff direction / bone chain hierarchy if desired
                                        tree_level = control_rig.data.ragdoll.bone_level_max - tree_level
                                    
                                    # define step size
                                    if falloff_mode == 'QUADRATIC':
                                        if tree_level == 0:
                                            max_lin = global_max_lin
                                        else:
                                            # base quadratic function
                                            max_lin = global_max_lin * falloff_factor * tree_level**2  + falloff_offset
                                            # inverse value
                                            if max_lin != 0:
                                                max_lin = 1/max_lin
                                            else: 
                                                max_lin = 0
                                            # scale to stepsize
                                            max_lin = max_lin * global_max_lin
                                            # clamp
                                            max_lin = min(max_lin, global_max_lin)
                                    else:
                                        # step size is divided by falloff factor to be consistent w/ control of quadratic function
                                        max_lin = global_max_lin - ((global_max_lin / bone_level_max / falloff_factor) * tree_level ) + falloff_offset 
                                        #clamp
                                        max_lin = min(max_lin, global_max_lin)

                                # modify constraints
                                if wiggle_const.type == 'GENERIC_SPRING':
                                    wiggle_const.use_limit_ang_x, wiggle_const.use_limit_ang_y, wiggle_const.use_limit_ang_z = limit_ang, limit_ang, limit_ang
                                    wiggle_const.use_limit_lin_x, wiggle_const.use_limit_lin_y, wiggle_const.use_limit_lin_z = limit_lin, limit_lin, limit_lin
                                    
                                    wiggle_const.limit_lin_x_lower, wiggle_const.limit_lin_x_upper = - max_lin, max_lin
                                    wiggle_const.limit_lin_y_lower, wiggle_const.limit_lin_y_upper = - max_lin, max_lin
                                    wiggle_const.limit_lin_z_lower, wiggle_const.limit_lin_z_upper = - max_lin, max_lin 

                                    wiggle_const.limit_ang_x_lower, wiggle_const.limit_ang_x_upper = math.degrees(- max_ang), math.degrees(max_ang)
                                    wiggle_const.limit_ang_y_lower, wiggle_const.limit_ang_y_upper = math.degrees(- max_ang), math.degrees(max_ang)
                                    wiggle_const.limit_ang_z_lower, wiggle_const.limit_ang_z_upper = math.degrees(- max_ang), math.degrees(max_ang)

                                    wiggle_const.use_spring_x = use_springs
                                    wiggle_const.use_spring_y = use_springs
                                    wiggle_const.use_spring_z = use_springs

                                    if use_springs == True:
                                        wiggle_const.spring_stiffness_x = control_rig.data.ragdoll.wiggles.constraints.stiffness
                                        wiggle_const.spring_stiffness_y = control_rig.data.ragdoll.wiggles.constraints.stiffness
                                        wiggle_const.spring_stiffness_z = control_rig.data.ragdoll.wiggles.constraints.stiffness
                                        
                                        wiggle_const.spring_damping_x = control_rig.data.ragdoll.wiggles.constraints.damping
                                        wiggle_const.spring_damping_y = control_rig.data.ragdoll.wiggles.constraints.damping
                                        wiggle_const.spring_damping_z = control_rig.data.ragdoll.wiggles.constraints.damping
                print("Info: Wiggle updated")

    def spring_drivers_add(self, control_rig):
            for obj in control_rig.data.ragdoll.wiggles.constraints.collection.objects:
                if obj.rigid_body_constraint and obj.rigid_body_constraint.type == 'GENERIC_SPRING':
                    obj.rigid_body_constraint.use_spring_x = True
                    obj.rigid_body_constraint.use_spring_y = True
                    obj.rigid_body_constraint.use_spring_z = True

                    properties = {
                        "stiffness": [
                            "spring_stiffness_x",
                            "spring_stiffness_y",
                            "spring_stiffness_z",
                            ],
                        "damping": [
                            "spring_damping_x",
                            "spring_damping_y",
                            "spring_damping_z",
                        ]
        
                    }
        
                    for key, value in properties.items():
                        for prop in value:
                            fcurve = obj.rigid_body_constraint.driver_add(prop)
                            var = fcurve.driver.variables.new()
                            var.name = key
                            var.type = 'SINGLE_PROP'
                            target = var.targets[0]
                            target.id_type = 'ARMATURE'
                            target.id = control_rig.data
                            target.data_path = 'ragdoll.wiggles.constraints.%s'%key
                            fcurve.driver.expression = key

                else:
                    print("Error: Wrong Rigid Body Constraint Type: %s"%obj.rigid_body_constraint.type)
        
    def spring_drivers_remove(self, control_rig):
        wiggle_constraints = control_rig.data.ragdoll.wiggles.constraints.collection
        for obj in wiggle_constraints.objects:
            for d in obj.animation_data.drivers:
                obj.animation_data.drivers.remove(d)

#------------------------ additional constraints created by user connecting ------------------------
#------------------------ mesh representation of bones to addional "hook" bones --------------------                        
class RdHookConstraints(RdRigidBodyConstraintsBase):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Ragdoll Hook Constraint Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Ragdoll Hook Constraint Suffix", default=".HookConstraint", update= lambda self, context: super().update_suffix(context)) # type: ignore

    def add(self, deform_rig, hook_bone, target_bone, control_rig):
        super().add(deform_rig, hook_bone, control_rig)
        self.deform_rig = deform_rig
        self.control_rig = control_rig
        empty = super().add_single(hook_bone, deform_rig.name)
        ragdoll_aux.object_add_to_collection(self.collection.name, empty)
        ragdoll_aux.object_remove_from_collection(bpy.context.scene.collection, empty)
        super().parent_set(empty, control_rig, hook_bone)
        super().constraint_set(empty, hook_bone.ragdoll.rigid_body, target_bone.ragdoll.rigid_body, 'GENERIC_SPRING', True)
        super().default_set(empty, 0.1, 22.5)
        hook_bone.ragdoll.hook_constraint = empty
        target_bone.ragdoll.hook_constraint = empty
        if target_bone.name in deform_rig.pose.bones:
            deform_rig.pose.bones[target_bone.name].ragdoll.hook_constraint = empty

#------------------------ helper objects used as target for bone transforms ------------------------
#------------------------ as rigig body objects' pivots need to centered to ------------------------
#------------------------ simulate correctly
class RdConnectors(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Ragdoll Connector Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Ragdoll Ridig Body Suffix", default=".Connect", update=lambda self, context: self.update_suffix(context)) # type: ignore
    suffix_previous: bpy.props.StringProperty(name="Previous Ragdoll Ridig Body Suffix", default=".Connect") # type: ignore

    def add(self, deform_rig, bones, control_rig):
        self.suffix_previous = self.suffix
        collection = ragdoll_aux.object_add_to_collection(deform_rig.name + self.suffix, None)
        for bone in bones:
            name = deform_rig.name + "." + bone.name + self.suffix
            empty = bpy.data.objects.new(name, None)
            empty.empty_display_size = 0.085
            empty.empty_display_type = 'SPHERE'
            collection = ragdoll_aux.object_add_to_collection(collection.name, empty)
            empty.parent = control_rig.pose.bones[bone.name].ragdoll.rigid_body
            empty.parent_type = 'OBJECT'
            empty.matrix_world = control_rig.matrix_world @ bone.matrix
            
            bone.ragdoll.connector = empty
            if bone.name in control_rig.pose.bones:
                control_rig.pose.bones[bone.name].ragdoll.connector = empty

        self.collection = collection
        control_rig.data.ragdoll.rigid_bodies.connectors.collection = collection

    def update_suffix(self, context):
        if self.collection:
            for obj in self.collection.objects:
                obj.name = obj.name.replace(self.suffix_previous, self.suffix)
            self.collection.name = self.collection.name.replace(self.suffix_previous, self.suffix)
            self.suffix_previous = self.suffix
        
#############################################################################################################
################################ Rigid Body Properties for Mesh Type Objects ################################

#------------------------ baseclass for simulated objects of ragdoll ------------------------
class SimulationMeshBase(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Geometry Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Naming Suffix", default=".RigidBody", update=lambda self, context: self.update(context)) # type: ignore
    suffix_previous: bpy.props.StringProperty(name="Previous Naming Suffix") # type: ignore
    constraints : bpy.props.PointerProperty(type=RdJointConstraints) # type: ignore
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll) # type: ignore
    deform_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll) # type: ignore

    width_min: bpy.props.FloatProperty(name="Minimum Geo Width", default=0.1, min=0.01, update=lambda self, context: self.update_width(context)) # type: ignore
    width_max: bpy.props.FloatProperty(name="Maximum Geo Width", default=0.1, min=0.0, update=lambda self, context: self.update_width(context)) # type: ignore
    width_relative: bpy.props.FloatProperty(name="Relative Geo Width", default=0.1, min=0.0, update=lambda self, context: self.update_width(context)) # type: ignore
    length_relative: bpy.props.FloatProperty(name="Relative Geo Length", default=0.9, min=0.01, update=lambda self, context: self.update_length(context)) # type: ignore


    def add(self, deform_rig, control_rig, pbones, is_hook=False):
        self.deform_rig = deform_rig
        self.control_rig = control_rig
        self.suffix_previous = self.suffix

        if isinstance(type(pbones), bpy.types.PoseBone.__class__):
            pbones = [pbones]
        rb_bones = []
        
        # set current frame to beginning of frame range # TODO: get simulation frame range for this!
        bpy.context.scene.frame_current = 1
        
        for pb in pbones:
            if pb.id_data.data.bones[pb.name].use_deform or is_hook == True:
                # add cubes to collection
                geo_name = deform_rig.name + "." + pb.name + self.suffix
                # add and scale box geometry per bone
                new_cube = ragdoll_aux.cube(1, geo_name, 'OBJECT')
                new_cube.display_type = 'WIRE'
                new_cube.ragdoll_bone_name = pb.name
                # place cube on center of bone 
                bone_matrix = pb.id_data.matrix_world @ pb.matrix
                bone_center = pb.id_data.matrix_world @ pb.center
                new_cube.matrix_world = mathutils.Matrix.LocRotScale(bone_center, bone_matrix.decompose()[1], bone_matrix.decompose()[2])

                for vert in new_cube.data.vertices:
                    vert.co[0] *= 1 / new_cube.dimensions[1] * pb.length * self.width_relative
                    vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length * self.length_relative
                    vert.co[2] *= 1 / new_cube.dimensions[1] * pb.length * self.width_relative

                # add cube to rigid body collection & set collision shape 
                bpy.context.scene.rigidbody_world.collection.objects.link(new_cube)
                new_cube.rigid_body.collision_shape = 'BOX'
                new_cube.rigid_body.kinematic = False
                rb_bones.append(new_cube)
        
        collection_name = deform_rig.name + self.suffix
        self.collection = ragdoll_aux.object_add_to_collection(collection_name, [rb_geo for rb_geo in rb_bones])
        ragdoll_aux.object_remove_from_collection(bpy.context.scene.collection, [rb_geo for rb_geo in rb_bones])
        self.scale()
        self.parents_set(control_rig)
        
        if is_hook:
            return rb_bones[0]
        else:
            return self.collection

    def kinematic_drivers_add(self, target_rig):
        for obj in self.collection.objects:
            driven_value = obj.rigid_body.driver_add("kinematic")
            driven_value.driver.type = 'SCRIPTED'
            driven_value.driver.expression = "kinematic"
            driver_var = driven_value.driver.variables.new()
            driver_var.name = "kinematic"
            driver_var.type = 'SINGLE_PROP'
            target = driver_var.targets[0]
            target.id_type = 'ARMATURE'
            target.id = target_rig.data
            target.data_path = 'ragdoll.kinematic'

    def scale(self, single_obj=None, axis='XYZ'):
        axis = ragdoll_aux.axis_string_to_index_list(axis)
        if self.width_min + self.width_max + self.width_relative > 0:
            if not single_obj:
                objects = self.collection.objects
            else:
                objects = [single_obj]

            for mesh in objects:
                if mesh:
                    bone = self.control_rig.pose.bones[mesh.ragdoll_bone_name]
                    protected = mesh.ragdoll_protect_approx
                    if bone:
   
                        for vert in mesh.data.vertices:
                            for i in range(3):
                                if i in axis:
                                    if i == 1:
                                        # reset Y dimension to 1 
                                        vert.co[i] *= abs(0.5 / vert.co[i])
                                        vert.co[i] *= bone.length * self.length_relative
                                    else:
                                        if not protected:
                                            # reset XZ dimensions to 1
                                            vert.co[i] *= abs(0.5 / vert.co[i])
                                            # clamp values to min/max
                                            width_factor = self.width_relative * bone.length

                                            if self.width_max != 0:
                                                width_factor = min(self.width_max, self.width_relative)
                                            
                                            if self.width_min != 0:
                                                width_factor = max(width_factor, self.width_min)
                        
                                            # apply new transform
                                            vert.co[i] *= width_factor

                    mesh.data.update()
                    bpy.context.view_layer.update()

        else:
            print("Error: Cannot create mesh with width of 0")

    def parents_set(self, control_rig):
        if self.collection:
            for obj in self.collection.objects:
                bone_name = obj.ragdoll_bone_name
                if bone_name in control_rig.pose.bones:
                    bone =  control_rig.pose.bones[bone_name]
                    obj.parent = control_rig
                    obj.parent_type = 'BONE'
                    obj.parent_bone = bone_name
                    
                    bone_matrix = control_rig.matrix_world @ bone.matrix
                    bone_center = control_rig.matrix_world @ bone.center
                    obj.matrix_world = control_rig.matrix_world @ bone.matrix
                    obj.matrix_world = mathutils.Matrix.LocRotScale(bone_center, bone_matrix.decompose()[1], bone_matrix.decompose()[2])
        self.control_rig = control_rig

    def geometry_approximate(self, context):
        self.approximated_reset(context)
        control_rig = context.object
        pose_bones = ragdoll_aux.get_visible_posebones(context.object)
        target = context.object.data.ragdoll.deform_mesh
        threshold = context.object.data.ragdoll.deform_mesh_projection_threshold
        offset = context.object.data.ragdoll.deform_mesh_offset
        # store pose position
        init_pose_position = control_rig.data.pose_position
        # set to rest position
        control_rig.data.pose_position = 'REST'
        context.view_layer.update()
        # snap bones' rigid body objects' face centers to target mesh surface
        if target:
            for bone in pose_bones:
                if bone.ragdoll.rigid_body:
                    ragdoll_aux.snap_rigid_body_cube(bone.ragdoll.rigid_body, target, 'XZ', threshold, offset)
                    bone.ragdoll.rigid_body.ragdoll_protect_approx = True
        # restore pose position
        control_rig.data.pose_position = init_pose_position
         
    def approximated_reset(self, context):
        control_rig = context.object
        pose_bones = ragdoll_aux.get_visible_posebones(context.object)

        for bone in pose_bones:
            mesh_obj = bone.ragdoll.rigid_body 
            if mesh_obj:
                mesh_obj.ragdoll_protect_approx = False
                mesh_obj.data = ragdoll_aux.cube(1, mesh_obj.name, 'DATA')
                self.scale(mesh_obj)
                mesh_obj.matrix_world = control_rig.matrix_world @ mathutils.Matrix.LocRotScale(bone.center, bone.matrix.decompose()[1], bone.matrix.decompose()[2])
                for child in mesh_obj.children:
                    child.matrix_world @= mesh_obj.matrix_parent_inverse

    def update_width(self, context):
        self.scale(None, 'XZ')

    def update_length(self, context):
        self.scale(None, 'Y')
    
    def update_suffix(self, context):
        if self.collection:
            for obj in self.collection.objects:
                obj.name = obj.name.replace(self.suffix_previous, self.suffix)
            self.collection.name = self.collection.name.replace(self.suffix_previous, self.suffix)
            self.suffix_previous = self.suffix
        
#------------------------ mesh representations of bones ------------------------
class RdRigidBodies(SimulationMeshBase):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Geometry Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Suffix", default=".RigidBody", update=lambda self, context: super().update_suffix(context)) # type: ignore
    constraints : bpy.props.PointerProperty(type=RdJointConstraints) # type: ignore
    connectors : bpy.props.PointerProperty(type=RdConnectors) # type: ignore

    def add(self, deform_rig, control_rig, pbones):
        super().add(deform_rig, control_rig, pbones)
        self.control_rig = control_rig
        for obj in self.collection.objects:
            obj.display_type = 'WIRE'
            obj.ragdoll_object_type = "RIGID_BODY_PRIMARY"
            bone_name = obj.ragdoll_bone_name
            if bone_name in deform_rig.pose.bones:
                deform_rig.pose.bones[bone_name].ragdoll.rigid_body = obj
            if bone_name in control_rig.pose.bones:
                control_rig.pose.bones[bone_name].ragdoll.rigid_body = obj

        super().kinematic_drivers_add(self.control_rig)

#------------------------ meshes directly bound to the control armature used ------------------------
#------------------------ as component of wiggle constraints for simulation atop of animation
class RdWiggles(SimulationMeshBase):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Ragdoll Wiggle Geometry Collection") # type: ignore
    suffix: bpy.props.StringProperty(name="Ragdoll Wiggle Geometry Suffix", default=".Wiggle", update=lambda self, context: super().update_suffix(context)) # type: ignore
    constraints : bpy.props.PointerProperty(type=RdWiggleConstraints) # type: ignore

    def add(self, deform_rig, control_rig, pbones):
        super().add(deform_rig, control_rig, pbones)
        for obj in self.collection.objects:
            obj.rigid_body.kinematic = True
            obj.ragdoll_object_type = "RIGID_BODY_WIGGLE"
            # TODO: set this elsewhere?
            obj.rigid_body.collision_collections[0] = False
            obj.rigid_body.collision_collections[19] = True
            bone_name = obj.ragdoll_bone_name
            if bone_name in deform_rig.pose.bones:
                deform_rig.pose.bones[bone_name].ragdoll.wiggle = obj
            if bone_name in control_rig.pose.bones:
                control_rig.pose.bones[bone_name].ragdoll.wiggle = obj
          
#------------------------ additional meshes created by user as component of hook constraints
class RdHooks(SimulationMeshBase):
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Ragdoll Hook Geometry") # type: ignore
    suffix: bpy.props.StringProperty(name="Ragdoll Hook Geometry Suffix", default=".Hook", update=lambda self, context: super().update_suffix(context)) # type: ignore
    constraints : bpy.props.PointerProperty(type=RdHookConstraints) # type: ignore

    def bone_add(self, context, pose_bone, length):
        if bpy.context.mode == 'EDIT_ARMATURE':
            bone_name = "RagDollHook.000" # TODO: name elsewhere
            edit_bone = context.object.data.edit_bones.new(name=bone_name)
            # head = pose_bone.matrix.decompose()[0]
            head = context.object.matrix_world @ context.scene.cursor.location
            tail = head + mathutils.Vector([0,0,length])
            setattr(edit_bone, 'use_deform', False)
            setattr(edit_bone, 'head', head)
            setattr(edit_bone, 'tail', tail)

            return edit_bone
        
    def add(self, context, pose_bone, hook_pose_bone):
        control_rig = context.object
        deform_rig = context.object.data.ragdoll.deform_rig
        obj = super().add(deform_rig, control_rig, hook_pose_bone, is_hook=True)
        obj.rigid_body.kinematic = True
        obj.ragdoll_object_type = "RIGID_BODY_HOOK"
        obj.rigid_body.collision_collections[0] = False
        obj.rigid_body.collision_collections[19] = True
        hook_pose_bone.ragdoll.rigid_body = obj
        hook_pose_bone.ragdoll.type = 'HOOK'

        if pose_bone.name in deform_rig.pose.bones:
            deform_rig.pose.bones[pose_bone.name].ragdoll.hook_mesh = obj
            deform_rig.pose.bones[pose_bone.name].ragdoll.hook_bone_name = hook_pose_bone.name
        if pose_bone.name in control_rig.pose.bones:
            control_rig.pose.bones[pose_bone.name].ragdoll.hook_mesh = obj
            control_rig.pose.bones[pose_bone.name].ragdoll.hook_bone_name = hook_pose_bone.name

        self.constraints.add(deform_rig, hook_pose_bone, pose_bone, control_rig)
        
    def objects_remove(self, context, bone_name):
        hook_constraint = context.object.pose.bones[bone_name].ragdoll.hook_constraint
        hook_mesh = context.object.pose.bones[bone_name].ragdoll.rigid_body

        ragdoll_aux.object_remove_from_collection(bpy.context.scene.rigidbody_world.collection, hook_mesh)
        ragdoll_aux.object_remove_from_collection(bpy.context.scene.rigidbody_world.constraints, hook_constraint)
        if hook_constraint:
            bpy.data.objects.remove(hook_constraint, do_unlink=True)
        if hook_mesh:
            bpy.data.objects.remove(hook_mesh, do_unlink=True)

        if bone_name in context.object.pose.bones:
            context.object.pose.bones[bone_name].ragdoll.type = 'DEFAULT'
     
    def bone_remove(self, context, edit_bone_name):
        edit_bone = context.object.data.edit_bones[edit_bone_name]
        context.object.data.edit_bones.remove(edit_bone)


#########################################################################################################################
################################ RagDoll Properties for Armature Type Objects ###########################################

#------------------------ store ragdoll related object pointers and data per bone ------------------------
class RagDollBone(bpy.types.PropertyGroup):
    is_ragdoll: bpy.props.BoolProperty(name="Part of a Ragdoll", default=False) # type: ignore
    tree_level: bpy.props.IntProperty(name="tree_level", min=0, default =0) # type: ignore
    rigid_body: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body", poll=mesh_poll) # type: ignore
    constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body Constraint", poll=empty_poll) # type: ignore
    connector: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body Connector", poll=empty_poll) # type: ignore
    wiggle: bpy.props.PointerProperty(type=bpy.types.Object, name="Wiggle", poll=mesh_poll) # type: ignore
    wiggle_constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="Wiggle Constraint", poll=empty_poll) # type: ignore
    hook_constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="Hook Constraint", poll=empty_poll) # type: ignore
    hook_mesh: bpy.props.PointerProperty(type=bpy.types.Object, name="Hook Mesh", poll=mesh_poll) # type: ignore
    hook_bone_name : bpy.props.StringProperty(name="Name of Control Bone for associated Hook") # type: ignore

    type: bpy.props.EnumProperty(items=
                                    [
                                        ('DEFAULT', "Ragdoll Bone", "RagDoll Bone of Control or Deform Rig"),
                                        ('HOOK', "Ragdoll Hook Bone in Control Rig", "Deform Rig of a RagDoll")                          
                                    ], default='DEFAULT') # type: ignore


#------------------------ main property group. constraint and rigid body groups nested inside ------------------------
class RagDoll(bpy.types.PropertyGroup):
    #-------- Object Pointers --------
    deform_rig : bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_poll) # type: ignore
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll) # type: ignore
    deform_mesh: bpy.props.PointerProperty(type=bpy.types.Object, name="Target Mesh", poll=mesh_poll) # type: ignore
    deform_mesh_offset: bpy.props.FloatVectorProperty(name="Offset", subtype='XYZ', default=(0.0, 0.0, 0.0)) # type: ignore
    deform_mesh_projection_threshold: bpy.props.FloatProperty(name="Projection Threshold", min=0.0, default=0.1) # type: ignore
    #-------- Control Rig Name Suffix --------
    ctrl_rig_suffix: bpy.props.StringProperty(default=".Control", update = lambda self, context: self.update_suffix(context)) # type: ignore
    ctrl_rig_suffix_previous: bpy.props.StringProperty() # type: ignore
    
    substring_replace_source: bpy.props.StringProperty() # type: ignore
    substring_replace_target: bpy.props.StringProperty() # type: ignore
    substring_replace_suffix: bpy.props.StringProperty() # type: ignore
    #-------- Grouped Simulation Objects and Properties -------- 
    rigid_bodies : bpy.props.PointerProperty(type=RdRigidBodies) # type: ignore
    hooks: bpy.props.PointerProperty(type=RdHooks) # type: ignore
    wiggles: bpy.props.PointerProperty(type=RdWiggles) # type: ignore

    #-------- Armature Sub Type --------
    type: bpy.props.EnumProperty(items=
                                    [   
                                        ('CONTROL', "Control Rig", "Control Rig of a RagDoll"),
                                        ('DEFORM', "Deform Rig", "Deform Rig of a RagDoll")                          
                                    ], 
                                    default='DEFORM') # type: ignore
    
    #-------- JSON Config File --------
    config: bpy.props.PointerProperty(type=bpy.types.Text) # type: ignore

    # -------- State --------
    initialized: bpy.props.BoolProperty(name="RagDoll initialized", default=False) # type: ignore
    
    # -------- Animation/Simulation switches --------
    kinematic: bpy.props.BoolProperty(name="Animated", default=False) # type: ignore
    simulation_influence: bpy.props.FloatProperty(name="Rigid Body_Influence",min=0.0, max=1.0, default=0.0) # type: ignore
   
    # -------- Hierarchy --------
    bone_level_max: bpy.props.IntProperty(name="bone_level_max", min=0, default=0) # type: ignore
 
    def new(self):
        # naming sheme
        self.ctrl_rig_suffix_previous = self.ctrl_rig_suffix
        # get selected bones. if none are selected, use all visible bones 
        bones = ragdoll_aux.get_visible_posebones(bpy.context.object)
        for b in bones:
            b.ragdoll.is_ragdoll = True
        # store bones' hierarchy level in bone prop
        self.deform_rig = ragdoll_aux.bones_tree_levels_set(bpy.context.object, bones)
        # duplicate armature to use as control rig
        self.control_rig = self.secondary_rig_add(self.deform_rig)
        # set config file if supplied
        if self.config:
            self.control_rig.data.ragdoll.config = self.config
        # add primary set of rigid bodies & constraints 
        self.control_rig.data.ragdoll.rigid_bodies.add(self.deform_rig, self.control_rig, bones)
        self.rigid_bodies.connectors.add(self.deform_rig, bones, self.control_rig)
        self.control_rig.data.ragdoll.rigid_bodies.constraints.add(self.deform_rig, bones, self.control_rig, 'GENERIC_SPRING')
        # add secondary set of rigid bodies & constraints for simulation atop of animation
        self.control_rig.data.ragdoll.wiggles.add(self.deform_rig, self.control_rig, bones)
        self.control_rig.data.ragdoll.wiggles.constraints.add(self.deform_rig, bones, self.control_rig)
        # add bone constraints to copy ragdoll's or control rig's transformations
        self.pose_constraints_add(bones)
        

        print("Info: added ragdoll")

    # read interrnal or external config file, set joints' constraints transformation limits
    def update_constraints(self, context):
        const_collection = context.object.data.ragdoll.rigid_bodies.constraints.collection
        context.object.data.ragdoll.rigid_bodies.constraints.limits_set(const_collection, context.object.data.ragdoll.config)

    # scale primary rigid bodies upon user input
    def update_geometry(self, context):
        context.object.data.ragdoll.rigid_bodies.scale()

    # delete all ragdoll related objects
    def remove(self, context):
        armature_object = context.object
        if armature_object.type == 'ARMATURE':
            if armature_object.data.ragdoll.type == 'DEFORM':
                deform_rig = armature_object
                control_rig = armature_object.data.ragdoll.control_rig

            else:
                control_rig = armature_object
                deform_rig = armature_object.data.ragdoll.deform_rig
                
            for bone in deform_rig.pose.bones:
                bone.ragdoll.is_ragdoll = False
                for const in bone.constraints:
                    if "ragdoll" in const.name.lower():
                        bone.constraints.remove(const)


            rigid_bodies = control_rig.data.ragdoll.rigid_bodies.collection
            constraints = control_rig.data.ragdoll.rigid_bodies.constraints.collection
            connectors = control_rig.data.ragdoll.rigid_bodies.connectors.collection
            wiggles = control_rig.data.ragdoll.wiggles.collection
            wiggle_constraints = control_rig.data.ragdoll.wiggles.constraints.collection
            hooks = control_rig.data.ragdoll.hooks.collection
            hook_constraints = control_rig.data.ragdoll.hooks.constraints.collection

            if bpy.context.scene.rigidbody_world:
                collection = bpy.context.scene.rigidbody_world.collection
                if rigid_bodies: 
                    ragdoll_aux.object_remove_from_collection(collection, rigid_bodies.objects)
                if wiggles: 
                    ragdoll_aux.object_remove_from_collection(collection, wiggles.objects)
                if hooks: 
                    ragdoll_aux.object_remove_from_collection(collection, hooks.objects)

            if context.scene.rigidbody_world:
                if context.scene.rigidbody_world.constraints:
                    collection = bpy.context.scene.rigidbody_world.constraints.collection_objects.data
                    rb_obj_list =  bpy.context.scene.rigidbody_world.constraints

                    if constraints: 
                        ragdoll_aux.object_remove_from_collection(collection, constraints.objects)
                        ragdoll_aux.object_remove_from_collection(rb_obj_list, constraints.objects)
                    if wiggle_constraints:
                        ragdoll_aux.object_remove_from_collection(collection, wiggle_constraints.objects)
                        ragdoll_aux.object_remove_from_collection(rb_obj_list, wiggle_constraints.objects)
                    if hook_constraints:
                        ragdoll_aux.object_remove_from_collection(collection, hook_constraints.objects)
                        ragdoll_aux.object_remove_from_collection(rb_obj_list, hook_constraints.objects)



            ragdoll_aux.collection_remove(rigid_bodies)
            ragdoll_aux.collection_remove(constraints)
            ragdoll_aux.collection_remove(connectors)
            ragdoll_aux.collection_remove(wiggles)
            ragdoll_aux.collection_remove(wiggle_constraints)
            ragdoll_aux.collection_remove(hooks)
            ragdoll_aux.collection_remove(hook_constraints)

            armature_data = control_rig.data

            bpy.data.objects.remove(control_rig, do_unlink=True)
            if armature_data.name in bpy.data.armatures:
                bpy.data.armatures.remove(armature_data, do_unlink=True)

            ragdoll_aux.drivers_remove_invalid(deform_rig)
            ragdoll_aux.drivers_remove_related(deform_rig)

            deform_rig.data.ragdoll.initialized = False

            ragdoll_aux.select_set_active(bpy.context, deform_rig)

            print("Info: removed ragdoll")

    # duplicate armature to use as control rig
    def secondary_rig_add(self, deform_rig):
        if deform_rig:
            # copy armature
            secondary_rig = deform_rig.copy()
            secondary_rig.name = deform_rig.name + deform_rig.data.ragdoll.ctrl_rig_suffix
            # copy armature data
            secondary_rig.data = deform_rig.data.copy()
            # copy armature custom props
            for key in deform_rig.keys():
                secondary_rig[key] = deform_rig[key]
            bpy.context.collection.objects.link(secondary_rig)
            
            # adjust viewport display to differentiate Armatures
            if deform_rig.data.display_type == 'OCTAHEDRAL':
                secondary_rig.data.display_type = 'STICK'
            else:
                secondary_rig.data.display_type = 'OCTAHEDRAL'

            self.deform_rig = deform_rig
            self.deform_rig.data.ragdoll.type = 'DEFORM'
            self.deform_rig.data.ragdoll.initialized = True

            self.control_rig = secondary_rig
            self.control_rig.data.ragdoll.type = 'CONTROL'
            self.control_rig.data.ragdoll.initialized = True

            ragdoll_aux.deselect_all()
            self.control_rig.select_set(True)
            bpy.context.view_layer.objects.active = self.control_rig
            
            print("Info: ctrl rig added")
            return self.control_rig

        else:
            print("Error: No active armature.")
            return None

    # reset approximated / modified primary rigid body meshes upon user input
    def rigid_bodies_reset(context):
        for bone in context.selected_pose_bones:
            ragdoll_aux.reset_rigid_body_cube(bone)
            
    # add constraints to copy transforms of simulation/animation 
    def pose_constraints_add(self, bones):
        for bone in bones:
            connector = bone.ragdoll.connector
            if connector:
                # add copy transform constraint for simulation
                copy_transforms_rd = bone.constraints.new('COPY_TRANSFORMS')
                copy_transforms_rd.name = "RagDoll Copy Transforms Simulation"
                copy_transforms_rd.target = connector
                # add driver to control constraint's influence using ragdoll property
                self.sim_influence_pose_constraint_driver_add(copy_transforms_rd, 'ragdoll.simulation_influence', '1-simulation_influence')

                # add copy transform constraint for animation
                copy_transforms_ctrl = bone.constraints.new('COPY_TRANSFORMS')
                copy_transforms_ctrl.name = "RagDoll Copy Transform Animation"
                copy_transforms_ctrl.target = self.control_rig
                copy_transforms_ctrl.subtarget = bone.name
                # add driver to control constraint's influence using ragdoll property
                self.sim_influence_pose_constraint_driver_add(copy_transforms_ctrl, 'ragdoll.simulation_influence', 'simulation_influence')
            
        print("Info: bone constraints set")

    # add simple scripted driver to pose constraint provided
    def sim_influence_pose_constraint_driver_add(self, pose_constraint, rd_data_path, expression):
        rd_influence = pose_constraint.driver_add("influence")
        rd_influence.driver.type = 'SCRIPTED'
        var = rd_influence.driver.variables.new()
        var.name = "simulation_influence"
        var.type = 'SINGLE_PROP'
        target = var.targets[0]
        target.id_type = 'ARMATURE'
        target.id = self.control_rig.data
        target.data_path = rd_data_path
        rd_influence.driver.expression = expression


    def update_suffix(self, context):
        if self.control_rig:
            rig = self.control_rig
        elif self.deform_rig:
            rig = self.deform_rig.data.ragdoll.control_rig
        if rig:
            rig.name = rig.name.replace(self.ctrl_rig_suffix_previous, self.ctrl_rig_suffix)
        self.ctrl_rig_suffix_previous = self.ctrl_rig_suffix
        
    def bone_names_substring_replace(self, context):
        rig_obj = context.object
        rigid_bodies = rig_obj.data.ragdoll.rigid_bodies
        constraints = rigid_bodies.constraints
        connectors = rigid_bodies.connectors
        wiggles = rig_obj.data.ragdoll.wiggles
        wiggle_constraints = wiggles.constraints
        
        pose_bones_ctrl = rig_obj.pose.bones
        
        source = rig_obj.data.ragdoll.substring_replace_source
        target = rig_obj.data.ragdoll.substring_replace_target
        suffix = rig_obj.data.ragdoll.substring_replace_suffix

        if rigid_bodies.collection:
            for obj in rigid_bodies.collection.objects:
                if source in obj.name:
                    obj.name = obj.name.replace(source, target)
                    obj.name = obj.name.replace(rigid_bodies.suffix, "") + suffix + rigid_bodies.suffix
                
        if constraints.collection:
            for obj in constraints.collection.objects:
                if source in obj.name:
                    obj.name = obj.name.replace(source, target)
                    obj.name = obj.name.replace(constraints.suffix, "") + suffix + constraints.suffix 

        if connectors.collection:
            for obj in connectors.collection.objects:
                if source in obj.name:
                    obj.name = obj.name.replace(source, target)
                    obj.name = obj.name.replace(connectors.suffix, "") + suffix + connectors.suffix 

        if wiggles.collection:
            for obj in wiggles.collection.objects:
                if source in obj.name:
                    obj.name = obj.name.replace(source, target)
                    obj.name = obj.name.replace(wiggles.suffix, "") + suffix + wiggles.suffix 

        if wiggle_constraints.collection:
            for obj in wiggle_constraints.collection.objects:
                if source in obj.name:
                    obj.name = obj.name.replace(source, target)
                    obj.name = obj.name.replace(wiggle_constraints.suffix, "") + suffix + wiggle_constraints.suffix 

        for bone in pose_bones_ctrl:
            if source in bone.name:
                bone.name = bone.name.replace(source, target) + suffix

        if rig_obj.data.ragdoll.deform_rig:
            pose_bones_def = rig_obj.data.ragdoll.deform_rig.pose.bones
            for bone in pose_bones_def:
                if source in bone.name:
                    bone.name = bone.name.replace(source, target) + suffix


