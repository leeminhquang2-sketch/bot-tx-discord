@echo off
title Game MQ System
color 0A

echo ============================================================
echo    🚀 GAME MQ SYSTEM - KHỞI ĐỘNG
echo ============================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long tai Python tu https://python.org
    pause
    exit /b
)

REM Cài đặt requirements
echo [1/2] Dang cai dat requirements...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Co loi khi cai dat requirements, thu lai...
    pip install discord.py Flask flask-cors flask-session cryptography
)

echo.
echo [2/2] Dang khoi dong he thong...
echo.
python run.py

pause
