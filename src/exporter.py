import numpy as np
from datetime import datetime

class BVHExporter:
    """MixamoボーンデータをBVH形式で出力"""

    CONFIDENCE_THRESHOLD = 0.3

    # モーションデータのボーン順序（HIERARCHYと完全一致）
    MOTION_ORDER = [
        "Hips",
        "Spine", "Spine1", "Spine2",
        "Neck", "Head",
        "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",    # ← 追加
        "RightShoulder", "RightArm", "RightForeArm", "RightHand", # ← 追加
        "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
        "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
    ]

    def __init__(self, frame_rate: int = 30):
        self.frame_rate = frame_rate

    def _build_hierarchy_text(self) -> str:
        return """HIERARCHY
    ROOT Hips
    {
    \tOFFSET 0.00 0.00 0.00
    \tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    \tJOINT Spine
    \t{
    \t\tOFFSET 0.00 10.00 0.00
    \t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\tJOINT Spine1
    \t\t{
    \t\t\tOFFSET 0.00 10.00 0.00
    \t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\tJOINT Spine2
    \t\t\t{
    \t\t\t\tOFFSET 0.00 10.00 0.00
    \t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\tJOINT Neck
    \t\t\t\t{
    \t\t\t\t\tOFFSET 0.00 10.00 0.00
    \t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\tJOINT Head
    \t\t\t\t\t{
    \t\t\t\t\t\tOFFSET 0.00 10.00 0.00
    \t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\tEnd Site
    \t\t\t\t\t\t{
    \t\t\t\t\t\t\tOFFSET 0.00 10.00 0.00
    \t\t\t\t\t\t}
    \t\t\t\t\t}
    \t\t\t\t}
    \t\t\t\tJOINT LeftShoulder
    \t\t\t\t{
    \t\t\t\t\tOFFSET 8.86 0.00 0.00
    \t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\tJOINT LeftArm
    \t\t\t\t\t{
    \t\t\t\t\t\tOFFSET 15.00 0.00 0.00
    \t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\tJOINT LeftForeArm
    \t\t\t\t\t\t{
    \t\t\t\t\t\t\tOFFSET 25.00 0.00 0.00
    \t\t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\t\tJOINT LeftHand
    \t\t\t\t\t\t\t{
    \t\t\t\t\t\t\t\tOFFSET 20.00 0.00 0.00
    \t\t\t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\t\t\tEnd Site
    \t\t\t\t\t\t\t\t{
    \t\t\t\t\t\t\t\t\tOFFSET 10.00 0.00 0.00
    \t\t\t\t\t\t\t\t}
    \t\t\t\t\t\t\t}
    \t\t\t\t\t\t}
    \t\t\t\t\t}
    \t\t\t\t}
    \t\t\t\tJOINT RightShoulder
    \t\t\t\t{
    \t\t\t\t\tOFFSET -8.86 0.00 0.00
    \t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\tJOINT RightArm
    \t\t\t\t\t{
    \t\t\t\t\t\tOFFSET -15.00 0.00 0.00
    \t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\tJOINT RightForeArm
    \t\t\t\t\t\t{
    \t\t\t\t\t\t\tOFFSET -25.00 0.00 0.00
    \t\t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\t\tJOINT RightHand
    \t\t\t\t\t\t\t{
    \t\t\t\t\t\t\t\tOFFSET -20.00 0.00 0.00
    \t\t\t\t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\t\t\t\tEnd Site
    \t\t\t\t\t\t\t\t{
    \t\t\t\t\t\t\t\t\tOFFSET -10.00 0.00 0.00
    \t\t\t\t\t\t\t\t}
    \t\t\t\t\t\t\t}
    \t\t\t\t\t\t}
    \t\t\t\t\t}
    \t\t\t\t}
    \t\t\t}
    \t\t}
    \t}
    \tJOINT LeftUpLeg
    \t{
    \t\tOFFSET 8.00 -15.00 0.00
    \t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\tJOINT LeftLeg
    \t\t{
    \t\t\tOFFSET 0.00 -35.00 0.00
    \t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\tJOINT LeftFoot
    \t\t\t{
    \t\t\t\tOFFSET 0.00 -35.00 0.00
    \t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\tJOINT LeftToeBase
    \t\t\t\t{
    \t\t\t\t\tOFFSET 0.00 -5.00 10.00
    \t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\tEnd Site
    \t\t\t\t\t{
    \t\t\t\t\t\tOFFSET 0.00 -5.00 10.00
    \t\t\t\t\t}
    \t\t\t\t}
    \t\t\t}
    \t\t}
    \t}
    \tJOINT RightUpLeg
    \t{
    \t\tOFFSET -8.00 -15.00 0.00
    \t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\tJOINT RightLeg
    \t\t{
    \t\t\tOFFSET 0.00 -35.00 0.00
    \t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\tJOINT RightFoot
    \t\t\t{
    \t\t\t\tOFFSET 0.00 -35.00 0.00
    \t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\tJOINT RightToeBase
    \t\t\t\t{
    \t\t\t\t\tOFFSET 0.00 -5.00 10.00
    \t\t\t\t\tCHANNELS 3 Zrotation Xrotation Yrotation
    \t\t\t\t\tEnd Site
    \t\t\t\t\t{
    \t\t\t\t\t\tOFFSET 0.00 -5.00 10.00
    \t\t\t\t\t}
    \t\t\t\t}
    \t\t\t}
    \t\t}
    \t}
    }"""

    def _build_motion_text(self, frames: list[dict]) -> str:
        """BVHのMOTIONセクションを生成"""
        lines = ["MOTION"]
        lines.append(f"Frames: {len(frames)}")
        lines.append(f"Frame Time: {1.0 / self.frame_rate:.6f}")

        for frame_data in frames:
            values = []
            for bone_name in self.MOTION_ORDER:
                bone       = frame_data.get(bone_name, {})
                rotation   = bone.get("rotation", [0, 0, 0])
                confidence = bone.get("confidence", 0.0)

                if confidence < self.CONFIDENCE_THRESHOLD:
                    rotation = [0, 0, 0]

                if bone_name == "Hips":
                    position = bone.get("position", [0, 0, 0])
                    values.extend([
                        position[0] * 100,
                        position[1] * 100,
                        position[2] * 100,
                        rotation[2],  # Zrotation
                        rotation[0],  # Xrotation
                        rotation[1],  # Yrotation
                    ])
                else:
                    values.extend([
                        rotation[2],  # Zrotation
                        rotation[0],  # Xrotation
                        rotation[1],  # Yrotation
                    ])

            lines.append(" ".join(f"{v:.4f}" for v in values))

        return "\n".join(lines)

    def export(self, bone_data: dict, output_path: str, frames: list[dict] = None):
        if frames is None:
            frames = [bone_data]

        hierarchy_text = self._build_hierarchy_text()
        motion_text    = self._build_motion_text(frames)

        bvh_content = hierarchy_text + "\n" + motion_text

        with open(output_path, "w") as f:
            f.write(bvh_content)

        print(f"[OK] BVHファイルを出力しました: {output_path}")
        print(f"     フレーム数: {len(frames)}")
        print(f"     ボーン数:   {len(self.MOTION_ORDER)}")