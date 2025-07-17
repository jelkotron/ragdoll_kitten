import bpy
import json
import os
import math
import mathutils


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
def get_visible_posebones(armature_object=None, selected=True):
    bones = []
    if armature_object and armature_object.type == 'ARMATURE':
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
def deselect_all(context=bpy.context):
    objs = []
    for obj in context.selected_objects:
        objs.append(obj)
    for obj in objs:
        obj.select_set(False)

#------------------------ validate object type ------------------------
def validate_selection(selected_object, mode = 'ARMATURE'):
    if selected_object.type == mode:
        return selected_object
    else:
        return None
    
def select_set_active(context, obj):
    obj.select_set(True)
    context.view_layer.objects.active = obj


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
        if objects:
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
        if objects:
            for obj in objects:
                if obj.name in collection.objects:
                    collection.objects.unlink(obj)

#------------------------ delete collection & objects ------------------------
def collection_remove(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        if collection.name in bpy.context.scene.collection.children: 
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

#------------------------ parse internal json file, read & modify data ------------------------
def config_update(context, bone):
    config = context.object.data.ragdoll.config
    lines = []
    for line in config.lines:
        lines.append(line.body)
    data = None
    try:
        data = json.loads("\n".join(lines))
    except json.decoder.JSONDecodeError as e:
        print(e)

    if data:
        data["default_values"]["distance"] = round(context.object.data.ragdoll.rigid_bodies.constraints.default_distance,4)
        data["default_values"]["rotation"] = round(math.degrees(context.object.data.ragdoll.rigid_bodies.constraints.default_rotation),4)

        if bone.ragdoll.constraint:
            data["bones"][bone.name] = {
                "limit_ang_x_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_x_lower),3),
                "limit_ang_x_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_x_upper),3),
                "limit_ang_y_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_y_lower),3),
                "limit_ang_y_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_y_upper),3),
                "limit_ang_z_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_z_lower),3),
                "limit_ang_z_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_z_upper),3)            
                }
            
            if bone.name != bone.ragdoll.name_previous:
                if data["bones"].get(bone.ragdoll.name_previous):
                    data["bones"].pop(bone.ragdoll.name_previous)

            encoded = json.dumps(data, sort_keys=True, indent=4)
            config.clear()
            config.write("".join([i for i in encoded]))


    

#------------------------ create config file w/ default values ------------------------
def config_create(context):
    armature = context.object
    if armature.data.ragdoll.deform_rig:
        bones = get_visible_posebones(armature.data.ragdoll.deform_rig)
    else:
        bones = get_visible_posebones(armature)

    filename = armature.name

    i = 1
    while filename + ".json" in bpy.data.texts:
        filename = armature.name + "_" + str(i).zfill(3)
        i += 1

    filename += ".json"

    text_data_block = bpy.data.texts.new(filename)

    data = {
        "bones": {},
        "default_values":{
            "distance" : round(context.object.data.ragdoll.rigid_bodies.constraints.default_distance,4),
            "rotation" : round(math.degrees(context.object.data.ragdoll.rigid_bodies.constraints.default_rotation),4)
            }
    }
    for bone in bones:
        if bone.ragdoll.constraint:
            data["bones"][bone.name] = {
                "limit_ang_x_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_x_lower),3),
                "limit_ang_x_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_x_upper),3),
                "limit_ang_y_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_y_lower),3),
                "limit_ang_y_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_y_upper),3),
                "limit_ang_z_lower" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_z_lower),3),
                "limit_ang_z_upper" : round(math.degrees(bone.ragdoll.constraint.rigid_body_constraint.limit_ang_z_upper),3)  
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

    mesh = bpy.data.meshes.new(name) 
    mesh.from_pydata(verts, [], faces)
    
    if mode == 'DATA':
        return mesh
    
    elif mode == 'OBJECT':
        cube = bpy.data.objects.new(name, mesh) 
        bpy.context.scene.collection.objects.link(cube)
        return cube
    

