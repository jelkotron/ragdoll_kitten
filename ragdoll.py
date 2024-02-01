import bpy
import math
import mathutils
import ragdoll_aux


#---- callback functions ---- 
def armature_poll(self, object):
    return object.type == 'ARMATURE'


def mesh_poll(self, object):
     return object.type == 'MESH'


def empty_poll(self, object):
    return object.type == 'EMPTY'


def wiggle_const_update(self, context):
    control_rig = ragdoll_aux.validate_selection(context.object)
    if control_rig.data.ragdoll.type == 'DEFORM':
        control_rig = control_rig.data.ragdoll.control_rig
    if control_rig:
        # limits
        limit_lin = control_rig.data.ragdoll.wiggle_restrict_linear
        limit_ang = control_rig.data.ragdoll.wiggle_restrict_angular
        global_max_lin = control_rig.data.ragdoll.wiggle_distance
        global_max_ang = control_rig.data.ragdoll.wiggle_rotation
        # settings
        use_wiggle = control_rig.data.ragdoll.wiggle
        use_falloff = control_rig.data.ragdoll.wiggle_use_falloff
        use_springs = control_rig.data.ragdoll.wiggle_use_springs
        falloff_mode = control_rig.data.ragdoll.wiggle_falloff_mode
        falloff_factor = control_rig.data.ragdoll.wiggle_falloff_factor
        falloff_offset = control_rig.data.ragdoll.wiggle_falloff_offset
        falloff_invert = control_rig.data.ragdoll.wiggle_falloff_invert
        bone_level_max = control_rig.data.ragdoll.bone_level_max
        wiggle_falloff_chain_ends = control_rig.data.ragdoll.wiggle_falloff_chain_ends

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
                            
                            # TODO: check if this make sense, it's late.
                            visible_bones = ragdoll_aux.get_visible_posebones()
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
                                    max_lin = 1/max_lin
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
                                wiggle_const.spring_stiffness_x = control_rig.data.ragdoll.wiggle_stiffness
                                wiggle_const.spring_stiffness_y = control_rig.data.ragdoll.wiggle_stiffness
                                wiggle_const.spring_stiffness_z = control_rig.data.ragdoll.wiggle_stiffness
                                
                                wiggle_const.spring_damping_x = control_rig.data.ragdoll.wiggle_damping
                                wiggle_const.spring_damping_y = control_rig.data.ragdoll.wiggle_damping
                                wiggle_const.spring_damping_z = control_rig.data.ragdoll.wiggle_damping
        print("Info: Wiggle updated")


def meshes_update(self, context):
    control_rig = ragdoll_aux.validate_selection(context.object)
    rb_cubes_scale(control_rig, 'RIGID_BODIES')
    rb_cubes_scale(control_rig, 'WIGGLE')


#---- additional properties definition ----
class RagDollBonePropGroup(bpy.types.PropertyGroup):
    is_ragdoll: bpy.props.BoolProperty(name="Part of a Ragdoll", default=False)
    tree_level: bpy.props.IntProperty(name="tree_level", min=0, default =0)
    rigid_body: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body", poll=mesh_poll)
    constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body Constraint", poll=empty_poll)
    connector: bpy.props.PointerProperty(type=bpy.types.Object, name="Rigid Body Connector", poll=empty_poll)
    wiggle: bpy.props.PointerProperty(type=bpy.types.Object, name="Wiggle", poll=mesh_poll)
    wiggle_constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="Wiggle Constraint", poll=empty_poll)


