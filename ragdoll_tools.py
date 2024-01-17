import bpy
import math
import mathutils

class RagDollBone():
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
   

class RagDoll():
    def __init__(self, config_file = None):
        self.config = config_load(config_file)
        self.config["ctrl_rig_postfix"] = ".ctrl"
        self.config["rd_postfix"] = ".RB"
        self.config["const_postfix"] = ".CONST"
        self.config["connect_postfix"] = ".CONNECT"
        self.config["rb_bone_width"] = 0.1
        self.config["strip"] = ["mixamorig:"]

        self.deform_rig = validate_selection(bpy.context.object)
        self.ctrl_rig = None
        self.rd_bones = None


    def ctrl_rig_add(self):
        if self.deform_rig != None:
            ctrl_rig_obj = self.deform_rig.copy()
            ctrl_rig_obj.name = self.deform_rig.name + self.config["ctrl_rig_postfix"]
            ctrl_rig_obj.data = self.deform_rig.data.copy() # necessary?
            
            bpy.context.collection.objects.link(ctrl_rig_obj)
                
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

            self.ctrl_rig = ctrl_rig_obj
        
        else:
            print("Error: No active armature.")
            return None


    def rb_cubes_add(self):
        pbones = get_visible_posebones()
        rd_bones = []
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0

        for pb in pbones:
            geo_name = self.deform_rig.name + "." + pb.name + self.config["rd_postfix"]
            # add and scale box geometry per bone
            new_cube = cube(1, geo_name)
            rd_bone = RagDollBone()
            rd_bone.geo = new_cube
            rd_bone.ctrl_rig = self.ctrl_rig

            for vert in new_cube.data.vertices:
                #TODO: consider armatures w/ scales other than 1
                vert.co[0] *= 1 / new_cube.dimensions[1] * self.config["rb_bone_width"]
                vert.co[1] *= 1 / new_cube.dimensions[1] * pb.length
                vert.co[2] *= 1 / new_cube.dimensions[1] * self.config["rb_bone_width"]

            rd_bone.geo = new_cube
            rd_bone.posebone = pb
            rd_bone.deform_rig_name = pb.id_data.name
            
            if pb.parent:
                try:
                    parent = bpy.data.objects[new_cube.name.replace(pb.name, pb.parent.name)]
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

            rd_bones.append(rd_bone)
            
        # restore current frame
        bpy.context.scene.frame_current = f_init
        self.rd_bones = rd_bones


    def rb_constraints_add(self):
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0

        for rdb in self.rd_bones:
            if rdb.parent_geo:
                empty_name = ""
                empty_name = rdb.deform_rig_name + rdb.posebone.name + self.config["const_postfix"]
                empty = bpy.data.objects.new(empty_name, None)
                bpy.context.collection.objects.link(empty)
                
                def_rig = bpy.data.objects[rdb.deform_rig_name]
                posebone = def_rig.pose.bones[rdb.posebone.name]
                
                vec = (posebone.head - posebone.tail)
                trans = mathutils.Matrix.Translation(vec)
                # TODO: add rigid body constraint collection, how?
                bpy.context.scene.rigidbody_world.constraints.objects.link(empty)
                            
                empty.matrix_local = posebone.matrix
                empty.parent = def_rig
                empty.parent_type = 'BONE'
                empty.parent_bone = rdb.posebone.name
                empty.matrix_parent_inverse = posebone.matrix.inverted() @ trans
                empty.empty_display_size = 0.15
                empty.rigid_body_constraint.type = 'GENERIC'
                empty.rigid_body_constraint.object1 = rdb.geo
                empty.rigid_body_constraint.object2 = rdb.parent_geo
                rdb.rb_constraint_obj = empty
                self.rb_constraint_limits_set(rdb)
                
        bpy.context.scene.frame_current = f_init
        print("Info: rd constraints added")


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

                if "limit_ang" in self.config:
                    if stripped_name in self.config["limit_ang"]:
                        
                        rb_const.rigid_body_constraint.limit_ang_x_lower = math.radians(ang_limits[stripped_name][0][0])
                        rb_const.rigid_body_constraint.limit_ang_x_upper = math.radians(ang_limits[stripped_name][0][1])
                        rb_const.rigid_body_constraint.limit_ang_y_lower = math.radians(ang_limits[stripped_name][1][0])
                        rb_const.rigid_body_constraint.limit_ang_y_upper = math.radians(ang_limits[stripped_name][1][1])
                        rb_const.rigid_body_constraint.limit_ang_z_lower = math.radians(ang_limits[stripped_name][2][0])
                        rb_const.rigid_body_constraint.limit_ang_z_upper = math.radians(ang_limits[stripped_name][2][1])
                print("Info: rd constraint limits set")


    def rb_connectors_add(self):
        # store current frame & tmp reset to 0
        f_init = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0

        for rdb in self.rd_bones:
            # add empty
            empty_name = ""
            empty_name = rdb.deform_rig_name + "." + rdb.posebone.name + self.config["connect_postfix"]
            empty = bpy.data.objects.new(empty_name, None)
            bpy.context.collection.objects.link(empty)
            
            # set & store position
            empty.matrix_world = self.deform_rig.matrix_world @ rdb.posebone.matrix
            obj_matrix = empty.matrix_world.copy()
            
            # set parent
            empty.parent_type = 'OBJECT'
            empty.parent = rdb. geo
            
            # remove parent inverse transform
            empty.matrix_world.identity()
            bpy.context.view_layer.update()
            empty.matrix_world = obj_matrix 

            # modifiy visualization
            empty.empty_display_type = 'SPHERE'
            empty.empty_display_size = 0.1

            rdb.rb_connect_obj = empty

        # reset current frame to initial value
        bpy.context.scene.frame_current = f_init

        print("Info: rd connectors added")


    def bone_constraints_add(self):
        for rdb in self.rd_bones:
            connector = rdb.rb_connect_obj
            # add copy transform constraint for simulation
            rdb.copy_transforms_rd = rdb.posebone.constraints.new('COPY_TRANSFORMS')
            rdb.copy_transforms_rd.name = "Copy Transforms RD"
            rdb.copy_transforms_rd.target = connector
            # add copy transform constraint for animation
            rdb.copy_transforms_ctrl = rdb.posebone.constraints.new('COPY_TRANSFORMS')
            rdb.copy_transforms_ctrl.name = "Copy Transforms Ctrl"
            rdb.copy_transforms_ctrl.target = rdb.ctrl_rig
            rdb.copy_transforms_ctrl.subtarget = rdb.posebone.name
        
        print("Info: bone constraints set")


    def bone_drivers_add(self):
        # add custom property to ctrl armature to switch animation/simulationv
        self.ctrl_rig.data["rd_influence"] = 1.0
    
        for rdb in self.rd_bones:
            # add driver to copy ragdoll transform constraint 
            rd_influence = rdb.copy_transforms_rd.driver_add('influence') 
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
            ctrl_influence = rdb.copy_transforms_ctrl.driver_add('influence')
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
            

