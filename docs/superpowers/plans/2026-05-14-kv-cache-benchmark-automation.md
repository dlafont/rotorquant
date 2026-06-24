# KV Cache Benchmark Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working benchmark automation slice for RotorQuant that can find the experimental llama.cpp fork, describe the local build environment, and run a dry-run or real llama-bench invocation with recorded outputs.

**Architecture:** Keep the new automation layer thin and file-oriented. Python helpers will own repo/build detection and run metadata, while PowerShell entrypoints stay as small shims for Windows usage. The first slice will focus on CPU/MSVC execution against `tools/llama.cpp/`, with CUDA treated as an optional build profile that is only enabled when the machine supports it.

**Tech Stack:** Python 3.11+, PowerShell 7+, pytest, YAML/CSV/Markdown file output, existing `scripts/python/environment_report.py`, existing `scripts/python/llamacpp_build.py`, and llama.cpp `llama-bench`.

---

### Task 1: Lock the benchmark run model

**Files:**
- Create: `scripts/python/benchmark_manifest.py`
- Create: `tests/test_benchmark_manifest.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from benchmark_manifest import BenchmarkRunRequest, default_run_id, resolve_source_root


def test_resolve_source_root_prefers_tools_llama_cpp(tmp_path: Path) -> None:
    (tmp_path / "tools" / "llama.cpp" / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "llama.cpp" / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (tmp_path / "tools" / "llama.cpp" / "examples").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "llama.cpp" / "ggml").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "llama.cpp" / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)

    assert resolve_source_root(tmp_path) == tmp_path / "tools" / "llama.cpp"


def test_default_run_id_is_stable_for_identical_inputs() -> None:
    a = default_run_id("release", "llama-bench", "model_a", 2048, 512, 128, "f16", "f16")
    b = default_run_id("release", "llama-bench", "model_a", 2048, 512, 128, "f16", "f16")

    assert a == b


def test_benchmark_request_round_trips_optional_cuda_flag() -> None:
    request = BenchmarkRunRequest(
        build_profile="release",
        model_id="model_a",
        model_path=Path("D:/models/model.gguf"),
        ctx_size=2048,
        prompt_tokens=512,
        gen_tokens=128,
        cache_k="f16",
        cache_v="f16",
        enable_cuda=False,
    )

    assert request.enable_cuda is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_benchmark_manifest.py -v`
Expected: fail because `scripts/python/benchmark_manifest.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from hashlib import sha1


@dataclass(frozen=True)
class BenchmarkRunRequest:
    build_profile: str
    model_id: str
    model_path: Path
    ctx_size: int
    prompt_tokens: int
    gen_tokens: int
    cache_k: str
    cache_v: str
    enable_cuda: bool = False


def resolve_source_root(root: Path) -> Path:
    root = root.resolve()
    for candidate in (root / "tools" / "llama.cpp", root):
        if (
            (candidate / "CMakeLists.txt").exists()
            and (candidate / "examples").exists()
            and (candidate / "ggml").exists()
            and (candidate / "src" / "llama.cpp").exists()
        ):
            return candidate
    raise FileNotFoundError("No llama.cpp source root found")


def default_run_id(
    build_profile: str,
    executable: str,
    model_id: str,
    ctx_size: int,
    prompt_tokens: int,
    gen_tokens: int,
    cache_k: str,
    cache_v: str,
) -> str:
    payload = "|".join(
        [
            build_profile,
            executable,
            model_id,
            str(ctx_size),
            str(prompt_tokens),
            str(gen_tokens),
            cache_k,
            cache_v,
        ]
    )
    return sha1(payload.encode("utf-8")).hexdigest()[:12]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_benchmark_manifest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/python/benchmark_manifest.py tests/test_benchmark_manifest.py
git commit -m "feat: add benchmark run manifest helpers"
```

### Task 2: Add benchmark report and result row plumbing

