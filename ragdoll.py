import bpy
import math
import mathutils
import ragdoll_aux


def armature_poll(self, object):
    return object.type == 'ARMATURE'


class RagDollPropGroup(bpy.types.PropertyGroup):
    #-------- Object Pointers --------
    deform_rig: bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_poll)
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll)
    rigid_bodies: bpy.props.PointerProperty(type=bpy.types.Collection)
    constraints: bpy.props.PointerProperty(type=bpy.types.Collection)
    connectors: bpy.props.PointerProperty(type=bpy.types.Collection)
    #-------- Armature Sub Type --------
    type: bpy.props.EnumProperty(items=[
                                                            ('CONTROL', "Control Rig", "Control Rig of a RagDoll"),
                                                            ('DEFORM', "Deform Rig", "Deform Rig of a RagDoll")                          
                                                            ], default='DEFORM')
    #-------- JSON Config File Pointer --------
    config: bpy.props.PointerProperty(type=bpy.types.Text)

    #-------- Suffixes --------
    ctrl_rig_suffix: bpy.props.StringProperty(name="Control Rig Suffix", default=".Control")
    def_rig_suffix: bpy.props.StringProperty(name="Deform Rig Suffix", default=".Deform")
    rb_suffix: bpy.props.StringProperty(name="Ragdoll Geo Suffix", default=".RigidBody")
    const_suffix: bpy.props.StringProperty(name="Rigid Body Constraint Suffix", default=".Constraint")
    connect_suffix: bpy.props.StringProperty(name="Connector Suffix", default=".Connect")
    # -------- State --------
    initialized: bpy.props.BoolProperty(name="RagDoll initialized", default=False)
    
    # -------- Geometry Settings
    rb_bone_width_min: bpy.props.FloatProperty(name="Minimum Rigid Body Geo Width", default=0.1)
    rb_bone_width_relative: bpy.props.FloatProperty(name="Relative Rigid Body Geo Width", default=0.1)

    # -------- Channels --------
    simulated: bpy.props.BoolProperty(name="is_animated", default=True)
    influence: bpy.props.FloatProperty(name="rigid_body_influence",min=0.0, max=1.0, default=1.0)
    wobble: bpy.props.BoolProperty(name="is_wobbley", default=False)
    wobble_distance: bpy.props.FloatProperty(name="wobble_distance_max",min=0.0, max=16.0, default=1.0)
    wobble_rotation: bpy.props.FloatProperty(name="wobble_rotation_max", subtype="ANGLE", min=0.0, max=360.0, default=0)
    


def rag_doll_create(armature_object):
    if armature_object.type == 'ARMATURE':
        bones = ragdoll_aux.get_visible_posebones()
        deform_rig = armature_object
        control_rig = secondary_rig_add(armature_object)
        rb_cubes_add(bones)
        rb_constraints_add(deform_rig)
        rb_constraint_defaults()
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
        ctrl.data["kinematic"] = False

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
        
        
def rb_cubes_add(pbones):
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

    if control_rig:
        for pb in pbones:
            geo_name = deform_rig.name + "." + pb.name + deform_rig.data.ragdoll.rb_suffix
            # add and scale box geometry per bone
            new_cube = ragdoll_aux.cube(1, geo_name)
            new_cube.display_type = 'WIRE'

            for vert in new_cube.data.vertices:
                #TODO: consider armatures w/ scales other than 1
                vert.co[0] *= 1 / new_cube.dimensions[1] * deform_rig.data.ragdoll.rb_bone_width_relative
                vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
                vert.co[2] *= 1 / new_cube.dimensions[1] * deform_rig.data.ragdoll.rb_bone_width_relative

            # parent cube to control rig bone
            new_cube.matrix_local = pb.matrix
            new_cube.parent = control_rig
            new_cube.parent_type = 'BONE'
            new_cube.parent_bone = pb.name

            # apply bone's transform to cube
            vector = (pb.head - pb.tail) / 2
            translate = mathutils.Matrix.Translation(vector)
            new_cube.matrix_parent_inverse = pb.matrix.inverted() @ translate
            
            # TODO: add rigid body world
            if bpy.context.scene.rigidbody_world.collection == None:
                bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
            
            # add cube to rigid body collection & set collision shape 
            bpy.context.scene.rigidbody_world.collection.objects.link(new_cube)
            new_cube.rigid_body.collision_shape = 'BOX'

            # add driver to switch animation/simulation
            driven_value = new_cube.rigid_body.driver_add("kinematic")
            driven_value.driver.type = 'SCRIPTED'
            driven_value.driver.expression = "animated"
            driver_var = driven_value.driver.variables.new()
            driver_var.name = "animated"
            driver_var.type = 'SINGLE_PROP'
            target = driver_var.targets[0]
            target.id_type = 'ARMATURE'
            target.id = control_rig.data
            target.data_path = '["kinematic"]'

            rb_bones.append(new_cube)
   
    
        
    # add cubes to collection
    collection_name = deform_rig.name + bpy.context.object.data.ragdoll.rb_suffix
    collection = ragdoll_aux.collection_objects_add(collection_name, [rb_geo for rb_geo in rb_bones])
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, [rb_geo for rb_geo in rb_bones])
    control_rig.data.ragdoll.rigid_bodies = collection
    # ctrl_rig.data.ragdoll.rigid_body_constraints = collection

    
    # restore current frame
    bpy.context.scene.frame_current = f_init


