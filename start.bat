@echo off
setlocal
title Keystone
cd /d "%~dp0"

rem ------------------------------------------------------------------
rem  Keystone launcher for Windows. Double-click to start.
rem  If Python 3.8+ isn't installed, it offers to install Python 3.12
rem  for this user only (no admin rights needed), then starts the app.
rem ------------------------------------------------------------------

call :find_python
if defined PY goto run

echo.
echo  Keystone needs Python 3.8 or newer, and it isn't installed on this PC.
echo.
choice /c YN /m " Install Python 3.12 now (about 25 MB download, no admin rights needed)"
if errorlevel 2 goto manual

echo.
echo  Installing Python. This takes a minute or two...
echo.

rem  1. winget, which comes with Windows 10 and 11
where winget >nul 2>nul
if %errorlevel%==0 (
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    call :find_python
)
if defined PY goto installed

rem  2. otherwise, the official installer from python.org
set "ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
set "PYURL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-%ARCH%.exe"
set "PYEXE=%TEMP%\keystone-python-setup.exe"
echo  Downloading %PYURL%
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = 'Tls12'; Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYEXE%'"
if not exist "%PYEXE%" goto manual
echo  Running the installer...
"%PYEXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0
del "%PYEXE%" >nul 2>nul
call :find_python
if defined PY goto installed
goto manual

:installed
echo.
echo  Python is installed. Starting Keystone...
echo.

:run
"%PY%" server.py
goto end

:manual
echo.
echo  Python couldn't be installed automatically.
echo  Your browser will open the Python download page. Install it, and on the
echo  first screen tick "Add python.exe to PATH". Then double-click start.bat again.
start "" "https://www.python.org/downloads/"
goto end

:find_python
rem  Sets PY to a working Python 3.8+, or leaves it empty.
set "PY="
for %%C in (py python python3) do (
    if not defined PY (
        %%C -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul && set "PY=%%C"
    )
)
rem  A Python installed a moment ago isn't on this window's PATH yet, so look where it goes
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Launcher\py.exe"
exit /b 0

:end
echo.
pause
