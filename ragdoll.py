import bpy
import math
import mathutils
import ragdoll_aux

#---------------- data structure storing rigid body and armature data per bone ----------------
class RigidBodyBone():
    def __init__(self):
        self.deform_rig_name = None     
        self.ctrl_rig = None
        self.posebone = None
        self.geo = None
        self.parent_geo = None
        self.rb_constraint_obj = None 
        self.rb_connect_obj = None
        self.copy_transforms_rd = None
        self.copy_transforms_ctrl = None

# target_armature : bpy.props.PointerProperty(type = bpy.types.Object, name = "Armature", update = functions.create_armature, poll=armature_poll)`
 

def armature_poll(self, object):
    return object.type == 'ARMATURE'




class RagDollPropGroup(bpy.types.PropertyGroup):
    deform_rig: bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_poll)
    control_rig: bpy.props.PointerProperty(type=bpy.types.Object,poll=armature_poll)
    rigid_bodies: bpy.props.PointerProperty(type=bpy.types.Collection)
    constraints: bpy.props.PointerProperty(type=bpy.types.Collection)
    connectors: bpy.props.PointerProperty(type=bpy.types.Collection)
    type: bpy.props.EnumProperty(items=[
                                                            ('CONTROL', "Control Rig", "Control Rig of a RagDoll"),
                                                            ('DEFORM', "Deform Rig", "Deform Rig of a RagDoll")                          
                                                            ], default='DEFORM')
    config: bpy.props.PointerProperty(type=bpy.types.Text)

    ctrl_rig_postfix: bpy.props.StringProperty(name="Control Rig Postfix", default=".Control")
    def_rig_postfix: bpy.props.StringProperty(name="Deform Rig Postfix", default=".Deform")
    rb_postfix: bpy.props.StringProperty(name="Ragdoll Geo Postfix", default=".RigidBody")
    const_postfix: bpy.props.StringProperty(name="Rigid Body Constraint Postfix", default=".Constraint")
    connect_postfix: bpy.props.StringProperty(name="Connector Postfix", default=".Connect")
    rb_bone_width: bpy.props.FloatProperty(name="Rigid Body Geo Width", default=0.1)

    initialized: bpy.props.BoolProperty(name="RagDoll initialized", default=False)


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
        # armature_object.data.ragdoll.initialized = True



        print("ragdoll created!")

def secondary_rig_add(armature_object):
    if armature_object:
        secondary_rig = armature_object.copy()
        secondary_rig.name = armature_object.name + armature_object.data.ragdoll.ctrl_rig_postfix
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
            geo_name = deform_rig.name + "." + pb.name + deform_rig.data.ragdoll.rb_postfix
            # add and scale box geometry per bone
            new_cube = ragdoll_aux.cube(1, geo_name)
            new_cube.display_type = 'WIRE'

            for vert in new_cube.data.vertices:
                #TODO: consider armatures w/ scales other than 1
                vert.co[0] *= 1 / new_cube.dimensions[1] * deform_rig.data.ragdoll.rb_bone_width
                vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
                vert.co[2] *= 1 / new_cube.dimensions[1] * deform_rig.data.ragdoll.rb_bone_width

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
    collection_name = deform_rig.name + bpy.context.object.data.ragdoll.rb_postfix
    collection = ragdoll_aux.collection_objects_add(collection_name, [rb_geo for rb_geo in rb_bones])
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, [rb_geo for rb_geo in rb_bones])
    control_rig.data.ragdoll.rigid_bodies = collection
    # ctrl_rig.data.ragdoll.rigid_body_constraints = collection

    
    # restore current frame
    bpy.context.scene.frame_current = f_init


def rag_doll_remove(armature_object):
    armature_object = bpy.context.active_object
    if armature_object.type == 'ARMATURE' and armature_object.data.ragdoll.type == 'CONTROL':
        rigid_bodies = armature_object.data.ragdoll.rigid_bodies
        constraints = armature_object.data.ragdoll.constraints
        connectors = armature_object.data.ragdoll.connectors

        collection_remove(rigid_bodies)
        collection_remove(constraints)
        collection_remove(connectors)

        armature_object.data.ragdoll.deform_rig.data.ragdoll.initialized = False
        bpy.data.objects.remove(armature_object, do_unlink=True)

        print("ragdoll removed!")


