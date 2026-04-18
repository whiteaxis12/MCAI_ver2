import pyassimp
import numpy as np

class FBXReader:
    """MixamoのFBXからボーン情報を読み込む"""

    def __init__(self, fbx_path: str):
        self.fbx_path = fbx_path
        self.bone_lengths = {}
        self.bone_positions = {}

    def load(self) -> bool:
        """FBXを読み込んでボーン情報を取得"""
        try:
            with pyassimp.load(self.fbx_path) as scene:
                print(f"[OK] FBXを読み込みました: {self.fbx_path}")
                print(f"[INFO] ルートノード: {scene.rootnode.name}")

                # 全ノードを表示してから解析
                self._print_hierarchy(scene.rootnode)
                self._extract_bones(scene.rootnode, np.zeros(3))
            return True
        except Exception as e:
            print(f"[ERROR] FBX読み込み失敗: {e}")
            return False

    def _print_hierarchy(self, node, depth: int = 0):
        """ノード階層を表示（デバッグ用）"""
        indent = "  " * depth
        print(f"{indent}[Node] {node.name}")
        for child in node.children:
            self._print_hierarchy(child, depth + 1)

    def _extract_bones(self, node, parent_pos: np.ndarray, depth: int = 0):
        """再帰的にボーン情報を取得"""
        transform = np.array(node.transformation).reshape(4, 4).T
        pos = transform[:3, 3]

        bone_name = node.name.strip()

        if bone_name:
            self.bone_positions[bone_name] = pos
            length = np.linalg.norm(pos - parent_pos)
            self.bone_lengths[bone_name] = length

        for child in node.children:
            self._extract_bones(child, pos, depth + 1)

    def get_bone_length(self, bone_name: str) -> float:
        return self.bone_lengths.get(bone_name, 1.0)

    def get_all_bone_lengths(self) -> dict:
        return self.bone_lengths