"""
Blenderをバックグラウンドで実行してFBXのボーン長さをJSONで出力
実行方法:
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python blender_fbx_to_bone_lengths.py
"""
import bpy
import json
import sys
import os

# ====================================
FBX_PATH    = r"C:\Users\naoki\Downloads\mixamo_character.fbx"
OUTPUT_JSON = r"C:\Users\naoki\MyProject\SourceCode\repos_vscode\MCAI\data\outputs\bone_lengths.json"
# ====================================

def main():
    # シーンクリア
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # FBXインポート
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)
    print(f"[OK] FBXインポート: {FBX_PATH}")

    # アーマチュアを取得
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

    if armature is None:
        print("[ERROR] アーマチュアが見つかりません")
        return

    print(f"[OK] アーマチュア: {armature.name}")

    # ボーン情報を取得
    bone_data = {}
    for bone in armature.data.bones:
        length   = bone.length
        head_pos = list(armature.matrix_world @ bone.head_local)
        tail_pos = list(armature.matrix_world @ bone.tail_local)

        bone_data[bone.name] = {
            "length":   round(length, 6),
            "head":     [round(v, 6) for v in head_pos],
            "tail":     [round(v, 6) for v in tail_pos],
            "parent":   bone.parent.name if bone.parent else None
        }
        print(f"  {bone.name:30s} length={length:.4f}")

    # JSONで出力
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(bone_data, f, indent=2)

    print(f"\n[OK] ボーン情報をJSONで出力: {OUTPUT_JSON}")

main()