@echo off
title MEBOT 0.1 - GİZLİ VE ÖZEL LİNK İLE BAŞLATICI
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo   MEBOT 0.1 - EN GUCLU VE ZEKI, ILK YERLI SUPER MODEL
echo   (Gizli Link ve Arama Motoru Koruma Modu)
echo ========================================================
echo.

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python server.py
    pause
    exit /b 0
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py server.py
    pause
    exit /b 0
)

set PYTHON_CMD="C:\Users\acer\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if exist %PYTHON_CMD% (
    %PYTHON_CMD% server.py
    pause
    exit /b 0
)

echo [HATA] Python calistirilamadi! Lutfen Python yuklu oldugundan emin olun.
pause
