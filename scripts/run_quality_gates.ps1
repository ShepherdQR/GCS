$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..")

Push-Location $repoRoot
try {
    & python tools\agentic_design\agentic_toolkit.py run-quality-gates @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