class RagDollPropGroup(bpy.types.PropertyGroup):
    #-------- Object Pointers --------
    deform_rig: bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_poll)
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll)
    rigid_bodies: bpy.props.PointerProperty(type=bpy.types.Collection)
    constraints: bpy.props.PointerProperty(type=bpy.types.Collection)
    connectors: bpy.props.PointerProperty(type=bpy.types.Collection)
    wiggles: bpy.props.PointerProperty(type=bpy.types.Collection)
    wiggle_constraints: bpy.props.PointerProperty(type=bpy.types.Collection)
    #-------- Armature Sub Type --------
    type: bpy.props.EnumProperty(items=[
                                                            ('CONTROL', "Control Rig", "Control Rig of a RagDoll"),
                                                            ('DEFORM', "Deform Rig", "Deform Rig of a RagDoll")                          
                                                            ], default='DEFORM')
    #-------- JSON Config File --------
    config: bpy.props.PointerProperty(type=bpy.types.Text)

    #-------- Suffixes --------
    ctrl_rig_suffix: bpy.props.StringProperty(name="Control Rig Suffix", default=".Control")
    def_rig_suffix: bpy.props.StringProperty(name="Deform Rig Suffix", default=".Deform")
    rb_suffix: bpy.props.StringProperty(name="Ragdoll Geo Suffix", default=".RigidBody")
    wiggle_suffix: bpy.props.StringProperty(name="Ragdoll Geo Suffix", default=".Wiggle")
    wiggle_const_suffix: bpy.props.StringProperty(name="Ragdoll Geo Suffix", default=".WiggleConstraint")
    const_suffix: bpy.props.StringProperty(name="Rigid Body Constraint Suffix", default=".Constraint")
    connect_suffix: bpy.props.StringProperty(name="Connector Suffix", default=".Connect")
    # -------- State --------
    initialized: bpy.props.BoolProperty(name="RagDoll initialized", default=False)
    
    # -------- Geometry Settings
    rb_bone_width_min: bpy.props.FloatProperty(name="Minimum Rigid Body Geo Width", default=0.1, min=0.0, update=meshes_update)
    rb_bone_width_max: bpy.props.FloatProperty(name="Minimum Rigid Body Geo Width", default=0.1, min=0.0, update=meshes_update)
    rb_bone_width_relative: bpy.props.FloatProperty(name="Relative Rigid Body Geo Width", default=0.1, min=0.0, update=meshes_update)

    # -------- Channels --------
    kinematic: bpy.props.BoolProperty(name="Animated", default=True)
    simulation_influence: bpy.props.FloatProperty(name="Rigid Body_Influence",min=0.0, max=1.0, default=0.0)
    
    wiggle: bpy.props.BoolProperty(name="Use Wiggle", default=False, update=wiggle_const_update)
    wiggle_distance: bpy.props.FloatProperty(name="Maximum Wiggle Translation",min=0.0, max=16.0, default=0.2, update=wiggle_const_update)
    wiggle_rotation: bpy.props.FloatProperty(name="Maximum Wiggle Rotation", subtype="ANGLE", min=0.0, max=math.radians(360.0), default=math.radians(22.5), update=wiggle_const_update)
    wiggle_restrict_linear: bpy.props.BoolProperty(name="Limit Wiggle Translation", default=True, update=wiggle_const_update)
    wiggle_restrict_angular: bpy.props.BoolProperty(name="Limit Wiggle Rotation", default=False, update=wiggle_const_update)

    wiggle_use_falloff: bpy.props.BoolProperty(name="Use Wiggle Falloff", default=False, update=wiggle_const_update)
    wiggle_falloff_invert: bpy.props.BoolProperty(name="Invert Falloff", default=False, update=wiggle_const_update)
    wiggle_falloff_chain_ends: bpy.props.BoolProperty(name="Chain Ends", default=True, update=wiggle_const_update)
    wiggle_falloff_mode: bpy.props.EnumProperty(items=[
                                                            ('LINEAR', "Linear", "Linear bone chain based falloff in wiggle"),
                                                            ('QUADRATIC', "Quadratic", "Quadratic bone chain based falloff in wiggle")                          
                                                            ], default='QUADRATIC', name="Falloff Mode", update=wiggle_const_update)
    
    wiggle_falloff_factor: bpy.props.FloatProperty(name="wiggle_falloff_factor", min=0.0, max=10.0, default=1.0, update=wiggle_const_update)
    wiggle_falloff_offset: bpy.props.FloatProperty(name="wiggle_falloff_factor", min=-10.0, max=10.0, update=wiggle_const_update)
    wiggle_drivers: bpy.props.BoolProperty(name="Wiggle has Drivers", default=False)

    wiggle_use_springs: bpy.props.BoolProperty(name="Use Springs", default=True, update=wiggle_const_update)
    wiggle_stiffness: bpy.props.FloatProperty(name="Stiffnesss", min=0, max=1000, update=wiggle_const_update)
    wiggle_damping: bpy.props.FloatProperty(name="Stiffnesss", min=0, max=1000, update=wiggle_const_update)

    bone_level_max: bpy.props.IntProperty(name="bone_level_max", min=0, default=0)