#------------------------ partition polygon list for quicksort ------------------------
# input:   <list of polygon vertex coordinate arrays> [[<vector3 v_0>, <vector3 v_1>, <vector3 v_n>], [...], ...]
#          <vector3 target location>
#          <int index lowest value>
#          <int index hightest value> 
# return:  <int partition index> 
def partition_polygons_by_proximity(polygons, target, low, high):
    # set last element index as pivot
    pivot = polygons[high]
    # calculate distance between center of triangle at pivot index and target vector
    pivot_center = sum([vert for vert in pivot], mathutils.Vector()) / len(pivot)
    distance_pivot_target = (pivot_center - target).length
    
    # pointer for greater element
    i = low - 1
    
    for j in range(low, high):
        poly = polygons[j]
        # calculate distance between center of triangle and target vector, compare to pivot
        poly_center = sum([vert for vert in poly], mathutils.Vector()) / len(poly)
        distance_poly_target = (poly_center - target).length         
        # compare distance    
        if distance_poly_target <= distance_pivot_target:
            i = i + 1
            
            # swap elements
            (polygons[i], polygons[j]) = (polygons[j], polygons[i])
            
    # swap pivot element w/ greater element
    (polygons[i+1], polygons[high]) = (polygons[high], polygons[i+1])
    
    return i+1 

#------------------------ quicksort polygons by their centers' proximity to target vector ------------------------
# input:   <list of polygon vertex coordinate arrays> [[<vector3 v_0>, <vector3 v_1>, <vector3 v_n>], [...], ...]
#          <vector3 target location>
#          <int index lowest value>
#          <int index hightest value>
# return:  <sorted list of polygon vertex coordinate arrays>
def sort_polygons_by_proximity(polygons, target, low, high):
    if low < high:
        partition_index = partition_polygons_by_proximity(polygons, target, low, high)
        sort_polygons_by_proximity(polygons, target, low, partition_index - 1)
        sort_polygons_by_proximity(polygons, target, partition_index + 1, high)
        
    return(polygons)


# ------------------------ calculate face normal from list of coordinates ------------------------
# input: [ [<vector3 vertex_0>, <vector3 vertex_1>, <vector3 vertex_2>], [...] ]
# return: <vector3 face_normal>
def normal_from_vertex_co_list(vertices):
    if len(vertices) > 0:    
        nrm = mathutils.Vector([0,0,0])
        for i in range(len(vertices)):
            vert_0 = mathutils.Vector(vertices[i])
            vert_1 = mathutils.Vector(vertices[(i+1) % len(vertices)])
            nrm += vert_0.cross(vert_1)
        
        return nrm.normalized()        
    else:
        return None


# ------------------------ convert a mesh's triangles to a simplified list coordinates ------------------------
# input: mesh object (object type datablock)
# return: [ [<vector3 vertex_0>, <vector3 vertex_1>, <vector3 vertex_2>], [...] ] 
def get_triangles(mesh_source):
    loop_tris = mesh_source.data.loop_triangles
    triangles = []    
    for key, value in loop_tris.items():
        tri = []
        for vert_index in value.vertices:
            vertex = mesh_source.data.vertices[vert_index]
            tri.append(mesh_source.matrix_world @ vertex.co)
        triangles.append(tri)
    return triangles    


# ------------------------ translate a polygon's vertices along a vector ------------------------
def translate_polygon(object, polygon, vector, axis='XYZ', offset=[0,0,0]):
    # TODO: Complex mesh support
    axis = axis_string_to_index_list(axis)
    
    mesh = polygon.id_data
    verts = mesh.vertices
    try:
        for idx in polygon.vertices:
            vertex = verts[idx]
            obj_scale = object.matrix_world.to_scale()
            for i in range(3):
                if i in axis:
                    vertex.co[i] = vertex.co[i] + vector[i] * 1 / obj_scale[i]# + (-vector[i] / vector[i]) * offset[i]
                    if vector[i] != 0:
                        vertex.co[i] += offset[i] * (vector[i]/abs(vector[i]))
                    
    except ZeroDivisionError as e:
        print("ZeroDivisionError: %s. Scale on %s-axis is 0"%(e, ["X","Y","Z"][i]))


