"""
シンプルなOCRプログラム（中学生向け）
- 画像のパスなどを下の定数で設定します（引数は不要）
- 最小限の前処理で、読み取ったテキストを表示します
- 必要に応じて設定を少し変えられるようにしています
"""

import os
import sys
from typing import List, Tuple, Optional

import cv2
import easyocr
import numpy as np


# === 1) 基本設定（ここを変更して使います） ===
# 読み取る画像（相対パスでも絶対パスでもOK）
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "img1.png")

# 認識する言語（日本語＋英語）
LANGS: List[str] = ["ja", "en"]

# 日本語向けモデル（通常は "japanese_g2"）
RECOG_NETWORK = "japanese_g2"

# モデル保存先（初回ダウンロード時にここへ保存）
MODEL_DIR = "./models"

# GPUを使うか（CPUで十分なら False のままでOK）
USE_GPU = False


# === 2) 前処理の設定（読みやすくするための軽い加工） ===
# 前処理を使うか
USE_PREPROCESS = True

# 画像をどれくらい大きくするか（2.0 なら縦横2倍）
RESIZE_SCALE = 2.0

# ぼかしのカーネルサイズ（奇数推奨: 3, 5 など）
BLUR_KERNEL = 3

# 二値化（白黒はっきりさせる）を使うか
USE_THRESHOLD = False
# "otsu" か "adaptive" を選択（USE_THRESHOLD が True のときのみ使用）
THRESH_METHOD = "otsu"  # or "adaptive"


# === 3) 読み取り範囲（全部読むなら None のままでOK） ===
# ROI = (x, y, w, h) 形式で指定。例: ROI = (100, 50, 400, 200)
ROI: Optional[Tuple[int, int, int, int]] = None


# === 4) 出力の設定 ===
# DETAIL=0: 文字だけの結果 / DETAIL=1: 座標や信頼度も（内部で使う）
DETAIL = 0
# 信頼度の下限（DETAIL=1 のときに使います）
MIN_CONFIDENCE = 0.0
# すべての行を1行にまとめて表示するか
JOIN_LINES = False

# デバッグ用：前処理画像をファイル保存するか
DEBUG_SAVE = False
DEBUG_SAVE_PATH = os.path.join(os.path.dirname(__file__), "preprocessed.png")


def ensure_odd(n: int) -> int:
    """カーネルサイズが偶数だとエラーになるため、奇数に直します。"""
    return n if n % 2 == 1 else n + 1


def load_image(path: str) -> np.ndarray:
    """画像を読み込みます（失敗したらわかりやすいメッセージを出します）。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")

    image = cv2.imread(path)  # OpenCVはPNG/JPG/BMP/TIFFなどに対応
    if image is None:
        raise ValueError("画像の読み込みに失敗しました。形式や破損を確認してください。")
    return image


def apply_roi(image: np.ndarray) -> np.ndarray:
    """ROI（読み取り範囲）が指定されていれば、その部分だけ切り出します。"""
    if ROI is None:
        return image
    x, y, w, h = ROI
    h_img, w_img = image.shape[:2]
    # 画像範囲に収まるようにガード
    x2 = min(x + w, w_img)
    y2 = min(y + h, h_img)
    x = max(0, x)
    y = max(0, y)
    if x >= x2 or y >= y2:
        raise ValueError("ROIの指定が不正です（画像範囲外）。")
    return image[y:y2, x:x2]


def simple_preprocess(image: np.ndarray) -> np.ndarray:
    """OCRが読みやすくなるように、簡単な前処理をします。
    1) グレースケール
    2) 少しぼかす（ノイズを減らす）
    3) 拡大（小さい文字を読みやすく）
    4) 必要なら二値化（白黒はっきり）
    """
    # グレースケール
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ぼかし（カーネルは奇数に）
    k = ensure_odd(int(BLUR_KERNEL))
    if k > 1:
        gray = cv2.GaussianBlur(gray, (k, k), 0)

    # 拡大
    if RESIZE_SCALE and RESIZE_SCALE > 0 and RESIZE_SCALE != 1.0:
        h, w = gray.shape[:2]
        new_w = max(1, int(w * RESIZE_SCALE))
        new_h = max(1, int(h * RESIZE_SCALE))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # 二値化（必要なときだけ）
    if USE_THRESHOLD:
        if THRESH_METHOD == "adaptive":
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
            )
        else:
            # デフォルトは大津の二値化
            _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if DEBUG_SAVE:
        cv2.imwrite(DEBUG_SAVE_PATH, gray)

    return gray


def run_ocr(image: np.ndarray) -> List[str]:
    """EasyOCRで文字を読み取って、文字列のリストを返します。"""
    reader = easyocr.Reader(
        LANGS,
        gpu=USE_GPU,
        model_storage_directory=MODEL_DIR,
        download_enabled=True,
        recog_network=RECOG_NETWORK,
    )

    # DETAILに応じて読み方を切り替え
    if DETAIL == 0:
        # 文字だけほしいとき（シンプル）
        results = reader.readtext(image, detail=0)  # ← detail は 0 か 1
        lines = [t.strip() for t in results if isinstance(t, str) and t.strip()]
        return lines
    else:
        # 座標や信頼度も返る
        results = reader.readtext(image, detail=1)
        lines: List[str] = []
        for bbox, text, conf in results:
            if not isinstance(text, str):
                continue
            text = text.strip()
            if not text:
                continue
            if conf is not None and conf < float(MIN_CONFIDENCE):
                continue
            lines.append(text)
        return lines


def main() -> int:
    try:
        # 画像の読み込み
        image = load_image(IMAGE_PATH)

        # 読み取り範囲が設定されていれば切り出し
        image = apply_roi(image)

        # 前処理（ON/OFF可能）
        if USE_PREPROCESS:
            image = simple_preprocess(image)

        # OCR実行
        lines = run_ocr(image)

        # 表示（1行ずつ、またはまとめて）
        if lines:
            if JOIN_LINES:
                print(" ".join(lines))
            else:
                print("\n".join(lines))
        else:
            print("（文字が見つかりませんでした）")

        return 0
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
