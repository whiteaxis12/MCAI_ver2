"""
debug_fbx_retarget.py
BVHからFBXへの転写をデバッグする
"""
import bpy
import os

MIXAMO_FBX_PATH = "data/outputs/mixamo_character.fbx"
BVH_PATH        = "data/outputs/sample_normalized.bvh"

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_mixamo_fbx(path):
    abs_path = os.path.abspath(path)
    bpy.ops.import_scene.fbx(filepath=abs_path)
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

def import_bvh(path):
    abs_path = os.path.abspath(path)
    bpy.ops.import_anim.bvh(
        filepath=abs_path,
        axis_forward='Z',
        axis_up='Y',
        rotate_mode='NATIVE',
        global_scale=0.01
    )
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

def debug_retarget(mixamo_armature, bvh_armature):
    """フレーム1と30でBVHとMixamoの値を比較"""

    BONE_MAP = {
        "Hips":         "mixamorig:Hips",
        "Spine":        "mixamorig:Spine",
        "Spine1":       "mixamorig:Spine1",
        "Spine2":       "mixamorig:Spine2",
        "Neck":         "mixamorig:Neck",
        "Head":         "mixamorig:Head",
        "LeftArm":      "mixamorig:LeftArm",
        "LeftForeArm":  "mixamorig:LeftForeArm",
        "LeftHand":     "mixamorig:LeftHand",
        "RightArm":     "mixamorig:RightArm",
        "RightForeArm": "mixamorig:RightForeArm",
        "RightHand":    "mixamorig:RightHand",
        "LeftUpLeg":    "mixamorig:LeftUpLeg",
        "LeftLeg":      "mixamorig:LeftLeg",
        "LeftFoot":     "mixamorig:LeftFoot",
        "LeftToeBase":  "mixamorig:LeftToeBase",
        "RightUpLeg":   "mixamorig:RightUpLeg",
        "RightLeg":     "mixamorig:RightLeg",
        "RightFoot":    "mixamorig:RightFoot",
        "RightToeBase": "mixamorig:RightToeBase",
    }

    for frame in [1, 30]:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()

        print(f"\n{'='*60}")
        print(f"フレーム {frame}")
        print(f"{'='*60}")
        print(f"{'ボーン':20s} {'BVH euler':35s} {'Mixamo適用後':35s}")
        print(f"{'-'*90}")

        for bvh_name, mixamo_name in BONE_MAP.items():
            bvh_bone    = bvh_armature.pose.bones.get(bvh_name)
            mixamo_bone = mixamo_armature.pose.bones.get(mixamo_name)

            if bvh_bone is None or mixamo_bone is None:
                print(f"{bvh_name:20s} [ボーンが見つかりません]")
                continue

            # BVHのオイラー角
            bvh_euler = bvh_bone.rotation_euler
            bvh_str   = f"({bvh_euler[0]*57.3:7.2f},{bvh_euler[1]*57.3:7.2f},{bvh_euler[2]*57.3:7.2f})"

            # Mixamoに転写後のオイラー角（転写前の値）
            mixamo_euler = mixamo_bone.rotation_euler
            mix_str      = f"({mixamo_euler[0]*57.3:7.2f},{mixamo_euler[1]*57.3:7.2f},{mixamo_euler[2]*57.3:7.2f})"

            print(f"{bvh_name:20s} BVH={bvh_str} Mixamo={mix_str}")

def main():
    print("="*60)
    print("FBX転写デバッグ開始")
    print("="*60)

    clear_scene()

    mixamo_armature = import_mixamo_fbx(MIXAMO_FBX_PATH)
    if mixamo_armature is None:
        print("[ERROR] Mixamoアーマチュアが見つかりません")
        return

    bvh_armature = import_bvh(BVH_PATH)
    if bvh_armature is None:
        print("[ERROR] BVHアーマチュアが見つかりません")
        return

    print(f"[OK] Mixamo: {mixamo_armature.name}")
    print(f"[OK] BVH:    {bvh_armature.name}")

    debug_retarget(mixamo_armature, bvh_armature)

main()