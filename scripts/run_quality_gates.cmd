@echo off
setlocal

set "REPO_ROOT=%~dp0.."

pushd "%REPO_ROOT%"
python tools\agentic_design\agentic_toolkit.py run-quality-gates %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
