import bpy
import json
import os

#######################################################################################
######################################## Bones ########################################
#------------ create dictionary w/ bones' level in tree ------------------------
def bones_tree_levels_get(armature):
    pose_bones = armature.pose.bones
    max_level = 0

    root_level_bones = []
    for bone in pose_bones:
        if bone.parent == None:
            root_level_bones.append(bone)

    levels = {}
            
    for bone in root_level_bones:
        bone_map_children(bone, levels)


    return levels

#------------ recursively iterate over bones' children to map their position in tree
def bone_map_children(root, map_obj, level=0):
    if root.name not in map_obj: 
        map_obj[root.name] = level
    for child in root.children:
        bone_map_children(child, map_obj, level+1)

#------------ set bones' hierarchy property ------------------------
def bones_tree_levels_set(armature, pose_bones_to_use):
    level_map = bones_tree_levels_get(armature)
    for bone in armature.pose.bones:
        if bone.name in level_map:
            bone.ragdoll.tree_level = level_map[bone.name]
            if bone in pose_bones_to_use:
                armature.data.ragdoll.bone_level_max = max(armature.data.ragdoll.bone_level_max, level_map[bone.name])
            
    return armature

#------------------------ exclude unselected/hidden pose bones and hidden bone collections ------------------------
def get_visible_posebones(armature_object=None):
    bones = []
    if armature_object.type == 'ARMATURE':
        if bpy.context.mode == 'POSE' and len(bpy.context.selected_pose_bones) > 0:
            bones = [i for i in bpy.context.selected_pose_bones]
            
        elif bpy.context.mode == 'EDIT' and len(bpy.context.selected_bones) > 0:
            bones = [bpy.context.object.pose.bones[i.name] for i in bpy.context.selected_bones]
        
        else:
            invisible_groups = []
            for col in armature_object.data.collections:
                if col.is_visible == False:
                    invisible_groups.append(col.name)
            for bone in armature_object.data.bones:
                visible = not bone.hide
                for col in invisible_groups:
                    if col in bone.collections:
                        visible = False
                if visible == True:
                    bones.append(armature_object.pose.bones[bone.name])

    if(len(bones) > 0):
        return bones
    
    else:
        print("Error: No active armature.")
        return None

#------------------------ remove armatures w/o users ------------------------
def garbage_collect_armatures():
    for arm in bpy.data.armatures:
        if arm.users == 0:
            bpy.data.armatures.remove(arm, do_unlink=True)


###############################################################################################
######################################## Selection ############################################ 
#------------ deselect all objects ------------ 
def deselect_all():
    objs = []
    for obj in bpy.context.selected_objects:
        objs.append(obj)
    for obj in objs:
        obj.select_set(False)

#------------------------ validate object type ------------------------
def validate_selection(selected_object, mode = 'ARMATURE'):
    if selected_object.type == mode:
        return selected_object
    else:
        return None
    

#############################################################################################
######################################## Collections ########################################
#------------------------ add or set rigid body constraint collection ------------------------
def rb_constraint_collection_set(collection_name = 'RigidBodyConstraints'):
    if collection_name not in bpy.data.collections:
        bpy.data.collections.new(collection_name)

    bpy.context.scene.rigidbody_world.constraints = bpy.data.collections[collection_name]    
        
#------------------------ create collection and/or add add objects ------------------------
def object_add_to_collection(collection_name, objects=[]):
    col = None
    if isinstance(type(objects), bpy.types.Object.__class__):
        objects = [objects]

    if collection_name not in bpy.data.collections:
        col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[collection_name]
    
    if col:
        for obj in objects:
            if obj.name not in bpy.data.collections[collection_name].objects:    
                bpy.data.collections[collection_name].objects.link(obj)


    bpy.context.view_layer.update()

    return col

#------------------------ remove objects from collection ------------------------
def object_remove_from_collection(collection, objects):
    if isinstance(type(objects), bpy.types.Object.__class__):
        objects = [objects]

    if collection != None:
        for obj in objects:
            if obj.name in collection.objects:
                collection.objects.unlink(obj)

#------------------------ delete collection & objects ------------------------
def collection_remove(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection, do_unlink=True)


