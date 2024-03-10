import bpy

class RAGDOLL_MT_Main(bpy.types.Menu):
    bl_label = "RagDoll"
    bl_idname = "RAGDOLL_MT_set_constraint_limits"

    def draw(self, context):
        layout = self.layout
        layout.menu("RAGDOLL_MT_constraint_limits")
        layout.menu("RAGDOLL_MT_constraint_type")


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

class RAGDOLL_MT_ConstraintType(bpy.types.Menu):
    bl_label = "Set Constraint Type"
    bl_idname = "RAGDOLL_MT_constraint_type"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("constraint.set_selected", text="Fixed").constraint_type = 'FIXED'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Point").constraint_type = 'POINT'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Hinge").constraint_type = 'HINGE'

        row = layout.row()
        row.operator("constraint.set_selected", text="Slider").constraint_type = 'SLIDER'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Piston").constraint_type = 'PISTON'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Generic").constraint_type = 'GENERIC'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Generic Spring").constraint_type = 'GENERIC_SPRING'
        
        row = layout.row()
        row.operator("constraint.set_selected", text="Motor").constraint_type = 'MOTOR'
        


def draw_menu(self, context):
    self.layout.menu(RAGDOLL_MT_Main.bl_idname)


def register():
    bpy.utils.register_class(RAGDOLL_MT_Main)
    bpy.utils.register_class(RAGDOLL_MT_ConstraintLimits)
    bpy.utils.register_class(RAGDOLL_MT_ConstraintType)
    bpy.types.VIEW3D_MT_pose.append(draw_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(draw_menu)

def unregister():
    bpy.types.VIEW3D_MT_pose.remove(draw_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(draw_menu)
    bpy.utils.unregister_class(RAGDOLL_MT_ConstraintType)
    bpy.utils.unregister_class(RAGDOLL_MT_ConstraintLimits)
    bpy.utils.unregister_class(RAGDOLL_MT_Main)    


if __name__ == "__main__":
    register()