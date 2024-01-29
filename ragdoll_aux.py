import bpy
import json
import os

def load_text(context, filepath):
    text = bpy.data.texts.load(filepath)
    if validate_selection(bpy.context.active_object, 'ARMATURE'):
        context.active_object.data.ragdoll.config = text
        if context.active_object.data.ragdoll.type == 'DEFORM':
            control_rig = context.active_object.data.ragdoll.control_rig 
            if control_rig:
                control_rig.data.ragdoll.config = text

        
def deselect_all():
    objs = []
    for obj in bpy.context.selected_objects:
        objs.append(obj)
    for obj in objs:
        obj.select_set(False)


def get_bone_children(armature):
    bones = {}
    for bone in armature.pose.bones:
        if bone.children:
            bones[bone.name] = [child.name for child in bone.children]
    return bones


#-------- validate object type --------
def validate_selection(selected_object, mode = 'ARMATURE'):
    if selected_object.type == mode:
        return selected_object
    else:
        return None

#-------- exclude unselected/hidden pose bones and hidden bone collections --------
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

#-------- read config for rigid body constraint limits --------
def config_load(filepath):
    data = None
    filepath = bpy.path.abspath(filepath)
    if filepath:
        with open(filepath, 'r') as file:
            data = json.load(file)
            # file.close()
        print("Info: config loaded.")
    else:
        data = {}

    return data

#-------- add or set rigid body constraint collection --------
def rb_constraint_collection_set(collection_name = 'RigidBodyConstraints'):
    if collection_name not in bpy.data.collections:
        bpy.data.collections.new(collection_name)

    bpy.context.scene.rigidbody_world.constraints = bpy.data.collections[collection_name]
    
        
#-------- create collection and/or add add objects --------
def collection_objects_add(collection_name, objects=[]):
    col = None
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


def collection_objects_remove(collection, objects=[]):
    for obj in objects:
        if obj.name in collection.objects:
            collection.objects.unlink(obj)



#-------- add a cube --------
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


#-------- remove armatures w/o users --------
def garbage_collect_armatures():
    for arm in bpy.data.armatures:
        if arm.users == 0:
            bpy.data.armatures.remove(arm, do_unlink=True)