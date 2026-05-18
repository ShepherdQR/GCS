@echo off
if "%~1"=="" (
    echo Usage: run_display.bat ^<graph_file^> [--viewer^|--server^|--summary^|--scene]
    echo        run_display.bat ^<scene_subdir^> --scene
    echo.
    echo   --viewer   : Open matplotlib 3D viewer ^(default^)
    echo   --server   : Start web server for Three.js viewer
    echo   --summary  : Print graph summary only
    echo   --scene    : Treat ^<scene_subdir^> as scene/^<subdir^>, display each txt separately
    echo.
    echo Example: run_display.bat g1.txt --viewer
    echo          run_display.bat bcc --scene
    exit /b 1
)
C:\Softwares\miniconda3\python.exe "%~dp0run_display.py" %*
