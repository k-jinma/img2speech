@echo off
echo 画像文字認識・音声読み上げアプリ 起動中...
echo.

REM 仮想環境のアクティベート
call .venv\Scripts\activate.bat

REM アプリケーションの起動
python image_to_speech_app.py

pause