def rag_doll_create(armature_object):
    if armature_object.type == 'ARMATURE':
        # get selected bones that are not hidden
        bones = ragdoll_aux.get_visible_posebones()
        for b in bones:
            b.ragdoll.is_ragdoll = True
        deform_rig = armature_object
        # store bones' hierarchy level in bone prop
        deform_rig = ragdoll_aux.bones_tree_levels_set(deform_rig, bones)
        # copy deform armature to use as control
        control_rig = secondary_rig_add(deform_rig)
      
        # primary rigid body objects (transform targets for bones)
        rb_cubes_add(bones, mode='PRIMARY')
        # secondary rigid body objects (wiggles)
        rb_cubes_add(bones, mode='SECONDARY')
       
        # primary constraints (joints between bones)
        rb_constraints_add(deform_rig, mode='PRIMARY')
        rb_constraint_defaults(control_rig.data.ragdoll.constraints, 0, 22.5)
        
        # secondary constraints (connection between primary rigid bodies and wiggle objects)
        rb_constraints_add(deform_rig, mode='SECONDARY') # wiggle constraints
        rb_constraint_defaults(control_rig.data.ragdoll.wiggle_constraints, 0.01, 22.5)
        
        # read transformational limits from file, set to primary rigid body constraints
        rd_constraint_limit(control_rig)

        # additional object layer to copy transforms from, as rigid body meshes' pivots have to be centered
        rb_connectors_add(control_rig)

        # 
        bone_constraints_add(bones, control_rig)
        bone_drivers_add(deform_rig, control_rig)
        control_rig.data.ragdoll.initialized = True
        deform_rig.data.ragdoll.initialized = True

        print("Info: added ragdoll")


def secondary_rig_add(armature_object):
    if armature_object:
        # copy armature
        secondary_rig = armature_object.copy()
        secondary_rig.name = armature_object.name + armature_object.data.ragdoll.ctrl_rig_suffix
        # copy armature data
        secondary_rig.data = armature_object.data.copy()
        # copy armature custom props
        for key in armature_object.keys():
            secondary_rig[key] = armature_object[key]
        bpy.context.collection.objects.link(secondary_rig)
        
        # adjust viewport display to differentiate Armatures
        if armature_object.data.display_type == 'OCTAHEDRAL':
            secondary_rig.data.display_type = 'STICK'
        else:
            secondary_rig.data.display_type = 'OCTAHEDRAL'

        deform = None
        ctrl = None

        if armature_object.data.ragdoll.type == 'DEFORM':
            secondary_rig.data.ragdoll.type = 'CONTROL'
            deform = armature_object
            ctrl = secondary_rig
        
        elif armature_object.data.ragdoll.type == 'CONTROL':
            secondary_rig.data.ragdoll.type = 'DEFORM'
            deform = secondary_rig
            ctrl = armature_object
        

        ctrl.data["rd_influence"] = 1.0
        ctrl.data.id_properties_ensure()  # Make sure the manager is updated
        property_manager = ctrl.data.id_properties_ui("rd_influence")
        property_manager.update(min=0, max=1)
        

        ctrl.data.ragdoll.deform_rig = deform
        ctrl.data.ragdoll.initialized = True
        
        deform.data.ragdoll.control_rig = ctrl
        deform.data.ragdoll.initialized = True

        ragdoll_aux.deselect_all()
        ctrl.select_set(True)
        bpy.context.view_layer.objects.active = ctrl
        
        print("Info: ctrl rig added")
        return ctrl

    else:
        print("Error: No active armature.")
        return None
        

def rb_cubes_scale(control_rig, mode='RIGID_BODIES'):
    width_relative = control_rig.data.ragdoll.rb_bone_width_relative
    width_min = control_rig.data.ragdoll.rb_bone_width_min
    width_max = control_rig.data.ragdoll.rb_bone_width_max

    if width_min + width_max + width_relative > 0:
        for bone in control_rig.pose.bones:
            mesh = None
            if mode == 'RIGID_BODIES':
                if bone.ragdoll.rigid_body:
                    mesh = bone.ragdoll.rigid_body
            elif mode == 'WIGGLES':
                if bone.ragdoll.wiggle:
                    mesh = bone.ragdoll.wiggle
            if mesh:
                print(mesh)
                for vert in mesh.data.vertices:
                    for i in range(3):
                        # reset cube to dimensions = [1,1,1] 
                        vert.co[i] *= abs(0.5 / vert.co[i])
                        if i == 1:
                            vert.co[i] *= bone.length
                        else:
                            # clamp values to min/max
                            width_factor = width_relative * bone.length

                            if width_max != 0:
                                width_factor = min(width_max, width_relative)
                            
                            if width_min != 0:
                                width_factor = max(width_factor, width_min)
        
                            # apply new transform
                            vert.co[i] *= width_factor

                mesh.data.update()
                bpy.context.view_layer.update()

    else:
        print("Error: Cannot create mesh with width of 0")
        

