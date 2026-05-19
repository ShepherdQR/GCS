@echo off
setlocal

set "REPO_ROOT=%~dp0"
set "CMAKE_EXE=C:\Softwares\Cmake\cmake_4_3_2\bin\cmake.exe"
set "LLVM_DIR=C:\Softwares\LLVM\LLVM_20_1_7\bin"
set "NINJA_DIR=C:\Softwares\ninja\ninja_1_13_2"
set "PATH=%LLVM_DIR%;%NINJA_DIR%;C:\Softwares\Cmake\cmake_4_3_2\bin;%PATH%"

pushd "%REPO_ROOT%"
"%CMAKE_EXE%" --preset clang-ninja
if errorlevel 1 (
    set "EXIT_CODE=%ERRORLEVEL%"
    popd
    exit /b %EXIT_CODE%
)

"%CMAKE_EXE%" --build --preset clang-ninja
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
