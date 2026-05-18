@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>&1

cd /d "%~dp0.."

echo === Building test_core ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_core.exe" "test\core\test_core.cpp" "core\src\core.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_core build

echo === Building test_io ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_io.exe" "test\io\test_io.cpp" "core\src\core.cpp" "io\src\io.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_io build

echo === Building test_dcm ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_dcm.exe" "test\dcm\test_dcm.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_dcm build

echo === Building test_lgs ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_lgs.exe" "test\lgs\test_lgs.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_lgs build

echo === Building test_cds ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_cds.exe" "test\cds\test_cds.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" "cds\src\cds.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_cds build

echo === Building test_app ===
cl /EHsc /std:c++17 /I"core\include" /I"io\include" /I"dcm\include" /I"lgs\include" /I"cds\include" /I"app\include" /I"test" /Fe:"x64\Debug\test_app.exe" "test\app\test_app.cpp" "app\src\App.cpp" "core\src\core.cpp" "io\src\io.cpp" "dcm\src\dcm.cpp" "lgs\src\lgs.cpp" "cds\src\cds.cpp" /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 echo FAILED: test_app build

echo.
echo === All test builds complete ===
