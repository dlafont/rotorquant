param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Output = $null
)

$PythonScript = Join-Path $Root "scripts\python\environment_report.py"

if (-not (Test-Path -LiteralPath $PythonScript)) {
    throw "Missing environment report script: $PythonScript"
}

$args = @("--root", $Root)
if ($Output) {
    $args += @("--output", $Output)
}

python $PythonScript @args
