# MCAI

※自作AIです。完成まではpythonで作成、スピードを要するならC++に順次移行
- マーカーレスモーションキャプチャーのAIを作成



## 目次

- [DevelopmentEnviroment](#developmentenviroment)
- [Directory](#Directory)


--------





















# DevelopmentEnviroment

- conda 環境python3.11

```cpp
// nvidia-smiにてcuda versionを確認。GPUに合わせたpytorchをinstall
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

pip install mediapipe opencv-python open3d
```

---

















# Directory

- ざっくりこんな感じで作っていく

```

│
├── 📁 data/                    # 入力データ
│   ├── images/                 # 入力画像
│   ├── videos/                 # 入力動画
│   └── outputs/                # 出力結果
│       ├── landmarks/          # 3D頂点データ（JSON/CSV）
│       └── visualizations/     # 可視化画像・動画
│
├── 📁 models/                  # 学習済みモデルの重み
│   └── .gitkeep
│
├── 📁 src/
│   ├── detector.py       # MediaPipeで3D骨格取得
│   ├── converter.py      # 骨格データ → BVH変換
    ├── visualizer.py     # 確認用可視化
    └── exporter.py       # BVH/FBXファイル出力
│
├── 📁 notebooks/               # Jupyter Notebook（実験・検証用）
│   └── 01_prototype.ipynb
│
├── 📁 tests/                   # テストコード
│   └── test_detector.py
│
├── 📁 config/                  # 設定ファイル
│   └── settings.yaml           # パラメータ設定
│
├── main.py                     # エントリーポイント
├── requirements.txt            # pip用ライブラリリスト
├── environment.yml             # conda環境ファイル
└── README.md                   # プロジェクト説明
```
