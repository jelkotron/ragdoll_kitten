import bpy
import math
import mathutils
C = bpy.context
D = bpy.data

rd_postfix = ".RD"
const_postfix = ".CONST"
connect_postfix = ".CONNECT"
ctrl_rig_postfix = ".CTRL"

default_limit_lin = [0,0]

default_limit_ang = [5,5]

rb_bone_width = 0.1

armature_ctrl = None
armature_deform = C.object # why is this not updated by add_rd_cubes?

strip_list = ["mixamorig:"]

ang_limits =   {
                "LeftLeg": [
                    [-120, 0], 
                    [default_limit_ang[0], default_limit_ang[1]], 
                    [default_limit_ang[0], default_limit_ang[1]],
                ],
                                
                "RightLeg": [
                    [-120, 0], 
                    [default_limit_ang[0], default_limit_ang[1]], 
                    [default_limit_ang[0], default_limit_ang[1]],
                    ],

                "LeftUpLeg": [
                    [-22.5, 90], 
                    [-22.5, 22.5], 
                    [-45, 5],
                ],
                                
                "RightUpLeg": [
                    [-22.5, 90], 
                    [-22.5, 22.5], 
                    [-45, 5],
                ],
                "Spine": [
                    [-22.5, 22.5], 
                    [-12, 12], 
                    [-10, 10],
                ],
                "Spine1": [
                    [-22.5, 22.5], 
                    [-12, 12], 
                    [-10, 10],
                ],
                "Spine2": [
                    [-10, 10], 
                    [-12, 12], 
                    [-10, 10],
                ],
                "LeftShoulder": [
                    [-22.5, 22.5], 
                    [-1, 1], 
                    [-22.5, 22.5],
                ],
                "RightShoulder": [
                    [-22.5, 22.5], 
                    [-1, 1], 
                    [-22.5, 22.5],
                ],
                "LeftArm": [
                    [-90, 90], 
                    [-0, 0], 
                    [90, -22.5],
                ],
                "RightArm": [
                    [90, -90], 
                    [-0, 0], 
                    [-90, 22.5],
                ],
                "LeftForeArm": [
                    [-0, 0], 
                    [-0, 0], 
                    [-0, 120],
                ],
                "RightForeArm": [
                    [-0, 0], 
                    [-0, 0], 
                    [-120, 0],
                ],
                "LeftHand": [
                    [-60, 60], 
                    [-22.5, 22.5], 
                    [-10, 10],
                ],
                "RightHand": [
                    [-60, 60], 
                    [-22.5, 22.5], 
                    [-10, 10],
                ],
                }



def cube():
    verts = [
            (1.0, 1.0, -1.0),
            (1.0, -1.0, -1.0),
            (-1.0, -1.0, -1.0),
            (-1.0, 1.0, -1.0), 
            (1.0, 1.0, 1.0), 
            (1.0, -1.0, 1.0), 
            (-1.0, -1.0, 1.0), 
            (-1.0, 1.0, 1.0)
            ] 
                
    faces = [
            (0, 1, 2, 3), 
            (4, 7, 6, 5), 
            (0, 4, 5, 1), 
            (1, 5, 6, 2), 
            (2, 6, 7, 3), 
            (4, 0, 3, 7)
            ]

    rd_name = "Cube"
    mesh = bpy.data.meshes.new(rd_name) 
    mesh.from_pydata(verts, [], faces)
    cube = bpy.data.objects.new(rd_name, mesh) 
    bpy.context.scene.collection.objects.link(cube)

    return cube        

def add_ctrl_rig(deform_rig_obj):
    ctrl_rig_obj = deform_rig_obj.copy()
    ctrl_rig_obj.name = deform_rig_obj.name + ".ctrl"
    ctrl_rig_obj.data = deform_rig_obj.data.copy()
    
    bpy.context.collection.objects.link(ctrl_rig_obj)
        
    if ctrl_rig_obj.data.display_type == 'OCTAHEDRAL':
        ctrl_rig_obj.data.display_type = 'STICK'
    else:
        ctrl_rig_obj.data.display_type = 'OCTAHEDRAL'

    ctrl_rig_obj.data["rd_influence"] = 1.0
    ctrl_rig_obj.data.id_properties_ensure()  # Make sure the manager is updated
    property_manager = ctrl_rig_obj.data.id_properties_ui("rd_influence")
    property_manager.update(min=0, max=1)

    ctrl_rig_obj.data["kinematic"] = True

    return ctrl_rig_obj
    

