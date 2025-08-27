@echo off
echo 画像文字認識・音声読み上げアプリ セットアップ
echo ================================================

echo.
echo 1. Pythonの確認...
python --version
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo https://www.python.org/downloads/ からPython 3.7以上をインストールしてください。
    pause
    exit /b 1
)

echo.
echo 2. 仮想環境の作成...
python -m venv .venv
if errorlevel 1 (
    echo エラー: 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

echo.
echo 3. 仮想環境のアクティベート...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo エラー: 仮想環境のアクティベートに失敗しました。
    pause
    exit /b 1
)

echo.
echo 4. 依存関係のインストール...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

echo.
echo 5. セットアップ完了！
echo.
echo アプリケーションを起動するには:
echo   run.bat を実行するか
echo   python image_to_speech_app.py を実行してください
echo.
pause
