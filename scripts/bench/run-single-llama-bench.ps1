param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Profile = "release",
    [string]$Backend = "cpu",
    [string]$ModelId = "smoke",
    [string]$ModelPath = "D:\models\model.gguf",
    [int]$CtxSize = 2048,
    [int]$PromptTokens = 512,
    [int]$GenTokens = 128,
    [string]$CacheK = "f16",
    [string]$CacheV = "f16",
    [int]$GpuLayers = 999,
    [switch]$FlashAttention,
    [switch]$ShortCacheFlags,
    [switch]$DryRun
)

$PythonScript = Join-Path $Root "scripts\python\run_single_llama_bench.py"
if (-not (Test-Path -LiteralPath $PythonScript)) {
    throw "Missing benchmark runner script: $PythonScript"
}

$args = @(
    "--root", $Root,
    "--profile", $Profile,
    "--backend", $Backend,
    "--model-id", $ModelId,
    "--model-path", $ModelPath,
    "--ctx-size", $CtxSize,
    "--prompt-tokens", $PromptTokens,
    "--gen-tokens", $GenTokens,
    "--cache-k", $CacheK,
    "--cache-v", $CacheV,
    "--gpu-layers", $GpuLayers
)

if ($FlashAttention) {
    $args += "--flash-attention"
}

if ($ShortCacheFlags) {
    $args += "--short-cache-flags"
}

if ($DryRun) {
    $args += "--dry-run"
}

python $PythonScript @args
