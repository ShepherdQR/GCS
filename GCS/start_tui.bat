@echo off
setlocal
cd /d "%~dp0"

if defined GCS_PYTHON (
    "%GCS_PYTHON%" -m gcs_viz %*
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python -m gcs_viz %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 -m gcs_viz %*
    exit /b %ERRORLEVEL%
)

echo Python 3 was not found. Install Python 3 or set GCS_PYTHON to the interpreter path.
exit /b 1