# ------------------------ calculate vectors between source object's face centers and target objects surface ------------------------
# input: source object of mesh type, target object of mesh type
# return: { <int face index> : <vector3 translation> }
def get_snapping_vectors(object, target, threshold, offset=[0,0,0]): 
    # TODO: avoid confusion in variable naming: "object" and "target" are inconsistent
    # TODO: use parent bone as origin of projection
    triangles = []
    if isinstance(target, bpy.types.Object): 
        if target.type == 'MESH':
            triangles = get_triangles(target)
    
    if len(triangles) > 0:
        try:
            sorted_triangles = sort_polygons_by_proximity(triangles, object.matrix_world.to_translation(), 0, len(triangles)-1)
        except RecursionError as e: 
            print("RecursionError: %s"%(e))
            print("Info: Using unsorted target geometry. Object too complex to snap to.")
            sorted_triangles = triangles
            # TODO: exception handling necessary?

        if isinstance(object, bpy.types.Object) and object.type == 'MESH': 
            vectors = {}
            for i in range(len(object.data.polygons)):
                poly = object.data.polygons[i]
                normal_local = poly.normal
                normal_world = (object.matrix_world.to_quaternion() @ normal_local).normalized()
                center_world = object.matrix_world @ poly.center

                for tri in sorted_triangles:
                    intersect = None
                    project_inwards = True
                    target_normal = normal_from_vertex_co_list(tri)
                    # avoid projecting to back faces
                    if normal_world.dot(target_normal) > 0:
                        # try projecting inwards
                        intersect = mathutils.geometry.intersect_ray_tri(tri[0], tri[1], tri[2], -normal_world, center_world, True)
                    if not intersect:
                        # try projecting outwards
                        intersect = mathutils.geometry.intersect_ray_tri(tri[0], tri[1], tri[2], normal_world, center_world, True)
                        if intersect:
                            project_inwards = False  
                        
                    if intersect:
                        # calculate vector between intersection and face center
                        distance = (intersect - center_world).length
                        if threshold > 0 and distance > threshold:
                            # nullify vector if beyond threshold
                            distance = 0

                        if not project_inwards:
                            vector = normal_local * distance
                        else:
                            vector = -normal_local * distance
                        
                        vectors[i] = vector

                        break

            return vectors
        
        else:
            return None
    

# ------------------------ snap a mesh's faces to target mesh surface ------------------------ 
# experimental function, not a fully featured shrinkwrap.
# limitations: 
#   - quad cube source object only.
#   - single target object only
#   - if source and target intersect, two iterations are necessary.
def snap_rigid_body_cube(mesh_source, mesh_target, axis='XYZ', threshold=0.0, offset=[0,0,0]):
    if len(mesh_source.data.vertices) == 8 and len(mesh_source.data.polygons) == 6:
        vectors = get_snapping_vectors(mesh_source, mesh_target, threshold, offset)

        if vectors:
            for key, value in vectors.items():
                vect = vectors[key]
                poly = mesh_source.data.polygons[key]
                translate_polygon(mesh_source, poly, vect, axis, offset)
                origin_to_center(mesh_source)
        else:
            print("Error: Invalid target.")
    else:
        print("Error: Mesh snapping only works on Quad Cubes.")


# ------------------------ reset a bone's rigid body geometry ------------------------ 
def reset_rigid_body_cube(pose_bone):
    rigid_body = pose_bone.data.ragdoll.rigid_body
    rigid_body.data = cube("", 'DATA')


def origin_to_center(mesh_obj):
    center = sum((vert.co for vert in mesh_obj.data.vertices), mathutils.Vector()) / len(mesh_obj.data.vertices)
    translation = mathutils.Matrix.Translation(-center)
    mesh_obj.data.transform(translation)
    for child in mesh_obj.children:
        child.matrix_world @= mesh_obj.matrix_parent_inverse
    mesh_obj.matrix_world.translation = mesh_obj.matrix_world @ center


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
                    # known issue, hacky, gets the job done
                    if fcurve.driver.expression.endswith(" "):
                        fcurve.driver.expression = fcurve.driver.expression[:-1]
                    else:
                        fcurve.driver.expression += " "


######################################################################################
######################################## Misc ########################################
# ------------------------ convert axis described as string to a list of indices ------------------------
# input: string, i.e. 'XYZ' , 'xz'
# return: [0,1,2], [0,2]
def axis_string_to_index_list(axis_string):
    map = {
        'X': 0,
        'Y': 1,
        'Z': 2,
        }
    indices = []
        
    for key, value in map.items():
        if key in axis_string.upper():
            indices.append(value)
            
    return indices    