def collection_remove(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.scene.collection.children.unlink(collection)


def rag_doll_update(context):
    control_rig = context.object
    rd_constraint_limit(control_rig)
    print("ragdoll updated!")


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
                
                empty_name = deform_rig.name + "." + bone.name + deform_rig.data.ragdoll.const_postfix
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
                print(deform_rig.name)
                print(bone.name)
                print(deform_rig.data.ragdoll.rb_postfix)
                name_0 = deform_rig.name + "." + bone.name + deform_rig.data.ragdoll.rb_postfix
                name_1 = deform_rig.name + "." + bone.parent.name + deform_rig.data.ragdoll.rb_postfix
                geo0 = bpy.data.objects[name_0]
                geo1 = bpy.data.objects[name_1]
                empty.rigid_body_constraint.object1 = geo0
                empty.rigid_body_constraint.object2 = geo1
                empties.append(empty)

        # add empties to collection
        collection_name = deform_rig.name + deform_rig.data.ragdoll.const_postfix
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
        print("pipiMama")
        config_data = ragdoll_aux.config_load(config.filepath)
        for obj in control_rig.data.ragdoll.constraints.objects:
            if obj.rigid_body_constraint:
                constraint = obj.rigid_body_constraint
                stripped_name = obj.name.rstrip(control_rig.data.ragdoll.const_postfix)
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

#-------- additional hierarchy layer to copy transforms from, as rigid body meshes' pivots need to be centered --------
def rb_connectors_add(control_rig):
    # store current frame & tmp reset to 0
    f_init = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = 0
    empties = []
    bones = ragdoll_aux.get_visible_posebones()
    deform_rig = control_rig.data.ragdoll.deform_rig

    for bone in bones:
        geo_name = deform_rig.name + "." + bone.name + control_rig.data.ragdoll.rb_postfix
        geo = bpy.data.objects.get(geo_name)

        if geo:
            # add empty
            empty_name = ""
            empty_name = deform_rig.name + "." + bone.name + control_rig.data.ragdoll.connect_postfix
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
    collection_name = deform_rig.name + control_rig.data.ragdoll.const_postfix
    collection = ragdoll_aux.collection_objects_add(collection_name, empties)
    ragdoll_aux.collection_objects_remove(bpy.context.scene.collection, empties)
    # TODO: get objs current collection
    control_rig.data.ragdoll.constraints = collection
    deform_rig.data.ragdoll.constraints = collection


    # reset current frame to initial value
    bpy.context.scene.frame_current = f_init

    print("Info: rd connectors added")


def bone_constraints_add(bones, control_rig):
    # control_rig = ragdoll_aux.validate_selection(bpy.context.object, 'ARMATURE')
    
    for bone in bones:
        deform_rig_name = bone.id_data.name
        connector_name = deform_rig_name + "." + bone.name + control_rig.data.ragdoll.connect_postfix
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





















#---------------- data structure storing rigid body and armature data  ----------------
class RagDoll():
    def __init__(self, config_file = None):
        # TODO: validate config file
        self.config = ragdoll_aux.config_load(config_file)
        self.deform_rig = ragdoll_aux.validate_selection(bpy.context.object)
        if self.deform_rig.users_collection[0] == bpy.context.scene.collection:
            self.collection = ragdoll_aux.collection_objects_add(self.deform_rig.name, [self.deform_rig])
        else:
            self.collection = self.deform_rig.users_collection[0] 
        
        self.deform_rig.data.ragdoll_type = 'DEFORM'
        self.ctrl_rig = None
        self.rb_bones = None
        

    def remove(self):
        pass

    def update(self):
        pass

    #-------- duplicate selected armature to separate mesh deform from control --------
    def ctrl_rig_add(self):
        if self.deform_rig != None:
            ctrl_rig_obj = self.deform_rig.copy()
            ctrl_rig_obj.name = self.deform_rig.name + self.deform_rig.data.ctrl_rig_postfix
            ctrl_rig_obj.data = self.deform_rig.data.copy() # necessary?
            
            bpy.context.collection.objects.link(ctrl_rig_obj)
            ctrl_rig_obj.data.ragdoll_type = 'CONTROL'    
            
            if ctrl_rig_obj.data.display_type == 'OCTAHEDRAL':
                ctrl_rig_obj.data.display_type = 'STICK'
            else:
                ctrl_rig_obj.data.display_type = 'OCTAHEDRAL'

            ctrl_rig_obj.data["rd_influence"] = 1.0
            ctrl_rig_obj.data.id_properties_ensure()  # Make sure the manager is updated
            property_manager = ctrl_rig_obj.data.id_properties_ui("rd_influence")
            property_manager.update(min=0, max=1)

            ctrl_rig_obj.data["kinematic"] = False
            print("Info: ctrl rig added")

            ragdoll_aux.collection_objects_add(self.collection.name, [ctrl_rig_obj])
            
            # ctrl_rig_obj.data.rag_doll = RagDollPropGroup()
            self.ctrl_rig = ctrl_rig_obj
        

        else:
            print("Error: No active armature.")
            return None

    #-------- add rigid body meshes for selected bones, transform & parent to ctrl rig bones --------
    def rb_cubes_add(self):
        pbones = ragdoll_aux.get_visible_posebones()
        rb_bones = []
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0

        for pb in pbones:
            geo_name = self.deform_rig.name + "." + pb.name + self.deform_rig.data.rb_postfix
            # add and scale box geometry per bone
            new_cube = ragdoll_aux.cube(1, geo_name)
            new_cube.display_type = 'WIRE'
            rd_bone = RigidBodyBone()
            rd_bone.geo = new_cube
            rd_bone.ctrl_rig = self.ctrl_rig

            for vert in new_cube.data.vertices:
                #TODO: consider armatures w/ scales other than 1
                vert.co[0] *= 1 / new_cube.dimensions[1] * self.deform_rig.data.rb_bone_width
                vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
                vert.co[2] *= 1 / new_cube.dimensions[1] * self.deform_rig.data.rb_bone_width

            rd_bone.geo = new_cube
            rd_bone.posebone = pb
            rd_bone.deform_rig_name = pb.id_data.name
            
            if pb.parent:
                try:
                    parent_name = new_cube.name.replace(pb.name, pb.parent.name)
                    parent = bpy.data.objects[parent_name] if parent_name in bpy.data.objects else None
                    rd_bone.parent_geo = parent if pb.parent in pbones else None
                except KeyError:
                    pb.parent = None
                    
            # parent cube to control rig bone
            new_cube.matrix_local = pb.matrix
            new_cube.parent = self.ctrl_rig
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
            target.id = self.ctrl_rig.data
            target.data_path = '["kinematic"]'

            rb_bones.append(rd_bone)
            
        # add cubes to collection
        collection_name = self.deform_rig.name + ".RigidBodies"
        collection = ragdoll_aux.collection_objects_add(collection_name, [rbb.geo for rbb in rb_bones])
        self.collection.children.link(collection)
        bpy.context.scene.collection.children.unlink(collection)
        self.deform_rig.data.rigid_body_collection = collection
        self.ctrl_rig.data.rigid_body_constraint_collection = collection

        self.rb_bones = rb_bones
        
        # restore current frame
        bpy.context.scene.frame_current = f_init


    #-------- add constraints or 'joints' connecting rigid body meshes --------
    def rb_constraints_add(self):
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0
        empties = []

        for rbb in self.rb_bones:
            if rbb.parent_geo:
                empty_name = ""
                empty_name = rbb.deform_rig_name + rbb.posebone.name + self.deform_rig.data.const_postfix
                empty = bpy.data.objects.new(empty_name, None)
                bpy.context.collection.objects.link(empty)
                
                def_rig = bpy.data.objects[rbb.deform_rig_name]
                posebone = def_rig.pose.bones[rbb.posebone.name]
                
                vec = (posebone.head - posebone.tail)
                trans = mathutils.Matrix.Translation(vec)
                # TODO: add rigid body constraint collection, how?
                bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
                            
                empty.matrix_local = posebone.matrix
                empty.parent = def_rig
                empty.parent_type = 'BONE'
                empty.parent_bone = rbb.posebone.name
                empty.matrix_parent_inverse = posebone.matrix.inverted() @ trans
                empty.empty_display_size = 0.15
                empty.rigid_body_constraint.type = 'GENERIC'
                empty.rigid_body_constraint.object1 = rbb.geo
                empty.rigid_body_constraint.object2 = rbb.parent_geo
                rbb.rb_constraint_obj = empty
                empties.append(empty)
                self.rb_constraint_limits_set(rbb)

        # add empties to collection
        collection_name = self.deform_rig.name + ".RigidBodyConstraints"
        collection = ragdoll_aux.collection_objects_add(collection_name, empties)
        self.collection.children.link(collection)
        bpy.context.scene.collection.children.unlink(collection)

        self.deform_rig.data.rigid_body_constraint_collection = collection
        self.ctrl_rig.data.rigid_body_constraint_collection = collection


        bpy.context.scene.frame_current = f_init
        print("Info: rd constraints added")
        print("Info: rd constraint limits set")

    #-------- limit constraints'/joints' linear & angular movement  --------
    def rb_constraint_limits_set(self, rd_bone):
        rb_const = rd_bone.rb_constraint_obj.rigid_body_constraint

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
                
                stripped_name = rd_bone.posebone.name

                if "strip" in self.config:
                    for i in range(len(self.config["strip"])):
                        stripped_name = stripped_name.replace(self.config["strip"][i],"")

                try:
                    bn = self.config["bones"][stripped_name] 
                    print(bn)
                    rb_const.limit_ang_x_lower = math.radians(bn["limit_ang_x_lower"])
                    rb_const.limit_ang_x_upper = math.radians(bn["limit_ang_x_upper"])
                    rb_const.limit_ang_y_lower = math.radians(bn["limit_ang_y_lower"])
                    rb_const.limit_ang_y_upper = math.radians(bn["limit_ang_y_upper"])
                    rb_const.limit_ang_z_lower = math.radians(bn["limit_ang_z_lower"])
                    rb_const.limit_ang_z_upper = math.radians(bn["limit_ang_z_upper"])
                
                except KeyError:
                    pass


    #-------- additional hierarchy layer to copy transforms from, as rigid body meshes' pivots need to be centered --------
    def rb_connectors_add(self):
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0
        empties = []

        for rbb in self.rb_bones:
            # add empty
            empty_name = ""
            empty_name = rbb.deform_rig_name + "." + rbb.posebone.name + self.deform_rig.data.connect_postfix
            empty = bpy.data.objects.new(empty_name, None)
            bpy.context.collection.objects.link(empty)
            
            # set & store position
            empty.matrix_world = self.deform_rig.matrix_world @ rbb.posebone.matrix
            obj_matrix = empty.matrix_world.copy()
            
            # set parent
            empty.parent_type = 'OBJECT'
            empty.parent = rbb. geo
            
            # remove parent inverse transform
            empty.matrix_world.identity()
            bpy.context.view_layer.update()
            empty.matrix_world = obj_matrix 

            # modifiy visualization
            empty.empty_display_type = 'SPHERE'
            empty.empty_display_size = 0.1

            rbb.rb_connect_obj = empty
            empties.append(empty)

        # add empties to collection
        collection_name = self.deform_rig.name + ".RigidBodyConnectors"
        collection = ragdoll_aux.collection_objects_add(collection_name, empties)
        self.collection.children.link(collection)
        bpy.context.scene.collection.children.unlink(collection)
        self.deform_rig.data.rigid_body_connector_collection = collection
        self.ctrl_rig.data.rigid_body_connector_collection = collection


        # reset current frame to initial value
        bpy.context.scene.frame_current = f_init

        print("Info: rd connectors added")

    #-------- copy transforms to bone from either simulation or control rig --------
    def bone_constraints_add(self):
        for rbb in self.rb_bones:
            connector = rbb.rb_connect_obj
            # add copy transform constraint for simulation
            rbb.copy_transforms_rd = rbb.posebone.constraints.new('COPY_TRANSFORMS')
            rbb.copy_transforms_rd.name = "Copy Transforms RD"
            rbb.copy_transforms_rd.target = connector
            # add copy transform constraint for animation
            rbb.copy_transforms_ctrl = rbb.posebone.constraints.new('COPY_TRANSFORMS')
            rbb.copy_transforms_ctrl.name = "Copy Transforms Ctrl"
            rbb.copy_transforms_ctrl.target = rbb.ctrl_rig
            rbb.copy_transforms_ctrl.subtarget = rbb.posebone.name
        
        print("Info: bone constraints set")

    #-------- controls to drive all bone constraints from a single value in ctrl armature's data tab --------
    def bone_drivers_add(self):
        # add custom property to ctrl armature to switch animation/simulationv
        self.ctrl_rig.data["rd_influence"] = 1.0
    
        for rbb in self.rb_bones:
            # add driver to copy ragdoll transform constraint 
            rd_influence = rbb.copy_transforms_rd.driver_add('influence') 
            rd_influence.driver.type = 'SCRIPTED'
            rd_influence.driver.expression = "rd_influence"
            var = rd_influence.driver.variables.new()
            var.name = "rd_influence"
            var.type = 'SINGLE_PROP'
            target = var.targets[0]
            target.id_type = 'ARMATURE'
            target.id = self.ctrl_rig.data
            target.data_path = '["rd_influence"]'
            
            # add driver to copy ctrl armature transform constraint 
            ctrl_influence = rbb.copy_transforms_ctrl.driver_add('influence')
            ctrl_influence.driver.type = 'SCRIPTED'
            ctrl_influence.driver.expression = "rd_influence"
            var = ctrl_influence.driver.variables.new()
            var.name = "rd_influence"
            var.type = 'SINGLE_PROP'
            target = var.targets[0]
            target.id_type = 'ARMATURE'
            target.id = self.ctrl_rig.data
            target.data_path = '["rd_influence"]'
            ctrl_influence.driver.expression = "1 - rd_influence"
            