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

def retarget_animation(mixamo_armature, bvh_armature, frame_start, frame_end):
    import mathutils

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

    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end   = frame_end

    if mixamo_armature.animation_data is None:
        mixamo_armature.animation_data_create()
    new_action = bpy.data.actions.new(name="RetargetedAnimation")
    mixamo_armature.animation_data.action = new_action

    # デバッグ：フレーム1の転写前後を確認
    bpy.context.scene.frame_set(frame_start)
    bpy.context.view_layer.update()

    print("\n=== フレーム1 転写前後の確認 ===")
    for bvh_name, mixamo_name in list(BONE_MAP.items())[:5]:
        bvh_bone    = bvh_armature.pose.bones.get(bvh_name)
        mixamo_bone = mixamo_armature.pose.bones.get(mixamo_name)

        if bvh_bone is None:
            print(f"[ERROR] BVHボーンなし: {bvh_name}")
            continue
        if mixamo_bone is None:
            print(f"[ERROR] Mixamoボーンなし: {mixamo_name}")
            continue

        print(f"\n{bvh_name}:")
        print(f"  BVH rotation_mode:  {bvh_bone.rotation_mode}")
        print(f"  BVH rotation_euler: {[round(v*57.3,2) for v in bvh_bone.rotation_euler]}")

        euler = bvh_bone.rotation_euler.copy()
        quat  = mathutils.Euler(euler, bvh_bone.rotation_mode).to_quaternion()

        mixamo_bone.rotation_mode       = 'QUATERNION'
        mixamo_bone.rotation_quaternion = quat
        mixamo_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_start)

        print(f"  転写後 Mixamo quat: {[round(v,3) for v in mixamo_bone.rotation_quaternion]}")

    # 全フレーム転写
    print(f"\n[INFO] 全フレーム転写開始: {frame_end - frame_start + 1}フレーム")
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()

        for bvh_name, mixamo_name in BONE_MAP.items():
            bvh_bone    = bvh_armature.pose.bones.get(bvh_name)
            mixamo_bone = mixamo_armature.pose.bones.get(mixamo_name)

            if bvh_bone is None or mixamo_bone is None:
                continue

            euler = bvh_bone.rotation_euler.copy()
            quat  = mathutils.Euler(euler, bvh_bone.rotation_mode).to_quaternion()

            mixamo_bone.rotation_mode       = 'QUATERNION'
            mixamo_bone.rotation_quaternion = quat
            mixamo_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

            if bvh_name == "Hips":
                mixamo_bone.location = bvh_bone.location.copy()
                mixamo_bone.keyframe_insert(data_path="location", frame=frame)

        if frame % 30 == 0:
            print(f"\r転写中: {frame}/{frame_end}", end="")

    print(f"\n[OK] アニメーション転写完了")

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

    # フレーム範囲取得
    action      = bvh_armature.animation_data.action
    frame_start = int(action.frame_range[0])
    frame_end   = int(action.frame_range[1])
    print(f"[OK] フレーム範囲: {frame_start} - {frame_end}")

    retarget_animation(mixamo_armature, bvh_armature, frame_start, frame_end)

    # FBX出力
    output_path = os.path.abspath("data/outputs/debug_output.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type in ('ARMATURE', 'MESH'):
            obj.select_set(True)

    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=True,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        add_leaf_bones=False,
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"[OK] デバッグFBX出力: {output_path}")

main()