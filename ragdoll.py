import bpy
import math
import mathutils
import ragdoll_aux




def armature_poll(self, object):
    return object.type == 'ARMATURE'

def mesh_poll(self, object):
     return object.type == 'MESH'
 
 
def empty_poll(self, object):
    return object.type == 'EMPTY'

class RagDollBonePropGroup(bpy.types.PropertyGroup):
    tree_lvl: bpy.props.IntProperty(name="tree_level", min=0, default =0)
    rigid_body: bpy.props.PointerProperty(type=bpy.types.Object, name="rigid_body", poll=mesh_poll)
    constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="constraint", poll=empty_poll)
    connector: bpy.props.PointerProperty(type=bpy.types.Object, name="connector", poll=empty_poll)
    wiggle: bpy.props.PointerProperty(type=bpy.types.Object, name="wiggle", poll=mesh_poll)
    wiggle_constraint: bpy.props.PointerProperty(type=bpy.types.Object, name="wiggle_constraint", poll=empty_poll)



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
    rb_bone_width_min: bpy.props.FloatProperty(name="Minimum Rigid Body Geo Width", default=0.1)
    rb_bone_width_max: bpy.props.FloatProperty(name="Minimum Rigid Body Geo Width", default=0.1)
    rb_bone_width_relative: bpy.props.FloatProperty(name="Relative Rigid Body Geo Width", default=0.1)

    # -------- Channels --------
    kinematic: bpy.props.BoolProperty(name="is_animated", default=True)
    kinematic_influence: bpy.props.FloatProperty(name="rigid_body_influence",min=0.0, max=1.0, default=1.0)
    wiggle: bpy.props.BoolProperty(name="is_wiggley", default=False)
    wiggle_distance: bpy.props.FloatProperty(name="wiggle_distance_max",min=0.0, max=16.0, default=0.2)
    wiggle_rotation: bpy.props.FloatProperty(name="wiggle_rotation_max", subtype="ANGLE", min=0.0, max=math.radians(360.0), default=math.radians(22.5))
    wiggle_restrict_linear: bpy.props.BoolProperty(name="wiggle_restrict_linear", default=True)
    wiggle_restrict_angular: bpy.props.BoolProperty(name="wiggle_restrict_angular", default=False)


def rag_doll_create(armature_object):
    if armature_object.type == 'ARMATURE':
        bones = ragdoll_aux.get_visible_posebones()
        deform_rig = armature_object
        deform_rig = ragdoll_aux.bones_tree_lvls_set(deform_rig)
        control_rig = secondary_rig_add(deform_rig)
        rb_cubes_add(bones, mode='PRIMARY') 
        rb_cubes_add(bones, mode='SECONDARY') # wiggles

        rb_constraints_add(deform_rig, mode='PRIMARY')
        rb_constraint_defaults(control_rig.data.ragdoll.constraints, 0, 22.5)
        
        rb_constraints_add(deform_rig, mode='SECONDARY') # wiggle constraints
        rb_constraint_defaults(control_rig.data.ragdoll.wiggle_constraints, 0.01, 22.5)
        
        rd_constraint_limit(control_rig)
        rb_connectors_add(control_rig)
        bone_constraints_add(bones, control_rig)
        bone_drivers_add(deform_rig, control_rig)
        control_rig.data.ragdoll.initialized = True
        deform_rig.data.ragdoll.initialized = True

        print("Info: added ragdoll")


def secondary_rig_add(armature_object):
    if armature_object:
        secondary_rig = armature_object.copy()
        secondary_rig.name = armature_object.name + armature_object.data.ragdoll.ctrl_rig_suffix
        secondary_rig.data = armature_object.data.copy() # necessary?
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
        