def rb_cubes_add(pbones, mode='PRIMARY'):
    rb_bones = []
    # store current frame & tmp reset to 0
    f_init = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = 0
    
    selected_rig = ragdoll_aux.validate_selection(bpy.context.object, 'ARMATURE')

    control_rig = None
    deform_rig = None

    if selected_rig:
        if selected_rig.data.ragdoll.type == 'DEFORM':
            control_rig = selected_rig.data.ragdoll.control_rig
            deform_rig = selected_rig
        elif selected_rig.data.ragdoll.type == 'CONTROL':
            control_rig = selected_rig
            deform_rig = selected_rig.data.ragdoll.deform_rig
    
    # select name and collection
    if mode == 'PRIMARY':
        suffix = deform_rig.data.ragdoll.rb_suffix
    
    elif mode == 'SECONDARY':
        suffix = deform_rig.data.ragdoll.wiggle_suffix

    if control_rig:
        for pb in pbones:
            geo_name = deform_rig.name + "." + pb.name + suffix
            # add and scale box geometry per bone
            new_cube = ragdoll_aux.cube(1, geo_name)
            new_cube.display_type = 'WIRE'

            for vert in new_cube.data.vertices:
                vert.co[0] *= 1 / new_cube.dimensions[1] * pb.length * deform_rig.data.ragdoll.rb_bone_width_relative
                vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
                vert.co[2] *= 1 / new_cube.dimensions[1] * pb.length * deform_rig.data.ragdoll.rb_bone_width_relative

            # parent cube to control rig bone
            new_cube.matrix_local = pb.matrix
            new_cube.parent = control_rig
            new_cube.parent_type = 'BONE'
            new_cube.parent_bone = pb.name

            # apply bone's transform to cube
            vector = (pb.head - pb.tail) / 2
            translate = mathutils.Matrix.Translation(vector)
            new_cube.matrix_parent_inverse = pb.matrix.inverted() @ translate
          
            # add cube to rigid body collection & set collision shape 
            bpy.context.scene.rigidbody_world.collection.objects.link(new_cube)
            new_cube.rigid_body.collision_shape = 'BOX'
            new_cube.rigid_body.kinematic = True
            # add driver to switch animation/simulation
            if mode == 'PRIMARY':
                # set bone property
                pb.ragdoll.rigid_body = new_cube
                if control_rig.pose.bones.get(pb.name):
                    control_rig.pose.bones[pb.name].ragdoll.rigid_body = new_cube
                    
                # add driver
                driven_value = new_cube.rigid_body.driver_add("kinematic")
                driven_value.driver.type = 'SCRIPTED'
                driven_value.driver.expression = "kinematic"
                driver_var = driven_value.driver.variables.new()
                driver_var.name = "kinematic"
                driver_var.type = 'SINGLE_PROP'
                target = driver_var.targets[0]
                target.id_type = 'ARMATURE'
                target.id = control_rig.data
                target.data_path = 'ragdoll.kinematic'

            else:
                # TODO: set this elsewhere
                new_cube.rigid_body.collision_collections[0] = False
                new_cube.rigid_body.collision_collections[1] = True
                # set bone property
                pb.ragdoll.wiggle = new_cube
                if control_rig.pose.bones.get(pb.name):
                    control_rig.pose.bones[pb.name].ragdoll.wiggle = new_cube

            rb_bones.append(new_cube)
   
    
        
    # add cubes to collection
    collection_name = deform_rig.name + suffix
    collection = ragdoll_aux.collection_objects_add(collection_name, [rb_geo for rb_geo in rb_bones])
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, [rb_geo for rb_geo in rb_bones])
    if mode == 'PRIMARY':
        control_rig.data.ragdoll.rigid_bodies = collection
    if mode == 'SECONDARY':
        control_rig.data.ragdoll.wiggles = collection
    
    # restore current frame
    bpy.context.scene.frame_current = f_init


