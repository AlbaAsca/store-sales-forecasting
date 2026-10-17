@echo off
REM Ejecución programada (Programador de tareas "store-sales runner", cada 3 h de 9 a 23 h):
REM una tarea de cada carril (pensar / medir) en paralelo o, si pensar no tiene, una ronda de aportación.
REM Pausa desde el panel o creando board\STOP. Logs: board\runs\scheduled.log (arranque), scheduled-think.log y scheduled-measure.log
cd /d "%~dp0"
set "PATH=%~dp0.venv\Scripts;%PATH%"
set PYTHONUTF8=1
if not exist board\runs mkdir board\runs
where claude >nul 2>nul || for /f "delims=" %%i in ('dir /b /s /o:n "%APPDATA%\Claude\claude-code\claude.exe" 2^>nul') do set "CLAUDE_BIN=%%i"
echo ==== %date% %time% CLAUDE_BIN=%CLAUDE_BIN% >> board\runs\scheduled.log
REM Dos carriles a la vez, cada uno con su log; espera a que terminen los dos.
powershell -NoProfile -Command "$t=Start-Process python -ArgumentList 'board\runner.py','--lane','think','--once','--contribute' -RedirectStandardOutput board\runs\scheduled-think.log -RedirectStandardError board\runs\scheduled-think.err -PassThru -NoNewWindow; $m=Start-Process python -ArgumentList 'board\runner.py','--lane','measure','--once' -RedirectStandardOutput board\runs\scheduled-measure.log -RedirectStandardError board\runs\scheduled-measure.err -PassThru -NoNewWindow; $t,$m | Wait-Process" >> board\runs\scheduled.log 2>&1