def rb_cubes_scale(control_rig):
    meshes = control_rig.data.ragdoll.rigid_bodies.objects
    bones = control_rig.pose.bones
    width_relative = control_rig.data.ragdoll.rb_bone_width_relative
    width_min = control_rig.data.ragdoll.rb_bone_width_min
    width_max = control_rig.data.ragdoll.rb_bone_width_max
   
   
    deform_rig_name = control_rig.data.ragdoll.deform_rig.name
    rb_suffix = control_rig.data.ragdoll.rb_suffix

    for mesh in meshes:
        bone = bones.get(mesh.name.replace(deform_rig_name,"").replace(rb_suffix,"").strip("."))
        if bone:
            dimensions = mesh.dimensions
            for vert in mesh.data.vertices:
                for i in range(3):
                    # reset cube to dimensions = [1,1,1] 
                    vert.co[i] *= abs(0.5 / vert.co[i])
                    # apply new transform
                    if i!=1:
                        maximum = (vert.co[i] / abs(vert.co[i]) * width_max) / 2
                        minimum = (vert.co[i] / abs(vert.co[i]) * width_min) / 2
                        vert.co[i] *= bone.length * width_relative
                        # problematic :/
                        # vert.co[i] = min(vert.co[i], maximum)
                        # vert.co[i] = max(vert.co[i], minimum)

                    else:
                        vert.co[i] *= 1 / 1 * bone.length
                    # apply relative value to x, z axis
        mesh.data.update()

    bpy.context.view_layer.update()
        

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
            # new_cube.display_type = 'WIRE'

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
            
            # # TODO: add rigid body world
            # if bpy.context.scene.rigidbody_world.collection == None:
            #     bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
            
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
    # deform_rig = armature_object.data.ragdoll.deform_rig
    
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
                        empty.rigid_body_constraint.type = 'GENERIC'
                        
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
                empty.rigid_body_constraint.type = 'GENERIC'
                
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
        config_data = ragdoll_aux.config_load(config.filepath)
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


#-------- additional object layer to copy transforms from, as rigid body meshes' pivots need to be centered --------
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
                var.name = "kinematic_influence"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'ARMATURE'
                target.id = control_rig.data
                target.data_path = 'ragdoll.kinematic_influence'
                rd_influence.driver.expression = "kinematic_influence"

                if 'CTRL' in const.name:
                    rd_influence.driver.expression = "1 - kinematic_influence"

    print("Info: bone constraint drivers set")


def drivers_remove_invalid(object):
    for d in object.animation_data.drivers:
        if 'kinematic_influence' in d.driver.expression:
            object.animation_data.drivers.remove(d)


def wiggles_update(context):
    control_rig = ragdoll_aux.validate_selection(context.object)
    if control_rig.data.ragdoll.type == 'DEFORM':
        control_rig = control_rig.data.ragdoll.control_rig
    if control_rig:
        wiggle_constraints = control_rig.data.ragdoll.wiggle_constraints.objects
        wiggle = control_rig.data.ragdoll.wiggle
        limit_lin = control_rig.data.ragdoll.wiggle_restrict_linear
        limit_ang = control_rig.data.ragdoll.wiggle_restrict_angular
        max_lin = control_rig.data.ragdoll.wiggle_distance
        max_ang = control_rig.data.ragdoll.wiggle_rotation
        
        for obj in wiggle_constraints:
            const = obj.rigid_body_constraint
            if const:
                if not wiggle:
                    const.enabled = False
                else:
                    const.enabled = True
                    if const.type == 'GENERIC' or const.type == 'GENERIC_SPRING':
                        const.use_limit_ang_x, const.use_limit_ang_y, const.use_limit_ang_z = limit_ang, limit_ang, limit_ang
                        const.use_limit_lin_x, const.use_limit_lin_y, const.use_limit_lin_z = limit_lin, limit_lin, limit_lin
                        const.limit_lin_x_lower, const.limit_lin_x_upper = - max_lin, max_lin
                        const.limit_lin_y_lower, const.limit_lin_y_upper = - max_lin, max_lin
                        const.limit_lin_z_lower, const.limit_lin_z_upper = - max_lin, max_lin 

                        const.limit_ang_x_lower, const.limit_ang_x_upper = math.degrees(- max_ang), math.degrees(max_ang)
                        const.limit_ang_y_lower, const.limit_ang_y_upper = math.degrees(- max_ang), math.degrees(max_ang)
                        const.limit_ang_z_lower, const.limit_ang_z_upper = math.degrees(- max_ang), math.degrees(max_ang)
                    
