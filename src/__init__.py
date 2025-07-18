bl_info = {
    "name": "Ragdoll Kitten",
    "blender": (4, 0, 1),
    "category": "Animation",
    "author": "Oliver Jelko",
    "version": (1, 0, 0),
    "location": "Properties > Physics > Ragdoll Kitten",
    "description": "Adds tools and controls for Rigid Body Simulation of Armature Objects",
    "warning": "",
    "doc_url": ""
}

import bpy

from ragdoll_kitten import ragdoll
from ragdoll_kitten import operators
from ragdoll_kitten import panels
from ragdoll_kitten import menus


def mesh_poll(self, object):
     return object.type == 'MESH'

def register():
    #-------- register custom properties --------
    ragdoll.register()
    operators.register()
    panels.register()
    menus.register()
    #-------- set custom properties --------
    bpy.types.Armature.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollArmature)
    bpy.types.PoseBone.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollBone)
    bpy.types.Object.ragdoll = bpy.props.PointerProperty(type=ragdoll.RagDollObject)
    bpy.types.Scene.ragdolls = bpy.props.CollectionProperty(type=ragdoll.RagDoll)


def unregister():
    #-------- delete custom properties --------
    if hasattr(bpy.types.Armature, 'ragdoll'):
        del bpy.types.Armature.ragdoll

    if hasattr(bpy.types.PoseBone, 'ragdoll'):
        del bpy.types.PoseBone.ragdoll

    if hasattr(bpy.types.Object, 'ragdoll'):
        del bpy.types.Object.ragdoll

    #-------- unregister custom properties --------
    panels.unregister()
    menus.unregister()
    operators.unregister()
    ragdoll.unregister()
    
   
if "bpy" in locals():
    import importlib
    importlib.reload(ragdoll)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(menus)

if __name__ == "__main__":
    register()