@echo off
REM Panel de agentes en http://localhost:8021
cd /d "%~dp0"
set "PATH=%~dp0.venv\Scripts;%PATH%"
start http://localhost:8021
python board\server.py