def rag_doll_remove(armature_object):
    if armature_object.type == 'ARMATURE':
        if armature_object.data.ragdoll.type == 'DEFORM':
            armature_object = armature_object.data.ragdoll.control_rig

        rigid_bodies = armature_object.data.ragdoll.rigid_bodies
        constraints = armature_object.data.ragdoll.constraints
        connectors = armature_object.data.ragdoll.connectors

        if bpy.context.scene.rigidbody_world:
            collection = bpy.context.scene.rigidbody_world.collection
            object_remove_from_collection(collection, rigid_bodies.objects)

        if bpy.context.scene.rigidbody_world.constraints:
            collection = bpy.context.scene.rigidbody_world.constraints.collection_objects.data
            rb_obj_list =  bpy.context.scene.rigidbody_world.constraints

            object_remove_from_collection(collection, constraints.objects)
            object_remove_from_collection(rb_obj_list, constraints.objects)

        # C.scene.rigidbody_world.constraints.collection_objects.data.objects['Armature.mixamorig:

        collection_remove(rigid_bodies)
        collection_remove(constraints)
        collection_remove(connectors)

        armature_object.data.ragdoll.deform_rig.data.ragdoll.initialized = False
        armature_data =armature_object.data
        bpy.data.objects.remove(armature_object, do_unlink=True)
        if armature_data.name in bpy.data.armatures:
            bpy.data.armatures.remove(armature_data, do_unlink=True)


        print("Info: removed ragdoll")


def collection_remove(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection, do_unlink=True)


def object_remove_from_collection(collection, objects):
    if collection:
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
        print("Info: ragdoll updated")


