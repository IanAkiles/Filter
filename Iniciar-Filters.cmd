@echo off
setlocal
cd /d "%~dp0"
set "MPLCONFIGDIR=%~dp0.cache\matplotlib"
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Ambiente Python nao encontrado. Siga a instalacao no README.md.
    pause
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" main.py
if errorlevel 1 pause
endlocal
