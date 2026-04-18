"""
blender_bvh_to_fbx.py
====================================
BVHをFBXに変換してUE5用に出力
実行方法:
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python blender_bvh_to_fbx.py
====================================
"""

import bpy
import os

# ====================================
# 設定欄 ← ここを編集してください
# ====================================
MIXAMO_FBX_PATH = "data/outputs/mixamo_character.fbx"
BVH_PATH        = "data/outputs/sample_normalized.bvh"
OUTPUT_FBX_PATH = "data/outputs/animation_output.fbx"
# ====================================

def clear_scene():
    """シーンをクリア"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("[OK] シーンをクリア")

def import_mixamo_fbx(path: str):
    """MixamoキャラクターFBXをインポート"""
    abs_path = os.path.abspath(path)
    bpy.ops.import_scene.fbx(filepath=abs_path)
    print(f"[OK] Mixamo FBXインポート: {abs_path}")

    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

    if armature is None:
        print("[ERROR] アーマチュアが見つかりません")
        return None

    print("[INFO] Mixamoボーン一覧:")
    for bone in armature.data.bones:
        print(f"  {bone.name}")

    return armature

def import_bvh(path: str):
    """BVHをインポート"""
    abs_path = os.path.abspath(path)
    bpy.ops.import_anim.bvh(
        filepath=abs_path,
        axis_forward='-Z',
        axis_up='Y',
        rotate_mode='NATIVE',
        global_scale=0.01  # cm→m変換
    )
    print(f"[OK] BVHインポート: {abs_path}")

    bvh_armature = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            bvh_armature = obj
            break

    if bvh_armature is None:
        print("[ERROR] BVHアーマチュアが見つかりません")
        return None

    print(f"[OK] BVHアーマチュア: {bvh_armature.name}")
    print("[INFO] BVHボーン一覧:")
    for bone in bvh_armature.data.bones:
        print(f"  {bone.name}")

    return bvh_armature

def get_frame_range(bvh_armature):
    """BVHのフレーム範囲を取得"""
    if bvh_armature.animation_data is None:
        return 1, 1
    action = bvh_armature.animation_data.action
    if action is None:
        return 1, 1
    frame_start = int(action.frame_range[0])
    frame_end   = int(action.frame_range[1])
    print(f"[OK] フレーム範囲: {frame_start} - {frame_end}")
    return frame_start, frame_end

def retarget_animation(mixamo_armature, bvh_armature, frame_start: int, frame_end: int):
    """BVHのアニメーションをMixamoリグに転写"""

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

    print(f"\n[INFO] アニメーション転写開始: {frame_end - frame_start + 1}フレーム")

    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)

        for bvh_bone_name, mixamo_bone_name in BONE_MAP.items():
            bvh_bone    = bvh_armature.pose.bones.get(bvh_bone_name)
            mixamo_bone = mixamo_armature.pose.bones.get(mixamo_bone_name)

            if bvh_bone is None or mixamo_bone is None:
                continue

            mixamo_bone.rotation_mode       = 'QUATERNION'
            mixamo_bone.rotation_quaternion = bvh_bone.rotation_quaternion.copy()

            # Hipsは位置も転写
            if bvh_bone_name == "Hips":
                mixamo_bone.location = bvh_bone.location.copy()
                mixamo_bone.keyframe_insert(data_path="location", frame=frame)

            mixamo_bone.keyframe_insert(
                data_path="rotation_quaternion",
                frame=frame
            )

        if frame % 30 == 0:
            print(f"\r転写中: {frame}/{frame_end}", end="")

    print(f"\n[OK] アニメーション転写完了")

def remove_bvh_armature(bvh_armature):
    """BVHアーマチュアを削除"""
    bpy.ops.object.select_all(action='DESELECT')
    bvh_armature.select_set(True)

    # BVHに関連するメッシュも削除
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.parent == bvh_armature:
            obj.select_set(True)

    bpy.ops.object.delete()
    print("[OK] BVHアーマチュアを削除")

def export_fbx(output_path: str):
    """アニメーションつきFBXを出力"""
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # Mixamoアーマチュアと関連メッシュのみ選択
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type in ('ARMATURE', 'MESH'):
            obj.select_set(True)

    bpy.ops.export_scene.fbx(
        filepath=abs_path,
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
    print(f"[OK] FBX出力: {abs_path}")

def main():
    print("=" * 50)
    print("BVH → FBX変換開始")
    print("=" * 50)

    clear_scene()

    mixamo_armature = import_mixamo_fbx(MIXAMO_FBX_PATH)
    if mixamo_armature is None:
        return

    bvh_armature = import_bvh(BVH_PATH)
    if bvh_armature is None:
        return

    frame_start, frame_end = get_frame_range(bvh_armature)

    retarget_animation(mixamo_armature, bvh_armature, frame_start, frame_end)

    # BVHアーマチュアを削除してからFBX出力
    remove_bvh_armature(bvh_armature)

    export_fbx(OUTPUT_FBX_PATH)

    print("\n" + "=" * 50)
    print(f"完了！ → {OUTPUT_FBX_PATH}")
    print("=" * 50)

main()