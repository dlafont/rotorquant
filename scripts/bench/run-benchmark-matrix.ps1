param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Profile = "release",
    [string]$Backend = "cpu",
    [switch]$DryRun,
    [switch]$Quick
)

$PythonScript = Join-Path $Root "scripts\python\run_benchmark_matrix.py"
if (-not (Test-Path -LiteralPath $PythonScript)) {
    throw "Missing benchmark matrix script: $PythonScript"
}

$args = @("--root", $Root, "--profile", $Profile, "--backend", $Backend)
if ($DryRun) {
    $args += "--dry-run"
}

if ($Quick) {
    $args += "--quick"
}

python $PythonScript @args
