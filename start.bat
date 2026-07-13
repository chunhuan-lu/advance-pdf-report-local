@echo off
REM ============================================================
REM  Advance Report Studio - one-click launcher
REM  Finds (or installs) Python, sets up deps, starts the app.
REM ============================================================
setlocal
cd /d "%~dp0"
set "VENV=.venv\Scripts\python.exe"

REM ---- refuse to run from inside a ZIP preview (Explorer extracts only this bat to Temp) ----
set "HERE=%~dp0"
set "NOTMP=%HERE:AppData\Local\Temp=%"
if not "%NOTMP%"=="%HERE%" (
    echo.
    echo [ERROR] It looks like start.bat was started from inside a ZIP file.
    echo         Right-click the ZIP, choose "Extract All...", then open the
    echo         extracted folder and double-click start.bat there.
    echo.
    pause
    exit
)

if not exist "local_store" mkdir "local_store"

REM ---- finish a launcher update staged by a previous run ----
if exist "start.bat.new" (move /y "start.bat.new" "start.bat" >nul & start "" "%~f0" & exit)

REM ---- auto-update to the latest version (needs internet; skipped on git working copies) ----
if exist ".git" (
    where git >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Git working copy detected - auto-update skipped.
        goto pysetup
    )
    echo [WARN] Found a .git folder but no git client - treating this as a normal install.
)
if not exist "update.ps1" (
    echo [INFO] First-time setup - downloading the updater ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/chunhuan-lu/advance-pdf-report-local/master/update.ps1' -OutFile 'update.ps1' -TimeoutSec 60"
)
if exist "update.ps1" powershell -NoProfile -ExecutionPolicy Bypass -File "update.ps1"
if exist "start.bat.new" (move /y "start.bat.new" "start.bat" >nul & start "" "%~f0" & exit)

if not exist "requirements.txt" (
    echo.
    echo [ERROR] Application files are missing and could not be downloaded.
    echo         Please check your internet connection and double-click
    echo         start.bat again, or copy the full application folder
    echo         onto this computer.
    pause
    exit
)

:pysetup
if exist "%VENV%" (
    "%VENV%" -c "pass" >nul 2>&1
    if not errorlevel 1 goto deps
    echo [WARN] Existing virtual environment is broken - recreating it ...
    rmdir /s /q ".venv"
)

call :findpy
if defined PY goto venv

echo [INFO] Python not found. Trying winget ...
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
call :findpy
if defined PY goto venv

echo [INFO] winget unavailable. Downloading Python 3.12 installer from python.org ...
set "PYSETUP=%TEMP%\python-3.12.10-amd64.exe"
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile '%PYSETUP%'"
if not exist "%PYSETUP%" goto nopython

echo [INFO] Installing Python 3.12 silently (per-user) ...
"%PYSETUP%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
call :findpy
if defined PY goto venv
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto venv
goto nopython

:findpy
set "PY="
py -3.12 -c "pass" >nul 2>&1
if not errorlevel 1 (set "PY=py -3.12" & goto :eof)
py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
if not errorlevel 1 (set "PY=py -3" & goto :eof)
python -c "import sys;raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
if not errorlevel 1 (set "PY=python" & goto :eof)
goto :eof

:venv
echo [INFO] Creating virtual environment ...
%PY% -m venv .venv
if not exist "%VENV%" goto fail

:deps
echo [INFO] Checking dependencies (first run may take a few minutes) ...
"%VENV%" -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo [WARN] pip install failed. Retrying with Tsinghua mirror ...
    "%VENV%" -m pip install -r requirements.txt -q --disable-pip-version-check -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 goto fail
)

echo [INFO] Applying database migrations ...
"%VENV%" manage.py migrate --noinput
if errorlevel 1 goto fail

echo.
echo ============================================================
echo   Advance Report Studio is running.
echo.
echo   On this PC :  http://127.0.0.1:8000
echo   On a phone :  join the same Wi-Fi, then open one of:
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do echo                 http://%%i:8000 ^(remove spaces^)
echo.
echo   Close this window or press Ctrl+C to stop.
echo ============================================================
echo.
start "" http://127.0.0.1:8000
"%VENV%" manage.py runserver 0.0.0.0:8000 --noreload
goto :eof

:nopython
echo.
echo [ERROR] Could not install Python automatically.
echo         Please install Python 3.12 manually from:
echo         https://www.python.org/downloads/
echo         then double-click start.bat again.
pause
goto :eof

:fail
echo.
echo [ERROR] Setup failed. Check the messages above.
pause