def rag_doll_remove(armature_object):
    if armature_object.type == 'ARMATURE':
        if armature_object.data.ragdoll.type == 'DEFORM':
            deform_rig = armature_object
            control_rig = armature_object.data.ragdoll.control_rig
            armature_object = armature_object.data.ragdoll.control_rig
        else:
            control_rig = armature_object
            deform_rig = armature_object.data.ragdoll.deform_rig
            
        for bone in deform_rig.pose.bones:
            bone.ragdoll.is_ragdoll = False
            for const in bone.constraints:
                if const.name == "Copy Transforms RD" or const.name == "Copy Transforms CTRL":
                    bone.constraints.remove(const)


        rigid_bodies = control_rig.data.ragdoll.rigid_bodies
        constraints = control_rig.data.ragdoll.constraints
        connectors = control_rig.data.ragdoll.connectors
        wiggles = control_rig.data.ragdoll.wiggles
        wiggle_constraints = control_rig.data.ragdoll.wiggle_constraints

        if bpy.context.scene.rigidbody_world:
            collection = bpy.context.scene.rigidbody_world.collection
            if rigid_bodies: object_remove_from_collection(collection, rigid_bodies.objects)
            if wiggles: object_remove_from_collection(collection, wiggles.objects)

        if bpy.context.scene.rigidbody_world.constraints:
            #TODO: be more concise
            collection = bpy.context.scene.rigidbody_world.constraints.collection_objects.data
            rb_obj_list =  bpy.context.scene.rigidbody_world.constraints

            if constraints: 
                object_remove_from_collection(collection, constraints.objects)
                object_remove_from_collection(rb_obj_list, constraints.objects)
            if wiggle_constraints:
                object_remove_from_collection(collection, wiggle_constraints.objects)
                object_remove_from_collection(rb_obj_list, wiggle_constraints.objects)

        # C.scene.rigidbody_world.constraints.collection_objects.data.objects['Armature.mixamorig:

        collection_remove(rigid_bodies)
        collection_remove(constraints)
        collection_remove(connectors)
        collection_remove(wiggles)
        collection_remove(wiggle_constraints)

        armature_data =armature_object.data
        bpy.data.objects.remove(armature_object, do_unlink=True)
        if armature_data.name in bpy.data.armatures:
            bpy.data.armatures.remove(armature_data, do_unlink=True)

        drivers_remove_invalid(deform_rig)
        deform_rig.data.ragdoll.initialized = False

        print("Info: removed ragdoll")


def collection_remove(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection, do_unlink=True)


def object_remove_from_collection(collection, objects):
    if collection != None:
        for obj in objects:
            if obj.name in collection.objects:
                collection.objects.unlink(obj)
    

def rag_doll_update(context):

    rig = context.object
    if ragdoll_aux.validate_selection(rig):
        control_rig = rig
        if rig.data.ragdoll.type == 'DEFORM':
            control_rig = rig.data.ragdoll.control_rig
        rd_constraint_limit(control_rig)
        rb_cubes_scale(control_rig)
        print("Info: ragdoll updated")


def force_update_drivers(context):
    # hack
    for armature in [i for i in bpy.data.objects if i.type=='ARMATURE']:
        if armature.animation_data:
            for fcurve in armature.animation_data.drivers:
                if fcurve:
                    if fcurve.driver.expression.endswith(" "):
                        fcurve.driver.expression = fcurve.driver.expression[:-1]
                    else:
                        fcurve.driver.expression += " "


