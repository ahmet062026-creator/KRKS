@echo off
title MEBOT 0.1 - SADE
color 0B
echo ==================================================
echo   MEBOT 0.1 - EN GUCLU VE ZEKI, ILK YERLI SUPER MODEL
echo ==================================================
echo Yerel sunucu baslatiliyor... (Lutfen bu pencereyi kapatmayin)

:: Sunucuyu baslat ve tarayiciyi ac
start http://127.0.0.1:8080/
set PORT=8080

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

echo [HATA] Python bulunamadi!
pause
