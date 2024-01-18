from ragdoll import RagDollBone, RagDoll
from ragdoll_aux import garbage_collect_armatures

def main():
    garbage_collect_armatures()
    rd = RagDoll()
    rd.ctrl_rig_add()
    rd.rb_cubes_add()
    rd.rb_constraints_add()
    rd.rb_connectors_add()
    rd.bone_constraints_add()
    rd.bone_drivers_add()