def rb_constraints_add(deform_rig, mode='PRIMARY'):
    # store current frame & tmp reset to 0
    f_init = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = 0
    armature_object = ragdoll_aux.validate_selection(bpy.context.active_object, 'ARMATURE')

    if armature_object and armature_object.data.ragdoll.type == 'CONTROL':
        control_rig = armature_object
        deform_rig = control_rig.data.ragdoll.deform_rig

    elif armature_object and armature_object.data.ragdoll.type == 'DEFORM':
        control_rig = armature_object
        deform_rig = control_rig.data.ragdoll.deform_rig

    rb_suffix = control_rig.data.ragdoll.rb_suffix
    wiggle_suffix = control_rig.data.ragdoll.wiggle_suffix


    if mode == 'PRIMARY':
        empty_suffix = deform_rig.data.ragdoll.const_suffix

    elif mode == 'SECONDARY':
        empty_suffix = deform_rig.data.ragdoll.wiggle_const_suffix
    
    empties = []
    bones = ragdoll_aux.get_visible_posebones()
    
    for bone in bones:
        if mode == 'PRIMARY':
            # add rigid body constraints to joints
            if len(bone.children) > 0:
                for i in range(len(bone.children)):
                    child = bone.children[i]
                    name_0 = deform_rig.name + "." + bone.name + rb_suffix
                    name_1 = deform_rig.name + "." + child.name + rb_suffix
                    
                    if name_0 in bpy.data.objects and name_1 in bpy.data.objects:
                        empty_name = deform_rig.name + "." + child.name + empty_suffix
                        empty = bpy.data.objects.new(empty_name, None)
                        bpy.context.collection.objects.link(empty)
                        empty.empty_display_size = 0.15
                        bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
                        empty.rigid_body_constraint.type = 'GENERIC_SPRING'
                        
                        vec = (child.head - child.tail)
                        trans = mathutils.Matrix.Translation(vec)
                            
                        empty.matrix_local = child.matrix
                        empty.parent = deform_rig
                        empty.parent_type = 'BONE'
                        empty.parent_bone = child.name
                        empty.matrix_parent_inverse = child.matrix.inverted() @ trans

                        empty.rigid_body_constraint.object1 = bpy.data.objects[name_0]
                        empty.rigid_body_constraint.object2 = bpy.data.objects[name_1]
                        empties.append(empty)
                        bone.ragdoll.constraint = empty
                        control_rig.pose.bones[bone.name].ragdoll.constraint =  empty
        else:
            # add rigid body constraints to wiggles
            name_0 = deform_rig.name + "." + bone.name + rb_suffix
            name_1 = deform_rig.name + "." + bone.name + wiggle_suffix

            if name_0 in bpy.data.objects and name_1 in bpy.data.objects:
                empty_name = deform_rig.name + "." + bone.name + empty_suffix
                empty = bpy.data.objects.new(empty_name, None)
                bpy.context.collection.objects.link(empty)
                empty.empty_display_size = 0.15
                bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
                empty.rigid_body_constraint.type = 'GENERIC_SPRING'
                
                vec = (bone.head - bone.tail)
                trans = mathutils.Matrix.Translation(vec)
                    
                empty.matrix_local = bone.matrix
                empty.parent = deform_rig
                empty.parent_type = 'BONE'
                empty.parent_bone = bone.name
                empty.matrix_parent_inverse = bone.matrix.inverted() @ trans

                empty.rigid_body_constraint.object1 = bpy.data.objects[name_0]
                empty.rigid_body_constraint.object2 = bpy.data.objects[name_1]
                empties.append(empty)

                bone.ragdoll.wiggle_constraint = empty
                control_rig.pose.bones[bone.name].ragdoll.wiggle_constraint =  empty

    # add empties to collection
    collection_name = deform_rig.name + empty_suffix
    collection = ragdoll_aux.collection_objects_add(collection_name, empties)
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, empties)
    # TODO: get objs current collection
    if mode == 'PRIMARY':
        control_rig.data.ragdoll.constraints = collection
        deform_rig.data.ragdoll.constraints = collection
        print("Info: rd constraints added")
        print("Info: rd constraint limits set")

    else:
        control_rig.data.ragdoll.wiggle_constraints = collection
        deform_rig.data.ragdoll.wiggle_constraints = collection

    bpy.context.scene.frame_current = f_init
           