**Files:**
- Create: `scripts/python/benchmark_report.py`
- Create: `tests/test_benchmark_report.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from benchmark_report import build_benchmark_report, write_benchmark_report


def test_build_benchmark_report_mentions_cuda_as_optional(tmp_path: Path) -> None:
    report = build_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[
            {
                "run_id": "abc123",
                "status": "skipped",
                "cache_k": "f16",
                "cache_v": "f16",
                "notes": "dry-run",
            }
        ],
    )

    assert "CUDA" in report
    assert "dry-run" in report
    assert "abc123" in report


def test_write_benchmark_report_creates_file(tmp_path: Path) -> None:
    output = write_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[],
    )

    assert output.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_benchmark_report.py -v`
Expected: fail because `scripts/python/benchmark_report.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


def build_benchmark_report(
    root: Path,
    source_root: Path,
    build_profile: str,
    run_summary: Iterable[Mapping[str, object]],
) -> str:
    lines = [
        "# Benchmark Automation Report",
        "",
        f"- Root: `{root}`",
        f"- Source root: `{source_root}`",
        f"- Build profile: `{build_profile}`",
        "- CUDA profile: optional, enabled only when the local toolchain supports it",
        "",
        "## Runs",
        "| run_id | status | cache_k | cache_v | notes |",
        "|---|---|---|---|---|",
    ]
    for row in run_summary:
        lines.append(
            f"| `{row.get('run_id', '')}` | {row.get('status', '')} | {row.get('cache_k', '')} | {row.get('cache_v', '')} | {row.get('notes', '')} |"
        )
    return "\n".join(lines) + "\n"


def write_benchmark_report(
    root: Path,
    source_root: Path,
    build_profile: str,
    run_summary: Iterable[Mapping[str, object]],
    output_path: Path | None = None,
) -> Path:
    output_path = output_path or (root / "results" / "reports" / "benchmark-automation-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_benchmark_report(root, source_root, build_profile, run_summary),
        encoding="utf-8",
    )
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_benchmark_report.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/python/benchmark_report.py tests/test_benchmark_report.py
git commit -m "feat: add benchmark report writer"
```

### Task 3: Wire the PowerShell benchmark entrypoint

**Files:**
- Create: `scripts/bench/run-single-llama-bench.ps1`
- Modify: `scripts/setup/build-llamacpp.ps1`
- Create: `tests/test_run_single_llama_bench.ps1` or a Python-level proxy test if PS tests are not practical

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from benchmark_manifest import resolve_source_root


def test_resolve_source_root_reports_missing_checkout(tmp_path: Path) -> None:
    try:
        resolve_source_root(tmp_path)
    except FileNotFoundError as exc:
        assert "llama.cpp" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_benchmark_manifest.py -v`
Expected: fail until the missing-checkout path is implemented with a clear message.

- [ ] **Step 3: Write minimal implementation**

```powershell
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$Profile = "release",
    [switch]$DryRun
)

$PythonScript = Join-Path $Root "scripts\python\run_single_llama_bench.py"
if (-not (Test-Path -LiteralPath $PythonScript)) {
    throw "Missing benchmark runner script: $PythonScript"
}

$args = @("--root", $Root, "--profile", $Profile)
if ($DryRun) {
    $args += "--dry-run"
}

python $PythonScript @args
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_benchmark_manifest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/bench/run-single-llama-bench.ps1 scripts/setup/build-llamacpp.ps1
git commit -m "feat: add benchmark entrypoint shim"
```

### Task 4: Add the first Python runner with dry-run and real-run scaffolding

**Files:**
- Create: `scripts/python/run_single_llama_bench.py`
- Create: `tests/test_run_single_llama_bench.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from run_single_llama_bench import build_command, summarize_run


