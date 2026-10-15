@echo off
REM Agentes autónomos: ejecutan las tareas del panel. Pausa desde el panel o creando board\STOP.
cd /d "%~dp0"
REM python del proyecto (.venv) primero: es el que usan los agentes
set "PATH=%~dp0.venv\Scripts;%PATH%"
set PYTHONUTF8=1
REM Sin CLI instalada: usa la que trae la app de escritorio (Claude Code)
where claude >nul 2>nul || for /f "delims=" %%i in ('dir /b /s /o:n "%APPDATA%\Claude\claude-code\claude.exe" 2^>nul') do set "CLAUDE_BIN=%%i"
if not defined CLAUDE_BIN where claude >nul 2>nul || (
  echo [!] Claude Code no esta instalado. En PowerShell: irm https://claude.ai/install.ps1 ^| iex
  pause & exit /b 1
)
python board\runner.py %*
pause