def rb_constraint_defaults(constraints, max_lin, max_ang):
        
        control_rig = ragdoll_aux.validate_selection(bpy.context.object)

        if control_rig:
            # constraints = control_rig.data.ragdoll.constraints
            if constraints:
                for obj in constraints.objects:
                    rb_const = obj.rigid_body_constraint
                    if rb_const:
                        if rb_const.type == 'GENERIC' or rb_const.type == 'GENERIC_SPRING':
                            rb_const.use_limit_lin_x = True
                            rb_const.use_limit_lin_y = True
                            rb_const.use_limit_lin_z = True
                            
                            rb_const.use_limit_ang_x = True
                            rb_const.use_limit_ang_y = True
                            rb_const.use_limit_ang_z = True
                            # default limits
                            rb_const.limit_lin_x_lower = -max_lin
                            rb_const.limit_lin_x_upper = max_lin
                            rb_const.limit_lin_y_lower = -max_lin
                            rb_const.limit_lin_y_upper = max_lin
                            rb_const.limit_lin_z_lower = -max_lin
                            rb_const.limit_lin_z_upper = max_lin
                            
                            rb_const.limit_ang_x_lower = math.radians(-max_ang)
                            rb_const.limit_ang_x_upper = math.radians(max_ang)
                            rb_const.limit_ang_y_lower = math.radians(-max_ang)
                            rb_const.limit_ang_y_upper = math.radians(max_ang)
                            rb_const.limit_ang_z_lower = math.radians(-max_ang)
                            rb_const.limit_ang_z_upper = math.radians(max_ang) 


def rd_constraint_limit(control_rig):
    config = control_rig.data.ragdoll.config
    if config:
        config_data = ragdoll_aux.config_load(config)

        if config_data != None:
            for obj in control_rig.data.ragdoll.constraints.objects:
                if obj.rigid_body_constraint:
                    constraint = obj.rigid_body_constraint
                    stripped_name = obj.name.rstrip(control_rig.data.ragdoll.const_suffix)
                    stripped_name = stripped_name.lstrip(control_rig.data.ragdoll.deform_rig.name).strip(".")
                    
                    if "strip" in config_data:
                        for i in range(len(config_data["strip"])):
                            stripped_name = stripped_name.replace(config_data["strip"][i],"")

                    bone_data = config_data.get("bones").get(stripped_name)
                    
                    if bone_data:
                        limit_lin_x_lower = bone_data.get("limit_lin_x_lower")
                        limit_lin_x_upper = bone_data.get("limit_lin_x_upper")
                        limit_lin_y_lower = bone_data.get("limit_lin_y_lower")
                        limit_lin_y_upper = bone_data.get("limit_lin_y_upper")
                        limit_lin_z_lower = bone_data.get("limit_lin_z_lower")
                        limit_lin_z_upper = bone_data.get("limit_lin_z_upper")

                        limit_ang_x_lower = bone_data.get("limit_ang_x_lower")
                        limit_ang_x_upper = bone_data.get("limit_ang_x_upper")
                        limit_ang_y_lower = bone_data.get("limit_ang_y_lower")
                        limit_ang_y_upper = bone_data.get("limit_ang_y_upper")
                        limit_ang_z_lower = bone_data.get("limit_ang_z_lower")
                        limit_ang_z_upper = bone_data.get("limit_ang_z_upper")

                        constraint.limit_lin_x_lower = limit_lin_x_lower if limit_lin_x_lower else constraint.limit_lin_x_lower  
                        constraint.limit_lin_x_upper = limit_lin_x_upper if limit_lin_x_upper else constraint.limit_lin_x_upper 
                        constraint.limit_lin_y_lower = limit_lin_y_lower if limit_lin_y_lower else constraint.limit_lin_y_lower 
                        constraint.limit_lin_y_upper = limit_lin_y_upper if limit_lin_y_upper else constraint.limit_lin_y_upper 
                        constraint.limit_lin_z_lower = limit_lin_z_lower if limit_lin_z_lower else constraint.limit_lin_z_lower 
                        constraint.limit_lin_z_upper = limit_lin_z_upper if limit_lin_z_upper else constraint.limit_lin_z_upper 

                        constraint.limit_ang_x_lower = math.radians(limit_ang_x_lower) if limit_ang_x_lower else constraint.limit_ang_x_lower 
                        constraint.limit_ang_x_upper = math.radians(limit_ang_x_upper) if limit_ang_x_upper else constraint.limit_ang_x_upper 
                        constraint.limit_ang_y_lower = math.radians(limit_ang_y_lower) if limit_ang_y_lower else constraint.limit_ang_y_lower 
                        constraint.limit_ang_y_upper = math.radians(limit_ang_y_upper) if limit_ang_y_upper else constraint.limit_ang_y_upper 
                        constraint.limit_ang_z_lower = math.radians(limit_ang_z_lower) if limit_ang_z_lower else constraint.limit_ang_z_lower 
                        constraint.limit_ang_z_upper = math.radians(limit_ang_z_upper) if limit_ang_z_upper else constraint.limit_ang_z_upper 

    else:
        rb_constraint_defaults(control_rig.data.ragdoll.constraints, 0, 22.5)


