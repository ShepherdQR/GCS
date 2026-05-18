@echo off
cd /d "%~dp0.."

echo ==========================================
echo === Running GCS Interface Tests ===
echo ==========================================

echo.
echo === test_core ===
x64\Debug\test_core.exe
echo.

echo === test_io ===
x64\Debug\test_io.exe
echo.

echo === test_dcm ===
x64\Debug\test_dcm.exe
echo.

echo === test_lgs ===
x64\Debug\test_lgs.exe
echo.

echo === test_cds ===
x64\Debug\test_cds.exe
echo.

echo === test_app ===
x64\Debug\test_app.exe
echo.

echo ==========================================
echo === All tests complete ===
echo ==========================================
