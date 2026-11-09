param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8765
)

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "프로젝트 .venv를 찾을 수 없습니다: $python"
}

& $python -m uvicorn app.main:app --host $HostAddress --port $Port