def rb_connectors_add(control_rig):
    # store current frame & tmp reset to 0
    f_init = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = 0
    empties = []
    bones = ragdoll_aux.get_visible_posebones()
    deform_rig = control_rig.data.ragdoll.deform_rig

    for bone in bones:
        geo_name = deform_rig.name + "." + bone.name + control_rig.data.ragdoll.rb_suffix
        geo = bpy.data.objects.get(geo_name)

        if geo:
            # add empty
            empty_name = ""
            empty_name = deform_rig.name + "." + bone.name + control_rig.data.ragdoll.connect_suffix
            empty = bpy.data.objects.new(empty_name, None)
            bpy.context.collection.objects.link(empty)
            
            # set & store position
            empty.matrix_world = deform_rig.matrix_world @ bone.matrix
            obj_matrix = empty.matrix_world.copy()
            
            # set parent
            empty.parent_type = 'OBJECT'
            empty.parent = geo
            
            # remove parent inverse transform
            empty.matrix_world.identity()
            bpy.context.view_layer.update()
            empty.matrix_world = obj_matrix 

            # modifiy visualization
            empty.empty_display_type = 'SPHERE'
            empty.empty_display_size = 0.1

            empties.append(empty)

    # add empties to collection
    collection_name = deform_rig.name + control_rig.data.ragdoll.connect_suffix
    collection = ragdoll_aux.collection_objects_add(collection_name, empties)
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, empties)
    # TODO: get objs current collection
    control_rig.data.ragdoll.connectors = collection
    deform_rig.data.ragdoll.connectors = collection


    # reset current frame to initial value
    bpy.context.scene.frame_current = f_init

    print("Info: rd connectors added")


def bone_constraints_add(bones, control_rig):
    # control_rig = ragdoll_aux.validate_selection(bpy.context.object, 'ARMATURE')
    
    for bone in bones:
        deform_rig_name = bone.id_data.name
        connector_name = deform_rig_name + "." + bone.name + control_rig.data.ragdoll.connect_suffix
        connector = bpy.data.objects.get(connector_name)
        if connector:
            # add copy transform constraint for simulation
            copy_transforms_rd = bone.constraints.new('COPY_TRANSFORMS')
            copy_transforms_rd.name = "Copy Transforms RD"
            copy_transforms_rd.target = connector
        
            # add copy transform constraint for animation
            copy_transforms_ctrl = bone.constraints.new('COPY_TRANSFORMS')
            copy_transforms_ctrl.name = "Copy Transforms CTRL"
            copy_transforms_ctrl.target = control_rig
            copy_transforms_ctrl.subtarget = bone.name
         
    print("Info: bone constraints set")


def bone_drivers_add(deform_rig, control_rig):
    for bone in deform_rig.pose.bones:
        # add driver to copy ragdoll transform constraint
        for const in bone.constraints:
            # TODO: not use constraints' names. custom props and pointers seem to be off stable API for constraints? 
            if 'RD' in const.name or 'CTRL' in const.name:
                rd_influence = const.driver_add("influence")
                rd_influence.driver.type = 'SCRIPTED'
                var = rd_influence.driver.variables.new()
                var.name = "simulation_influence"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'ARMATURE'
                target.id = control_rig.data
                target.data_path = 'ragdoll.simulation_influence'
                rd_influence.driver.expression = "1-simulation_influence"

                if 'CTRL' in const.name:
                    rd_influence.driver.expression = "simulation_influence"

    print("Info: bone constraint drivers set")


def wiggle_spring_drivers_add(control_rig):
    for obj in control_rig.data.ragdoll.wiggle_constraints.objects:
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
                    target.data_path = 'ragdoll.wiggle_%s'%key
                    fcurve.driver.expression = key

        else:
            print("Error: Wrong Rigid Body Constraint Type: %s"%obj.rigid_body_constraint.type)
    

def wiggle_spring_drivers_remove(control_rig):
    wiggle_constraints = control_rig.data.ragdoll.wiggle_constraints.objects
    for obj in wiggle_constraints:
        for d in obj.animation_data.drivers:
            obj.animation_data.drivers.remove(d)


def drivers_remove_invalid(object):
    for d in object.animation_data.drivers:
        if not d.is_valid:
            object.animation_data.drivers.remove(d)               


