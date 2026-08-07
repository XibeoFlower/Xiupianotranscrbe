@echo off
chcp 65001 >nul
title Piano Transcriber - Cai dat va Khoi chay
echo ============================================
echo   PIANO TRANSCRIBER (Transkun) - Setup
echo ============================================
echo.

REM --- Kiem tra Python co san hay chua ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python.
    echo Vui long cai Python tai https://www.python.org/downloads/
    echo Nho tick "Add python.exe to PATH" khi cai.
    pause
    exit /b 1
)
echo [OK] Da tim thay Python.

REM --- Kiem tra FFmpeg co san hay chua ---
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] Khong tim thay FFmpeg trong PATH.
    echo App van chay duoc nhung se loi khi doc file mp3/wav neu chua cai FFmpeg.
    echo Xem huong dan cai FFmpeg trong file huong-dan-app-transkun.md muc 3.
    echo.
)

REM --- Tao moi truong ao neu chua co ---
if not exist "venv" (
    echo Dang tao moi truong ao...
    python -m venv venv
)

REM --- Kich hoat moi truong ao ---
call venv\Scripts\activate.bat

REM --- Cai dat cac thu vien can thiet ---
echo.
echo Dang kiem tra va cai dat thu vien can thiet...
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo Dang cai PyTorch ^(ban CPU^)...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
)

if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install transkun psutil
)

REM --- Chay app ---
echo.
echo ============================================
echo   Dang khoi chay ung dung...
echo ============================================
python app.py

echo.
echo Ung dung da dong. Nhan phim bat ky de thoat cua so nay.
pause >nul
