import cv2
import os
from src.detector import PoseDetector
from src.converter import MixamoConverter
from src.exporter import BVHExporter
from src.fbx_reader import FBXReader

def test_fbx_reader():
    """FBX読み込みテスト"""
    fbx_path = r"C:\Users\naoki\Downloads\mixamo_character.fbx"
    reader   = FBXReader(fbx_path)

    if reader.load():
        print("\n=== ボーン長さ一覧 ===")
        for name, length in reader.get_all_bone_lengths().items():
            print(f"{name:30s} {length:.4f}")
        reader.unload()
    else:
        print("[ERROR] FBX読み込み失敗")

# mainの最初に追加
if __name__ == "__main__":
    test_fbx_reader()