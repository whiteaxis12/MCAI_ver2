"""
BVHの1フレーム目の値を人間が読みやすい形で表示
"""

BONE_ORDER = [
    "Hips",
    "Spine", "Spine1", "Spine2",
    "Neck", "Head",
    "LeftArm", "LeftForeArm", "LeftHand",
    "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
    "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
]

def parse_bvh_frame1(bvh_path: str):
    with open(bvh_path, 'r') as f:
        lines = f.readlines()

    # MOTIONセクションを探す
    motion_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == "MOTION":
            motion_idx = i
            break

    # Frame Time行の次がフレームデータ
    frame_line = lines[motion_idx + 3].strip()
    values = [float(v) for v in frame_line.split()]

    print(f"[INFO] 値の総数: {len(values)}")
    print(f"[INFO] 期待値: {6 + (len(BONE_ORDER)-1)*3} = {6+57}")
    print()

    # Hipsは位置+回転（6値）
    print("=== 1フレーム目のボーンデータ ===")
    idx = 0
    for i, bone in enumerate(BONE_ORDER):
        if bone == "Hips":
            px, py, pz = values[idx], values[idx+1], values[idx+2]
            rz, rx, ry = values[idx+3], values[idx+4], values[idx+5]
            print(f"{bone:20s} pos=({px:7.2f},{py:7.2f},{pz:7.2f}) rot=({rx:7.2f},{ry:7.2f},{rz:7.2f})")
            idx += 6
        else:
            rz, rx, ry = values[idx], values[idx+1], values[idx+2]
            print(f"{bone:20s}                              rot=({rx:7.2f},{ry:7.2f},{rz:7.2f})")
            idx += 3

parse_bvh_frame1("data/outputs/sample_normalized.bvh")