@echo off
setlocal
cd /d "%~dp0.."

set "TEST_BIN=..\build\bin\x64\Debug"

echo ==========================================
echo === Running GCS Interface Tests ===
echo ==========================================

echo.
echo === test_core ===
"%TEST_BIN%\test_core.exe"
echo.

echo === test_io ===
"%TEST_BIN%\test_io.exe"
echo.

echo === test_dcm ===
"%TEST_BIN%\test_dcm.exe"
echo.

echo === test_lgs ===
"%TEST_BIN%\test_lgs.exe"
echo.

echo === test_cds ===
"%TEST_BIN%\test_cds.exe"
echo.

echo === test_app ===
"%TEST_BIN%\test_app.exe"
echo.

echo ==========================================
echo === All tests complete ===
echo ==========================================