def test_build_command_uses_short_cache_flags_when_requested(tmp_path: Path) -> None:
    cmd = build_command(
        executable=Path("llama-bench.exe"),
        model_path=Path("D:/models/model.gguf"),
        ctx_size=2048,
        prompt_tokens=512,
        gen_tokens=128,
        gpu_layers=999,
        cache_k="f16",
        cache_v="f16",
        short_cache_flags=True,
    )

    assert "-ctk" in cmd
    assert "-ctv" in cmd


def test_summarize_run_marks_dry_run() -> None:
    row = summarize_run(run_id="abc123", status="skipped", notes="dry-run")

    assert row["run_id"] == "abc123"
    assert row["status"] == "skipped"
    assert row["notes"] == "dry-run"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_single_llama_bench.py -v`
Expected: fail because the runner module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

from pathlib import Path


def build_command(
    executable: Path,
    model_path: Path,
    ctx_size: int,
    prompt_tokens: int,
    gen_tokens: int,
    gpu_layers: int,
    cache_k: str,
    cache_v: str,
    short_cache_flags: bool,
) -> list[str]:
    command = [
        str(executable),
        "-m",
        str(model_path),
        "-p",
        str(prompt_tokens),
        "-n",
        str(gen_tokens),
        "-c",
        str(ctx_size),
        "-ngl",
        str(gpu_layers),
    ]
    if short_cache_flags:
        command.extend(["-ctk", cache_k, "-ctv", cache_v])
    else:
        command.extend(["--cache-type-k", cache_k, "--cache-type-v", cache_v])
    return command


def summarize_run(run_id: str, status: str, notes: str = "") -> dict[str, str]:
    return {"run_id": run_id, "status": status, "notes": notes}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_single_llama_bench.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/python/run_single_llama_bench.py tests/test_run_single_llama_bench.py
git commit -m "feat: add llama-bench command builder"
```

### Task 5: Verify the first end-to-end dry run against the proven build

**Files:**
- Modify: `scripts/python/run_single_llama_bench.py`
- Modify: `scripts/python/benchmark_report.py`
- Possibly modify: `scripts/python/llamacpp_build.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from run_single_llama_bench import summarize_run


def test_summarize_run_marks_unsupported_methods() -> None:
    row = summarize_run(run_id="abc123", status="unsupported", notes="invalid value")

    assert row["status"] == "unsupported"
    assert "invalid value" in row["notes"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_single_llama_bench.py -v`
Expected: fail until unsupported-status handling is added.

- [ ] **Step 3: Write minimal implementation**

```python
def summarize_run(run_id: str, status: str, notes: str = "") -> dict[str, str]:
    return {
        "run_id": run_id,
        "status": status,
        "notes": notes,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_single_llama_bench.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/python/run_single_llama_bench.py tests/test_run_single_llama_bench.py
git commit -m "feat: add benchmark run status plumbing"
```

### Task 6: Smoke test the automation layer against the local fork

**Files:**
- Modify: `scripts/setup/build-llamacpp.ps1`
- Modify: `scripts/setup/check-environment.ps1`
- Create or update: `results/reports/benchmark-automation-report.md`

- [ ] **Step 1: Run the new dry-run path**

Run: `powershell -File scripts/setup/build-llamacpp.ps1 -Profile release`

Expected:
- The script reports the `tools/llama.cpp` source root.
- The script does not require CUDA to be installed.
- The report file is written under `results/reports/`.

- [ ] **Step 2: Run the runner in dry-run mode**

Run: `powershell -File scripts/bench/run-single-llama-bench.ps1 -Profile release -DryRun`

Expected:
- A deterministic run ID is produced.
- No benchmark process is launched.
- A report row is written with `status=skipped` and a `dry-run` note.

- [ ] **Step 3: Run the existing pytest suite**

Run: `pytest`

Expected:
- All existing tests still pass.
- The new benchmark-manifest, report, and runner tests pass.

- [ ] **Step 4: Commit**

```bash
git add scripts docs tests results/reports/benchmark-automation-report.md
git commit -m "feat: scaffold benchmark automation for llama.cpp fork"
```

