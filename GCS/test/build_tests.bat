@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>&1

cd /d "%~dp0.."

set "BUILD_DIR=..\build"
set "TEST_BIN=%BUILD_DIR%\bin\x64\Debug"
set "TEST_OBJ_ROOT=%BUILD_DIR%\obj\tests\x64\Debug"

if not exist "%TEST_BIN%" mkdir "%TEST_BIN%"

echo === Building test_core ===
if not exist "%TEST_OBJ_ROOT%\test_core" mkdir "%TEST_OBJ_ROOT%\test_core"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_core\\" /Fd:"%TEST_OBJ_ROOT%\test_core\test_core.pdb" /Fe:"%TEST_BIN%\test_core.exe" "test\core\test_core.cpp" "core\src\core.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_core build

echo === Building test_io ===
if not exist "%TEST_OBJ_ROOT%\test_io" mkdir "%TEST_OBJ_ROOT%\test_io"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_io\\" /Fd:"%TEST_OBJ_ROOT%\test_io\test_io.pdb" /Fe:"%TEST_BIN%\test_io.exe" "test\io\test_io.cpp" "core\src\core.cpp" "io\src\io.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_io build

echo === Building test_dcm ===
if not exist "%TEST_OBJ_ROOT%\test_dcm" mkdir "%TEST_OBJ_ROOT%\test_dcm"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_dcm\\" /Fd:"%TEST_OBJ_ROOT%\test_dcm\test_dcm.pdb" /Fe:"%TEST_BIN%\test_dcm.exe" "test\dcm\test_dcm.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_dcm build

echo === Building test_lgs ===
if not exist "%TEST_OBJ_ROOT%\test_lgs" mkdir "%TEST_OBJ_ROOT%\test_lgs"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_lgs\\" /Fd:"%TEST_OBJ_ROOT%\test_lgs\test_lgs.pdb" /Fe:"%TEST_BIN%\test_lgs.exe" "test\lgs\test_lgs.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_lgs build

echo === Building test_cds ===
if not exist "%TEST_OBJ_ROOT%\test_cds" mkdir "%TEST_OBJ_ROOT%\test_cds"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_cds\\" /Fd:"%TEST_OBJ_ROOT%\test_cds\test_cds.pdb" /Fe:"%TEST_BIN%\test_cds.exe" "test\cds\test_cds.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" "cds\src\cds.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_cds build

echo === Building test_app ===
if not exist "%TEST_OBJ_ROOT%\test_app" mkdir "%TEST_OBJ_ROOT%\test_app"
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fo:"%TEST_OBJ_ROOT%\test_app\\" /Fd:"%TEST_OBJ_ROOT%\test_app\test_app.pdb" /Fe:"%TEST_BIN%\test_app.exe" "test\app\test_app.cpp" "app\src\App.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" "cds\src\cds.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_app build

echo.
echo === All test builds complete ===
