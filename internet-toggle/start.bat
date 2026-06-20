@echo off
chcp 65001 >nul
cd /d "%~dp0"

if "%1"=="--bind" (
    python main.py --bind
    pause
) else if "%1"=="--key" (
    python main.py --key %2
    pause
) else if "%1"=="--detect" (
    python main.py --detect
    pause
) else (
    pythonw main.py
)
