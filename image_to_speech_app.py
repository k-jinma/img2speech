import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import easyocr
import pyttsx3
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os
import time

class ImageToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像文字認識・音声読み上げアプリ")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # EasyOCRリーダーの初期化
        self.reader = None
        self.engine = None
        self.current_image = None
        self.recognized_text = ""
        
        # GUIの構築
        self.setup_gui()
        
        # 初期化処理
        self.initialize_components()
    
    def setup_gui(self):
        """GUIの構築"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="画像文字認識・音声読み上げアプリ", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 左側のパネル（画像表示・操作）
        left_panel = ttk.LabelFrame(main_frame, text="画像操作", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 画像表示エリア
        self.image_label = ttk.Label(left_panel, text="画像を選択してください", 
                                    relief="solid", borderwidth=2)
        self.image_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # ボタン
        ttk.Button(left_panel, text="画像を選択", command=self.load_image).grid(row=1, column=0, pady=5)
        ttk.Button(left_panel, text="文字認識実行", command=self.recognize_text).grid(row=1, column=1, pady=5)
        ttk.Button(left_panel, text="前処理画像表示", command=self.show_processed_image).grid(row=2, column=0, pady=5)
        ttk.Button(left_panel, text="元画像で認識", command=self.recognize_original_image).grid(row=2, column=1, pady=5)
        
        # 右側のパネル（テキスト表示・音声操作）
        right_panel = ttk.LabelFrame(main_frame, text="テキスト・音声操作", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 認識されたテキスト表示エリア
        ttk.Label(right_panel, text="認識されたテキスト:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(right_panel, width=50, height=15, wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 音声設定
        voice_frame = ttk.LabelFrame(right_panel, text="音声設定", padding="5")
        voice_frame.grid(row=2, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(voice_frame, text="速度:").grid(row=0, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(voice_frame, from_=0.5, to=2.0, variable=self.speed_var, 
                                   orient=tk.HORIZONTAL, length=150)
        self.speed_scale.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(voice_frame, text="音量:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_scale = ttk.Scale(voice_frame, from_=0.0, to=1.0, variable=self.volume_var, 
                                    orient=tk.HORIZONTAL, length=150)
        self.volume_scale.grid(row=1, column=1, padx=(5, 0), pady=(5, 0))
        
        # 音声操作ボタン
        button_frame = ttk.Frame(right_panel)
        button_frame.grid(row=3, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="音声読み上げ", command=self.speak_text).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="停止", command=self.stop_speech).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="テキストクリア", command=self.clear_text).grid(row=0, column=2, padx=5)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # グリッドの重み設定
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def initialize_components(self):
        """EasyOCRとpyttsx3の初期化"""
        self.status_var.set("EasyOCRを初期化中...")
        self.root.update()
        
        # EasyOCRの初期化（バックグラウンドで実行）
        def init_easyocr():
            try:
                # 日本語認識に特化した設定
                self.reader = easyocr.Reader(
                    ['ja', 'en'], 
                    gpu=False,  # CPU使用で安定性を向上
                    model_storage_directory='./models',  # モデル保存ディレクトリ
                    download_enabled=True,
                    recog_network='japanese_g2'  # 日本語専用モデル
                )
                self.root.after(0, lambda: self.status_var.set("EasyOCR初期化完了"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"EasyOCR初期化エラー: {str(e)}"))
        
        # pyttsx3の初期化
        def init_pyttsx3():
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 1.0)
                self.root.after(0, lambda: self.status_var.set("準備完了"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"音声エンジン初期化エラー: {str(e)}"))
        
        # バックグラウンドで初期化
        threading.Thread(target=init_easyocr, daemon=True).start()
        threading.Thread(target=init_pyttsx3, daemon=True).start()
    
    def load_image(self):
        """画像ファイルを読み込み"""
        file_path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[
                ("画像ファイル", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            try:
                # ファイルパスを正規化
                file_path = os.path.abspath(file_path)
                
                # ファイルの存在確認
                if not os.path.exists(file_path):
                    messagebox.showerror("エラー", f"ファイルが見つかりません: {file_path}")
                    return
                
                # ファイルサイズの確認
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    messagebox.showerror("エラー", "ファイルが空です")
                    return
                
                print(f"画像ファイルを読み込み中: {file_path}")
                print(f"ファイルサイズ: {file_size} bytes")
                
                # 画像を読み込み（OpenCVで試行）
                image = cv2.imread(file_path)
                if image is None:
                    print("OpenCVでの読み込みに失敗。PILで試行します...")
                    # PILで読み込みを試行
                    try:
                        pil_image = Image.open(file_path)
                        # PIL画像をOpenCV形式に変換
                        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                        print("PILでの読み込みに成功しました")
                    except Exception as pil_error:
                        print(f"PILでの読み込みも失敗: {pil_error}")
                        messagebox.showerror("エラー", f"画像の読み込みに失敗しました\nファイルパス: {file_path}\nファイルサイズ: {file_size} bytes\nOpenCVエラー: 読み込み失敗\nPILエラー: {pil_error}")
                        return
                
                # 画像をリサイズ（表示用）
                height, width = image.shape[:2]
                max_size = 400
                if height > max_size or width > max_size:
                    scale = min(max_size / width, max_size / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    image = cv2.resize(image, (new_width, new_height))
                
                # BGRからRGBに変換
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # PIL画像に変換
                pil_image = Image.fromarray(image_rgb)
                photo = ImageTk.PhotoImage(pil_image)
                
                # 画像を表示
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo
                
                # 元の画像を保存（表示用の画像をコピー）
                self.current_image = image.copy()
                
                # 文字認識用の画像を前処理
                self.processed_image = self.preprocess_image_for_ocr(image.copy())
                
                self.status_var.set(f"画像を読み込みました: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("エラー", f"画像の読み込み中にエラーが発生しました: {str(e)}")
    
    def preprocess_image_for_ocr(self, image):
        """OCR用の画像前処理"""
        try:
            # グレースケール変換
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # ノイズ除去
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # コントラスト改善
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # ガウシアンブラーでノイズを軽減
            blurred = cv2.GaussianBlur(enhanced, (1, 1), 0)
            
            # アダプティブ二値化
            binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # モルフォロジー処理でノイズ除去
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 画像を拡大（文字を大きくする）
            height, width = cleaned.shape
            scale_factor = 2
            enlarged = cv2.resize(cleaned, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)
            
            return enlarged
            
        except Exception as e:
            print(f"画像前処理エラー: {e}")
            return image  # 前処理に失敗した場合は元の画像を返す
    
    def show_processed_image(self):
        """前処理された画像を表示"""
        if hasattr(self, 'processed_image') and self.processed_image is not None:
            try:
                # 前処理画像を表示用に変換
                if len(self.processed_image.shape) == 2:  # グレースケール
                    display_image = cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2RGB)
                else:
                    display_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                
                # リサイズ
                height, width = display_image.shape[:2]
                max_size = 400
                if height > max_size or width > max_size:
                    scale = min(max_size / width, max_size / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    display_image = cv2.resize(display_image, (new_width, new_height))
                
                # PIL画像に変換
                pil_image = Image.fromarray(display_image)
                photo = ImageTk.PhotoImage(pil_image)
                
                # 画像を表示
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo
                
                self.status_var.set("前処理画像を表示しました")
                
            except Exception as e:
                messagebox.showerror("エラー", f"前処理画像の表示に失敗しました: {str(e)}")
        else:
            messagebox.showwarning("警告", "前処理画像がありません。先に画像を選択してください。")
    
    def recognize_original_image(self):
        """元の画像で文字認識を実行"""
        if self.current_image is None:
            messagebox.showwarning("警告", "先に画像を選択してください")
            return
        
        if self.reader is None:
            messagebox.showwarning("警告", "EasyOCRの初期化が完了していません")
            return
        
        self.status_var.set("元画像で文字認識中...")
        self.root.update()
        
        def recognize():
            try:
                print("元画像で文字認識を開始します...")
                print(f"画像サイズ: {self.current_image.shape}")
                
                # 元画像で文字認識実行
                results = self.reader.readtext(
                    self.current_image,
                    detail=1
                )
                
                print(f"認識結果数: {len(results)}")
                
                # 結果をテキストに変換
                recognized_text = ""
                total_confidence = 0
                valid_results = 0
                
                for result in results:
                    try:
                        if len(result) == 3:
                            bbox, text, confidence = result
                        elif len(result) == 2:
                            bbox, text = result
                            confidence = 0.5
                        else:
                            continue
                        
                        if confidence > 0.05:  # より低い閾値
                            recognized_text += f"{text} (信頼度: {confidence:.2f})\n"
                            total_confidence += confidence
                            valid_results += 1
                        else:
                            print(f"低信頼度の結果を除外: '{text}' (信頼度: {confidence:.2f})")
                    except Exception as parse_error:
                        print(f"結果の解析エラー: {parse_error}")
                        continue
                
                if valid_results > 0:
                    avg_confidence = total_confidence / valid_results
                    print(f"平均信頼度: {avg_confidence:.2f}")
                
                # GUIを更新
                self.root.after(0, lambda: self.update_recognized_text(recognized_text))
                self.root.after(0, lambda: self.status_var.set(f"元画像認識完了 ({valid_results}個のテキストを検出)"))
                
            except Exception as e:
                error_msg = str(e)
                print(f"元画像文字認識エラー: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("エラー", f"文字認識中にエラーが発生しました: {error_msg}"))
                self.root.after(0, lambda: self.status_var.set("文字認識エラー"))
        
        # バックグラウンドで実行
        threading.Thread(target=recognize, daemon=True).start()
    
    def recognize_text(self):
        """画像から文字を認識"""
        if self.current_image is None:
            messagebox.showwarning("警告", "先に画像を選択してください")
            return
        
        if self.reader is None:
            messagebox.showwarning("警告", "EasyOCRの初期化が完了していません")
            return
        
        self.status_var.set("文字認識中...")
        self.root.update()
        
        def recognize():
            try:
                # 前処理された画像を使用して文字認識実行
                image_to_use = self.processed_image if hasattr(self, 'processed_image') else self.current_image
                
                print("文字認識を開始します...")
                print(f"画像サイズ: {image_to_use.shape}")
                
                # 文字認識実行（シンプルな設定）
                results = self.reader.readtext(
                    image_to_use,
                    detail=1  # 詳細情報を取得
                )
                
                print(f"認識結果数: {len(results)}")
                
                # 結果をテキストに変換（信頼度も表示）
                recognized_text = ""
                total_confidence = 0
                valid_results = 0
                
                print(f"結果の形式: {type(results)}")
                print(f"最初の結果: {results[0] if results else 'None'}")
                
                for result in results:
                    try:
                        if len(result) == 3:
                            bbox, text, confidence = result
                        elif len(result) == 2:
                            bbox, text = result
                            confidence = 0.5  # デフォルト信頼度
                        else:
                            print(f"予期しない結果形式: {result}")
                            continue
                        
                        if confidence > 0.1:  # 信頼度が10%以上の結果を使用
                            recognized_text += f"{text} (信頼度: {confidence:.2f})\n"
                            total_confidence += confidence
                            valid_results += 1
                        else:
                            print(f"低信頼度の結果を除外: '{text}' (信頼度: {confidence:.2f})")
                    except Exception as parse_error:
                        print(f"結果の解析エラー: {parse_error}, 結果: {result}")
                        continue
                
                if valid_results > 0:
                    avg_confidence = total_confidence / valid_results
                    print(f"平均信頼度: {avg_confidence:.2f}")
                
                # GUIを更新
                self.root.after(0, lambda: self.update_recognized_text(recognized_text))
                self.root.after(0, lambda: self.status_var.set(f"文字認識完了 ({valid_results}個のテキストを検出、平均信頼度: {avg_confidence:.2f})"))
                
            except Exception as e:
                error_msg = str(e)
                print(f"文字認識エラー: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("エラー", f"文字認識中にエラーが発生しました: {error_msg}"))
                self.root.after(0, lambda: self.status_var.set("文字認識エラー"))
        
        # バックグラウンドで実行
        threading.Thread(target=recognize, daemon=True).start()
    
    def update_recognized_text(self, text):
        """認識されたテキストを更新"""
        self.recognized_text = text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text)
    
    def speak_text(self):
        """テキストを音声で読み上げ"""
        if not self.recognized_text.strip():
            messagebox.showwarning("警告", "読み上げるテキストがありません")
            return
        
        if self.engine is None:
            messagebox.showwarning("警告", "音声エンジンが初期化されていません")
            return
        
        def speak():
            try:
                # 音声設定を適用
                self.engine.setProperty('rate', int(150 * self.speed_var.get()))
                self.engine.setProperty('volume', self.volume_var.get())
                
                # テキストを読み上げ
                self.engine.say(self.recognized_text)
                self.engine.runAndWait()
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("エラー", f"音声読み上げ中にエラーが発生しました: {error_msg}"))
        
        # バックグラウンドで実行
        threading.Thread(target=speak, daemon=True).start()
        self.status_var.set("音声読み上げ中...")
    
    def stop_speech(self):
        """音声読み上げを停止"""
        if self.engine:
            self.engine.stop()
        self.status_var.set("音声読み上げを停止しました")
    
    def clear_text(self):
        """テキストエリアをクリア"""
        self.text_area.delete(1.0, tk.END)
        self.recognized_text = ""
        self.status_var.set("テキストをクリアしました")

def main():
    root = tk.Tk()
    app = ImageToSpeechApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 