# add Cubes, parent them to bones
def add_rd_cubes():
    C.scene.frame_current = 0
    armature_deform = C.object
    armature_ctrl = add_ctrl_rig(armature_deform)
    
    for pb in C.selected_pose_bones:
        new_cube = cube()
        
        for vert in new_cube.data.vertices:
            vert.co[0] *= 1 / new_cube.dimensions[1] * rb_bone_width
            vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
            vert.co[2] *= 1 / new_cube.dimensions[1] * rb_bone_width
                   
        new_cube.name = armature_deform.name + "." + pb.name + rd_postfix
        new_cube.matrix_local = pb.matrix
        new_cube.parent = armature_ctrl
        new_cube.parent_type = 'BONE'
        new_cube.parent_bone = pb.name

        vec = (C.object.pose.bones[pb.name].head - C.object.pose.bones[pb.name].tail) / 2
        trans = mathutils.Matrix.Translation(vec)
        new_cube.matrix_parent_inverse = pb.matrix.inverted() @ trans

        C.scene.rigidbody_world.collection.objects.link(new_cube)
        new_cube.rigid_body.collision_shape = 'BOX'
        
        # driver: global kinetic switch from ctrl armature  
        kinematic_driver = new_cube.rigid_body.driver_add("kinematic")
        kinematic_driver.driver.type = 'SCRIPTED'
        kinematic_driver.driver.expression = "var"
        var = kinematic_driver.driver.variables.new()
        var.name = "var"
        var.type = 'SINGLE_PROP'
        target = var.targets[0]
        target.id_type = 'ARMATURE'
        target.id = armature_ctrl.data
        target.data_path = '["kinematic"]'
        
        
    
# adds rb constraint objects, parents them to bones
def add_empty(mode = 'CONSTRAINT'):
    for pb in C.selected_pose_bones:
        armature = pb.id_data 
        empty_name = ""
        if mode == 'CONSTRAINT':
            empty_name = armature.name + "." + pb.name + const_postfix
            
        elif mode == 'CONNECT':
            empty_name = armature.name + "." + pb.name + connect_postfix
            
        empty = bpy.data.objects.new(empty_name, None)
        bpy.context.collection.objects.link(empty)
        vec = (C.object.pose.bones[pb.name].head - C.object.pose.bones[pb.name].tail)
        trans = mathutils.Matrix.Translation(vec)
       
        C.scene.rigidbody_world.constraints.objects.link(empty)
        
        if mode == 'CONSTRAINT':
            empty.matrix_local = pb.matrix
            empty.parent = armature
            empty.parent_type = 'BONE'
            empty.parent_bone = pb.name
            empty.matrix_parent_inverse = pb.matrix.inverted() @ trans
            empty.empty_display_size = 0.15
            empty.rigid_body_constraint.type = 'GENERIC'
            set_constraint_limits(empty, armature.name)
            
            try:
                parent_bone = pb.parent
                if parent_bone != None:
                    empty.rigid_body_constraint.object1 = D.objects[armature.name + "." + pb.name + rd_postfix]
                    empty.rigid_body_constraint.object2 = D.objects[armature.name + "." + pb.parent.name + rd_postfix]
                
            except KeyError as e:
                print(e)
            
                
        elif mode == 'CONNECT':
            try:
                empty.parent_type = 'OBJECT'
                rd_object = D.objects[empty.name.replace(connect_postfix, rd_postfix)]
               
                empty.empty_display_type = 'SPHERE'
                empty.matrix_world = C.object.matrix_world @ C.object.pose.bones[pb.name].matrix 
                ob_matrix_orig = empty.matrix_world.copy()
                empty.parent = rd_object
                empty.matrix_world.identity()
                bpy.context.view_layer.update()
                empty.matrix_world = ob_matrix_orig 
                empty.empty_display_size = 0.1
                
         
            except KeyError as e:
                print(e)
            


