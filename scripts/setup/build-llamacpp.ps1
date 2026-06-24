param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Output = $null,
    [string]$Profile = "release",
    [string]$Backend = "cpu",
    [switch]$FlashAttention
)

$PythonScript = Join-Path $Root "scripts\python\llamacpp_build.py"

if (-not (Test-Path -LiteralPath $PythonScript)) {
    throw "Missing build planner script: $PythonScript"
}

$args = @("--root", $Root, "--profile", $Profile, "--backend", $Backend)
if ($FlashAttention) {
    $args += "--flash-attention"
}
if ($Output) {
    $args += @("--output", $Output)
}

python $PythonScript @args
