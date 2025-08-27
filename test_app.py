#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像文字認識・音声読み上げアプリのテストスクリプト
"""

import sys
import os

def test_imports():
    """必要なライブラリのインポートテスト"""
    print("ライブラリのインポートテストを開始...")
    
    try:
        import easyocr
        print("✓ EasyOCR インポート成功")
    except ImportError as e:
        print(f"✗ EasyOCR インポート失敗: {e}")
        return False
    
    try:
        import pyttsx3
        print("✓ pyttsx3 インポート成功")
    except ImportError as e:
        print(f"✗ pyttsx3 インポート失敗: {e}")
        return False
    
    try:
        import cv2
        print("✓ OpenCV インポート成功")
    except ImportError as e:
        print(f"✗ OpenCV インポート失敗: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow インポート成功")
    except ImportError as e:
        print(f"✗ PIL/Pillow インポート失敗: {e}")
        return False
    
    try:
        import tkinter as tk
        print("✓ tkinter インポート成功")
    except ImportError as e:
        print(f"✗ tkinter インポート失敗: {e}")
        return False
    
    return True

def test_easyocr():
    """EasyOCRの基本機能テスト"""
    print("\nEasyOCR機能テストを開始...")
    
    try:
        import easyocr
        reader = easyocr.Reader(['ja', 'en'])
        print("✓ EasyOCR初期化成功")
        return True
    except Exception as e:
        print(f"✗ EasyOCR初期化失敗: {e}")
        return False

def test_pyttsx3():
    """pyttsx3の基本機能テスト"""
    print("\npyttsx3機能テストを開始...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✓ pyttsx3初期化成功")
        
        # 音声プロパティの設定テスト
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.5)
        print("✓ 音声プロパティ設定成功")
        
        return True
    except Exception as e:
        print(f"✗ pyttsx3初期化失敗: {e}")
        return False

def test_gui():
    """GUIの基本機能テスト"""
    print("\nGUI機能テストを開始...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # テスト用ウィンドウを作成
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示
        
        # 基本的なウィジェットのテスト
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="テスト")
        button = ttk.Button(frame, text="テスト")
        
        print("✓ GUIウィジェット作成成功")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ GUI機能テスト失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("画像文字認識・音声読み上げアプリ テスト開始")
    print("=" * 50)
    
    # 各テストを実行
    tests = [
        ("ライブラリインポート", test_imports),
        ("EasyOCR機能", test_easyocr),
        ("pyttsx3機能", test_pyttsx3),
        ("GUI機能", test_gui)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}テスト:")
        result = test_func()
        results.append((test_name, result))
    
    # 結果の表示
    print("\n" + "=" * 50)
    print("テスト結果:")
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 すべてのテストが成功しました！")
        print("アプリケーションを実行できます: python image_to_speech_app.py")
    else:
        print("❌ 一部のテストが失敗しました。")
        print("依存関係のインストールを確認してください: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 