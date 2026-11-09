param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8765
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Project .venv was not found: $python"
}

Push-Location $projectRoot
try {
    & $python -m uvicorn app.main:app --host $HostAddress --port $Port
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
