@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE="
for %%P in (
  "C:\Users\NAITIK PATHAK\AppData\Local\Programs\Python\Python314\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) do (
  if not defined PYTHON_EXE if exist "%%~P" (
    "%%~P" -c "import flask" >nul 2>nul && set "PYTHON_EXE=%%~P"
  )
)
if not defined PYTHON_EXE (
  echo Could not find an installed Python with Flask.
  echo Install Flask for Python 3.10 or newer, then run this file again.
  pause
  exit /b 1
)
"%PYTHON_EXE%" app.py
if errorlevel 1 (
  echo The app could not start. Review the error above.
  pause
)
