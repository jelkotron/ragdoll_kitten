import bpy

class RAGDOLL_MT_Main(bpy.types.Menu):
    bl_label = "RagDoll"
    bl_idname = "RAGDOLL_MT_set_constraint_limits"

    def draw(self, context):
        layout = self.layout
        layout.menu("RAGDOLL_MT_constraint_limits")

class RAGDOLL_MT_ConstraintLimits(bpy.types.Menu):
    bl_label = "Limit Rotation"
    bl_idname = "RAGDOLL_MT_constraint_limits"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("bone.set_constrotmin", text="X Minimum").axis = 0
        row = layout.row()
        row.operator("bone.set_constrotmin", text="Y Minimum").axis = 1
        row = layout.row()
        row.operator("bone.set_constrotmin", text="Z Minimum").axis = 2

        sep = layout.separator()
        row = layout.row()
        row.operator("bone.set_constrotmax", text="X Maximum").axis = 0
        row = layout.row()
        row.operator("bone.set_constrotmax", text="Y Maximum").axis = 1
        row = layout.row()
        row.operator("bone.set_constrotmax", text="Z Maximum").axis = 2


def draw_menu(self, context):
    self.layout.menu(RAGDOLL_MT_Main.bl_idname)


def register():
    bpy.utils.register_class(RAGDOLL_MT_Main)
    bpy.utils.register_class(RAGDOLL_MT_ConstraintLimits)
    bpy.types.VIEW3D_MT_pose.append(draw_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(draw_menu)

def unregister():
    bpy.types.VIEW3D_MT_pose.remove(draw_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(draw_menu)
    bpy.utils.unregister_class(RAGDOLL_MT_ConstraintLimits)
    bpy.utils.unregister_class(RAGDOLL_MT_Main)    


if __name__ == "__main__":
    register()