######################################################################################################
######################################## Configuration / JSON ########################################
#------------------------ import json file, set as selected armature's config ------------------------
def load_text(context, filepath=None, datablock=None):
    if filepath and not datablock:
        text = bpy.data.texts.load(filepath)
    
    elif datablock and not filepath:
        text = datablock

    if validate_selection(bpy.context.active_object, 'ARMATURE'):
        context.active_object.data.ragdoll.config = text
        if context.active_object.data.ragdoll.type == 'DEFORM':
            control_rig = context.active_object.data.ragdoll.control_rig 
            if control_rig:
                control_rig.data.ragdoll.config = text

#------------------------ parse json file / internal text content, return dict ------------------------
def config_load(config):
    data = None
    filepath = bpy.path.abspath(config.filepath)

    if config.is_dirty:
        lines = []
        for line in config.lines:
            lines.append(line.body)
        try:
            data = json.loads("\n".join(lines))
            print("Info: JSON Data loaded.")
        except json.decoder.JSONDecodeError as e:
            print(e)
            
    else:
        if os.path.exists(config.filepath):
            with open(filepath, 'r') as file:
                try:
                    data = json.load(file)
                    print("Info: JSON Data loaded.")
                except json.decoder.JSONDecodeError as e:
                    print(e)
    return data

#------------------------ create config file w/ default values ------------------------
def config_create(armature):
    deform_rig = None
    control_rig = None

    if armature.data.ragdoll.type == 'CONTROL':
        control_rig = armature
        deform_rig = armature.data.ragdoll.deform_rig if armature.data.ragdoll.deform_rig else None
    else:
        control_rig = armature.data.ragdoll.control_rig if armature.data.ragdoll.control_rig else None
        deform_rig = armature

    if deform_rig == None:
        deform_rig = armature
    
    filename = deform_rig.name

    i = 1
    while filename + ".json" in bpy.data.texts:
        filename = deform_rig.name + "_" + str(i).zfill(3)
        i += 1

    filename += ".json"

    text_data_block = bpy.data.texts.new(filename)

    data = {
        "strip":[],
        "bones": {}
    }
    for bone in deform_rig.pose.bones:
        if bone.ragdoll.is_ragdoll:
            data["bones"][bone.name] = {
                "limit_ang_x_lower" : -45,
                "limit_ang_x_upper" : 45,
                "limit_ang_y_lower" : -45,
                "limit_ang_y_upper" : 45,
                "limit_ang_z_lower" : -45,
                "limit_ang_z_upper" : 45
            }
            
            
    encoded = json.dumps(data, sort_keys=True, indent=4)
    
    text_data_block.write("".join([i for i in encoded]))

    return text_data_block


##########################################################################################
######################################## Geometry ########################################
#------------------------ add a cube ------------------------
def cube(width, name, mode='OBJECT'):
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
    
    if mode == 'VERTICES':
        return verts

    faces = [
            (0, 1, 2, 3), 
            (4, 7, 6, 5), 
            (0, 4, 5, 1), 
            (1, 5, 6, 2), 
            (2, 6, 7, 3), 
            (4, 0, 3, 7)
            ]

    if mode == 'OBJECT':
        mesh = bpy.data.meshes.new(name) 
        mesh.from_pydata(verts, [], faces)
        cube = bpy.data.objects.new(name, mesh) 
        bpy.context.scene.collection.objects.link(cube)

        return cube 


#########################################################################################
######################################## Drivers ########################################
#------------------------ delete invalid drivers ------------------------
def drivers_remove_invalid(object):
    for d in object.animation_data.drivers:
        if not d.is_valid:
            object.animation_data.drivers.remove(d)

#------------------------ delete ragdoll drivers ------------------------
def drivers_remove_related(object):
    for d in object.animation_data.drivers:
        # TODO: add macros for these names and/or find another way to address these objects
        if 'simulation_influence' in d.driver.expression:
            object.animation_data.drivers.remove(d)

#------------------------ update armature drivers ------------------------
def force_update_drivers(context):
    for armature in [i for i in bpy.data.objects if i.type=='ARMATURE']:
        if armature.animation_data:
            for fcurve in armature.animation_data.drivers:
                if fcurve:
                    # hacky, gets the job done
                    if fcurve.driver.expression.endswith(" "):
                        fcurve.driver.expression = fcurve.driver.expression[:-1]
                    else:
                        fcurve.driver.expression += " "