def set_constraint_limits(obj, armature_name):
    obj.rigid_body_constraint.use_limit_lin_x = True
    obj.rigid_body_constraint.use_limit_lin_y = True
    obj.rigid_body_constraint.use_limit_lin_z = True
    
    obj.rigid_body_constraint.use_limit_ang_x = True
    obj.rigid_body_constraint.use_limit_ang_y = True
    obj.rigid_body_constraint.use_limit_ang_z = True
    
    obj.rigid_body_constraint.limit_lin_x_lower = default_limit_lin[0]
    obj.rigid_body_constraint.limit_lin_x_upper = default_limit_lin[1]
    obj.rigid_body_constraint.limit_lin_y_lower = default_limit_lin[0]
    obj.rigid_body_constraint.limit_lin_y_upper = default_limit_lin[1]
    obj.rigid_body_constraint.limit_lin_z_lower = default_limit_lin[0]
    obj.rigid_body_constraint.limit_lin_z_upper = default_limit_lin[1]
    
    obj.rigid_body_constraint.limit_ang_x_lower = math.radians(default_limit_ang[0])
    obj.rigid_body_constraint.limit_ang_x_upper = math.radians(default_limit_ang[1])
    obj.rigid_body_constraint.limit_ang_y_lower = math.radians(default_limit_ang[0])
    obj.rigid_body_constraint.limit_ang_y_upper = math.radians(default_limit_ang[1])
    obj.rigid_body_constraint.limit_ang_z_lower = math.radians(default_limit_ang[0])
    obj.rigid_body_constraint.limit_ang_z_upper = math.radians(default_limit_ang[1]) 
    
    stripped_name = obj.name.replace(const_postfix,"").replace(armature_name, "").lstrip(".")

    
    for i in range(len(strip_list)):
        stripped_name = stripped_name.replace(strip_list[i],"")
        
    if stripped_name in ang_limits:
        obj.rigid_body_constraint.limit_ang_x_lower = math.radians(ang_limits[stripped_name][0][0])
        obj.rigid_body_constraint.limit_ang_x_upper = math.radians(ang_limits[stripped_name][0][1])
        obj.rigid_body_constraint.limit_ang_y_lower = math.radians(ang_limits[stripped_name][1][0])
        obj.rigid_body_constraint.limit_ang_y_upper = math.radians(ang_limits[stripped_name][1][1])
        obj.rigid_body_constraint.limit_ang_z_lower = math.radians(ang_limits[stripped_name][2][0])
        obj.rigid_body_constraint.limit_ang_z_upper = math.radians(ang_limits[stripped_name][2][1])
        

def update_constraint_limits():
    armature = C.object
    constraints = []
    if armature.type == 'ARMATURE':
        for pb in armature.pose.bones:
            const_name = armature.name + "." + pb.name + const_postfix
            if const_name in D.objects:
                constraints.append(D.objects[const_name])
    for c in constraints:
        set_constraint_limits(c, armature.name)


def garbage_collect(type='ARMATURE'):
    junk = []
    if type == 'ARMATURE':
        for i in range(len(D.armatures)):
            arm = D.armatures[i]
            if arm.users == 0:
                junk.append(arm)
        for i in range(len(junk)):
            arm = junk[i]
            D.armatures.remove(arm, do_unlink = True)
    
    junk = []
        
        
 
        
def add_copytrans(): 
    if armature_deform != None:
        armature_ctrl = D.objects[armature_deform.name + ".ctrl"] # TODO: set by function creating ctrl armature
        
        # add custom armature properties
        armature_deform.data["rd_influence"] = 1.0
        armature_ctrl.data.id_properties_ensure()  # Make sure the manager is updated
        property_manager = armature_ctrl.data.id_properties_ui("rd_influence")
        property_manager.update(min=0, max=1)
        
        # constraints and drivers
        for pb in C.selected_pose_bones:
            try:
                # get connector object
                connector_name = armature_deform.name + "." + pb.name + connect_postfix
                connector = D.objects[connector_name]
                
                # add constraint to copy transforms from ragdoll geometry
                rdconst = pb.constraints.new('COPY_TRANSFORMS')
                rdconst.target = connector
                rdconst.name = "Copy Transforms RD"                
                
                # add driver to globally control constraint influence
                driver = rdconst.driver_add('influence')
                driver.driver.type = 'SCRIPTED'
                driver.driver.expression = "var"
                var = driver.driver.variables.new()
                var.name = "var"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]

                target.id_type = 'ARMATURE'
                target.id = armature_deform.data
                target.data_path = '["rd_influence"]'
                
                # add constraint to copy transforms from ctrl armature
                ctrl_const = pb.constraints.new('COPY_TRANSFORMS') 
                ctrl_const.target = armature_ctrl
                ctrl_const.subtarget = pb.name
                ctrl_const.name = "Copy Transforms Ctrl"
                
                # add driver to set ctrl armature influence inversely proportianal to rd influence
                driver = ctrl_const.driver_add('influence')
                driver.driver.type = 'SCRIPTED'
                driver.driver.expression = "1-var"
                var = driver.driver.variables.new()
                var.name = "var"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'ARMATURE'
                target.id = armature_deform.data
                target.data_path = '["rd_influence"]'
                
                armature_ctrl.data["rd_influence"] = 1.0
                bpy.context.view_layer.update()
            
            except KeyError as e:
                pass        

        # driver: deform rig rd_influence using ctrl rig property
        rd_driver = armature_deform.data.driver_add('["rd_influence"]')
        rd_driver.driver.type = 'SCRIPTED'
        rd_driver.driver.expression = "var"
        var = rd_driver.driver.variables.new()
        var.name = "var"
        var.type = 'SINGLE_PROP'
        target = var.targets[0]
        target.id_type = 'ARMATURE'
        target.id = armature_ctrl.data
        target.data_path = '["rd_influence"]'
            

garbage_collect('ARMATURE')
add_rd_cubes()
add_empty('CONSTRAINT')
add_empty('CONNECT')
add_copytrans()
#update_constraint_limits()