# ocr_from_path.py の使い方（macOS・仮想環境）

このドキュメントは、単体スクリプト `ocr_from_path.py` を macOS で実行するための手順をまとめたものです。プロジェクト全体ではなく、この1ファイルを動かすことにフォーカスしています。

- 対象: `ocr_from_path.py`
- 画像の指定方法: スクリプト内の定数 `IMAGE_PATH` にファイルパスを記載（コマンド引数は不要）
- 前提: 初回のみOCRモデルの自動ダウンロードが行われるため、インターネット接続が必要です

> メモ: 以下のコマンドは zsh での実行を想定しています（macOSの標準）。

---

## 1. Python のバージョン確認

```bash
python3 --version
which python3
```

- 目安: Python 3.9〜3.12（本スクリプトは 3.9 で検証）
- 複数の Python が入っている場合、以降は同じ `python3` を使ってください。

---

## 2. 作業ディレクトリへ移動

```bash
cd "/Users/jinmakazuhiro/Gitリポジトリ/img2speech"
```

> 直接 `ocr_from_path.py` が置いてあるフォルダに移動してください。

---

## 3. 仮想環境の作成と有効化

```bash
python3 -m venv .venv
source .venv/bin/activate
python -V   # 仮想環境のPythonであることを確認
python -m pip install --upgrade pip setuptools wheel
```

- 有効化に成功すると、プロンプトに `(.venv)` が表示されます。
- 終了するときは `deactivate` で無効化できます。

---

## 4. 依存ライブラリのインストール

`ocr_from_path.py` の実行に最低限必要なライブラリをインストールします。

- リポジトリに `requirements.txt` がある場合（推奨）

```bash
pip install -r requirements.txt
```

- 単体で最低限のパッケージを入れたい場合（固定バージョン例）

```bash
pip install easyocr==1.7.2 opencv-python==4.12.0.88 Pillow==11.3.0 numpy==2.0.2
```

インストール確認（任意）:
```bash
python -c 'import cv2, easyocr, numpy; print("cv2:", cv2.__version__, "easyocr:", easyocr.__version__, "numpy:", numpy.__version__)'
```

---

## 5. 画像パス（IMAGE_PATH）の設定

`ocr_from_path.py` を開き、先頭付近の定数 `IMAGE_PATH` を実際の画像ファイルに合わせて編集します。

例（同じフォルダに `img1.png` を置く場合は既定のままでOK）:
```python
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "img1.png")
```

例（絶対パスを使う場合）:
```python
IMAGE_PATH = "/Users/あなたの名前/Pictures/sample.png"
```

> macOS では見た目が同じでも文字が微妙に異なる（濁点の合成文字など）ケースがあります。パスはタブ補完やドラッグ＆ドロップで入力すると安全です。

---

## 6. 実行

```bash
python ocr_from_path.py
```

- 認識できた文字列が1行ずつ表示されます。
- 何も検出されなかった場合は「（文字が見つかりませんでした）」と表示されます。

補足（仮想環境のPythonを明示的に使う場合）:
```bash
./.venv/bin/python ocr_from_path.py
```

---

## 7. よくあるトラブルと対処

- 「No module named 'cv2'」が出る
  - 仮想環境が有効になっていない可能性があります。`source .venv/bin/activate` を実行してから `pip install ...` と `python ocr_from_path.py` を再実行してください。

- 画像が読めない/パスが合っているのに見つからない
  - パスの文字（濁点付きの文字合成など）が異なることがあります。`ls` で確認し、タブ補完で正しいパスを入力してください。
  - 透過PNGや非対応形式で問題がある場合は、JPEG/PNG など別形式で再保存して試してください。

- 初回実行が遅い
  - OCRモデル（日本語モデルなど）を `./models` にダウンロードしています。2回目以降は速くなります。

---

## 8. 補足（スクリプトのカスタマイズ）

`ocr_from_path.py` には以下の簡単な設定があります。

- `IMAGE_PATH`: 読み取る画像ファイルのパス
- `LANGS`: 認識言語（例: `["ja", "en"]`）
- `RECOG_NETWORK`: 日本語向けモデル（例: `"japanese_g2"`）
- `USE_PREPROCESS`: 前処理のON/OFF
- `RESIZE_SCALE`: 拡大倍率
- `USE_THRESHOLD`: 二値化のON/OFF（薄い文字に有効なことがあります）

詳しくはソース内のコメントをご覧ください。

---

## 9. 実行のショートカット（任意）

zsh のエイリアスを使うと、仮想環境有効化から実行まで一気に行うこともできます。

```bash
alias runocr='cd "/Users/jinmakazuhiro/Gitリポジトリ/img2speech" && source .venv/bin/activate && python ocr_from_path.py'
runocr
```

---

以上で `ocr_from_path.py` を macOS で実行する準備と実行方法は完了です。