def rb_constraints_add(deform_rig):
    # store current frame & tmp reset to 0
    f_init = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = 0

    armature_object = ragdoll_aux.validate_selection(bpy.context.active_object, 'ARMATURE')
    if armature_object and armature_object.data.ragdoll.type == 'CONTROL':
        empties = []
        bones = ragdoll_aux.get_visible_posebones()
        # deform_rig = armature_object.data.ragdoll.deform_rig
        
        for bone in bones:
            if bone.parent:
                empty_name = ""
                
                empty_name = deform_rig.name + "." + bone.name + deform_rig.data.ragdoll.const_suffix
                empty = bpy.data.objects.new(empty_name, None)
                bpy.context.collection.objects.link(empty)
                
                vec = (bone.head - bone.tail)
                trans = mathutils.Matrix.Translation(vec)
                bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
                            
                empty.matrix_local = bone.matrix
                empty.parent = deform_rig
                empty.parent_type = 'BONE'
                empty.parent_bone = bone.name
                empty.matrix_parent_inverse = bone.matrix.inverted() @ trans
                empty.empty_display_size = 0.15
                empty.rigid_body_constraint.type = 'GENERIC'
                
                name_0 = deform_rig.name + "." + bone.name + deform_rig.data.ragdoll.rb_suffix
                name_1 = deform_rig.name + "." + bone.parent.name + deform_rig.data.ragdoll.rb_suffix
                geo0 = bpy.data.objects[name_0]
                geo1 = bpy.data.objects[name_1]
                empty.rigid_body_constraint.object1 = geo0
                empty.rigid_body_constraint.object2 = geo1
                empties.append(empty)

        # add empties to collection
        collection_name = deform_rig.name + deform_rig.data.ragdoll.const_suffix
        collection = ragdoll_aux.collection_objects_add(collection_name, empties)
        ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, empties)
        # TODO: get objs current collection
        armature_object.data.ragdoll.constraints = collection
        deform_rig.data.ragdoll.constraints = collection


        bpy.context.scene.frame_current = f_init
        print("Info: rd constraints added")
        print("Info: rd constraint limits set")
           

def rb_constraint_defaults():
        
        control_rig = ragdoll_aux.validate_selection(bpy.context.object)

        if control_rig:
            constraints = control_rig.data.ragdoll.constraints
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
                            rb_const.limit_lin_x_lower = 0
                            rb_const.limit_lin_x_upper = 0
                            rb_const.limit_lin_y_lower = 0
                            rb_const.limit_lin_y_upper = 0
                            rb_const.limit_lin_z_lower = 0
                            rb_const.limit_lin_z_upper = 0
                            
                            rb_const.limit_ang_x_lower = math.radians(-22.5)
                            rb_const.limit_ang_x_upper = math.radians(22.5)
                            rb_const.limit_ang_y_lower = math.radians(-22.5)
                            rb_const.limit_ang_y_upper = math.radians(22.5)
                            rb_const.limit_ang_z_lower = math.radians(-22.5)
                            rb_const.limit_ang_z_upper = math.radians(22.5) 
                            
                            # stripped_name = posebone.name

                            # if "strip" in control_rig.config:
                            #     for i in range(len(control_rig.config["strip"])):
                            #         stripped_name = stripped_name.replace(control_rig.config["strip"][i],"")

                            # try:
                            #     bn = control_rig.config["bones"][stripped_name] 
                            #     print(bn)
                            #     rb_const.limit_ang_x_lower = math.radians(bn["limit_ang_x_lower"])
                            #     rb_const.limit_ang_x_upper = math.radians(bn["limit_ang_x_upper"])
                            #     rb_const.limit_ang_y_lower = math.radians(bn["limit_ang_y_lower"])
                            #     rb_const.limit_ang_y_upper = math.radians(bn["limit_ang_y_upper"])
                            #     rb_const.limit_ang_z_lower = math.radians(bn["limit_ang_z_lower"])
                            #     rb_const.limit_ang_z_upper = math.radians(bn["limit_ang_z_upper"])
                            
                            # except KeyError:
                            #     pass


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
        rb_constraint_defaults()



#-------- additional hierarchy layer to copy transforms from, as rigid body meshes' pivots need to be centered --------
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
    # add custom property to ctrl armature to switch animation/simulationv
    control_rig.data["rd_influence"] = 1.0

    for bone in deform_rig.pose.bones:
        # add driver to copy ragdoll transform constraint
        for const in bone.constraints:
            # TODO: not use constraints' names. custom props and pointers seem to be off stable API for constraints? 
            if 'RD' in const.name or 'CTRL' in const.name:
                rd_influence = const.driver_add("influence")
                rd_influence.driver.type = 'SCRIPTED'
                var = rd_influence.driver.variables.new()
                var.name = "rd_influence"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'ARMATURE'
                target.id = control_rig.data
                target.data_path = '["rd_influence"]'
                rd_influence.driver.expression = "rd_influence"

                if 'CTRL' in const.name:
                    rd_influence.driver.expression = "1 - rd_influence"

    print("Info: bone constraint drivers set")