def validate_selection(selected_object, mode = 'ARMATURE'):
    if selected_object.type == mode:
        return selected_object
    else:
        return None

def get_visible_posebones():
    bones = []
    if bpy.context.active_object.type == 'ARMATURE':
        if bpy.context.mode == 'POSE' and len(bpy.context.selected_pose_bones) > 0:
            bones = [i for i in bpy.context.selected_pose_bones]
            
        elif bpy.context.mode == 'EDIT' and len(bpy.context.selected_bones) > 0:
            bones = [bpy.context.object.pose.bones[i.name] for i in bpy.context.selected_bones]
        
        else:
            invisible_groups = []
            for col in bpy.context.object.data.collections:
                if col.is_visible == False:
                    invisible_groups.append(col.name)
            for bone in bpy.context.object.data.bones:
                visible = not bone.hide
                for col in invisible_groups:
                    if col in bone.collections:
                        visible = False
                if visible == True:
                    bones.append(bpy.context.object.pose.bones[bone.name])

    if(len(bones) > 0):
        return bones
    
    else:
        print("Error: No active armature.")
        return None

def config_load(filepath):
    print("Info: config loaded.")
    config =  {}
    return config

def cube(width, name):
    verts = [
            (width/2, width/2, -width/2),
            (width/2, -width/2, -width/2),
            (-width/2, -width/2, -width/2),
            (-width/2, width/2, -width/2), 
            (width/2, width/2, width/2), 
            (width/2, -width/2, width/2), 
            (-width/2, -width/2, width/2), 
            (-width/2, width/2, width/2)
            ] 
                
    faces = [
            (0, 1, 2, 3), 
            (4, 7, 6, 5), 
            (0, 4, 5, 1), 
            (1, 5, 6, 2), 
            (2, 6, 7, 3), 
            (4, 0, 3, 7)
            ]

    mesh = bpy.data.meshes.new(name) 
    mesh.from_pydata(verts, [], faces)
    cube = bpy.data.objects.new(name, mesh) 
    bpy.context.scene.collection.objects.link(cube)

    return cube 


def garbage_collect_armatures():
    for arm in bpy.data.armatures:
                if arm.users == 0:
                    bpy.data.armatures.remove(arm, do_unlink=True)

garbage_collect_armatures()
rd = RagDoll()
rd.ctrl_rig_add()
rd.rb_cubes_add()
rd.rb_constraints_add()
rd.rb_connectors_add()
rd.bone_constraints_add()
rd.bone_drivers_add()

#class CustomMenu(bpy.types.Menu):
#    bl_label = "Custom Menu"
#    bl_idname = "OBJECT_MT_custom_menu"

#    def draw(self, context):
#        layout = self.layout
#        
#        if bpy.context.scene.rigidbody_world == None:
#            layout.label(text="Rigid Body World not found.", icon='ERROR')
#            layout.operator("rigidbody.world_add")


#def draw_item(self, context):
#    layout = self.layout
#    layout.menu(CustomMenu.bl_idname)


#def register():
#    bpy.utils.register_class(CustomMenu)

#    # lets add ourselves to the main header
#    bpy.types.INFO_HT_header.append(draw_item)


#def unregister():
#    bpy.utils.unregister_class(CustomMenu)

#    bpy.types.INFO_HT_header.remove(draw_item)


#if __name__ == "__main__":
#    register()

#    # The menu can also be called from scripts
#    bpy.ops.wm.call_menu(name=CustomMenu.bl_idname)
