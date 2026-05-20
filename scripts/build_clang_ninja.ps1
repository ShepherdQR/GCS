$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..")
$cmake = "C:\Softwares\Cmake\cmake_4_3_2\bin\cmake.exe"
$ninjaDir = "C:\Softwares\ninja\ninja_1_13_2"
$llvmDir = "C:\Softwares\LLVM\LLVM_20_1_7\bin"

$env:PATH = "$llvmDir;$ninjaDir;$(Split-Path -Parent $cmake);$env:PATH"

Push-Location $repoRoot
try {
    & $cmake --preset clang-ninja
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $cmake --build --preset clang-ninja
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
