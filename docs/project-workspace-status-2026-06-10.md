# RotorQuant Workspace Status Report

Date: 2026-06-10

This report summarizes what has changed in this local workspace since it was
first created from the repository baseline.

## Baseline

- Local workspace baseline: `origin/main` / `upstream/main`
- Baseline commit: `fcd7676` (`Merge pull request #2 from mikee-gwu/fix-blackwell-aarch64-support`)
- Local branch: `eval/kv-cache-benchmark-automation`
- Current branch commit: `d0ed46c` (`Track session handoff artifacts`)
- Reflog evidence:
  - `2026-05-13 16:01:29 -0600`: `main` created from `origin/main`
  - `2026-05-14 11:34:49 -0600`: handoff/TODO commit created
  - `2026-05-14 11:36:39 -0600`: checkout to `eval/kv-cache-benchmark-automation`

The repository still tracks both remotes:

- `origin`: `https://github.com/dlafont/rotorquant.git`
- `upstream`: `https://github.com/scrya-com/rotorquant.git`

## High-Level Progress

The workspace has moved from a research-code checkout into a more operational
benchmarking workspace. The main progress is around making KV-cache benchmark
automation explicit, repeatable, and testable.

The most important additions are:

- a benchmark automation TODO and implementation plan
- environment and llama.cpp build reporting scripts
- benchmark matrix configuration files
- single-run and matrix benchmark wrappers
- llama-bench output parsing and markdown reporting helpers
- focused unit tests covering the new automation modules
- metadata and handoff notes under `_meta/`

The project-level technical milestone captured in `AGENTS.md` is that the
llama.cpp CUDA integration has already reached working 3-bit symmetric and
asymmetric KV-cache configurations, with IsoQuant and PlanarQuant results
recorded against WikiText-2. That CUDA work appears to live in the external
llama.cpp integration branch noted there, while this workspace is now adding the
local automation needed to reproduce and extend those measurements.

## Committed Local Work

One local commit exists on top of the cloned baseline:

`d0ed46c Track session handoff artifacts`

That commit added:

- `TODO-kv-cache-benchmark-automation.md`
- `codex-session-doctor.ps1.before.patch`
- `PRJ-rotorquant.code-workspace`
- `_meta/Codex_chat_copies/Clone_and_compile_rotoquant_project_chat.md`

The commit is mostly handoff and planning material. It establishes the benchmark
automation mission, expected result structure, repository detection needs,
environment setup work, build automation targets, cache method matrix, benchmark
matrix, accuracy harness ideas, reporting schema, and definition of done.

## Current Uncommitted Work

The working tree contains the larger implementation pass for benchmark
automation. These files are currently untracked or modified, so they are not yet
part of the branch history.

### Benchmark Configs

New config files under `configs/` define the first benchmark inputs:

- `configs/models.yaml`
  - `qwen_3b`: small validation model placeholder
  - `llama_8b`: practical local benchmark model placeholder
- `configs/cache_methods.yaml`
  - baselines: `f16_f16`, `q8_q8`, `q4_q4`
  - experimental methods: `turbo3_turbo3`, `planar3_planar3`, `iso3_iso3`
- `configs/benchmark.matrix.yaml`
  - build profiles: CPU and CUDA
  - context sizes: 2048, 4096, 8192, 16384
  - prompt sizes: 512, 2048, 4096
  - generation tokens: 256
  - performance repetitions: 3
  - deterministic seed and temperature settings

### Python Automation

New scripts under `scripts/python/` implement the core automation layer:

- `environment_report.py`
  - detects whether the checkout looks like RotorQuant research code,
    llama.cpp, or a hybrid layout
  - collects git metadata
  - writes `results/reports/environment-report.md`
- `llamacpp_build.py`
  - detects llama.cpp source location
  - checks CMake, Ninja, MSVC, and CUDA toolchain availability
  - writes a build plan to `results/reports/llamacpp-build-report.md`
- `benchmark_config.py`
  - loads model, cache-method, and matrix YAML files
- `benchmark_matrix.py`
  - expands models, cache methods, build profiles, context sizes, prompt
    lengths, generation lengths, GPU layers, and repetitions into jobs
- `benchmark_manifest.py`
  - resolves the llama.cpp source root
  - creates stable run identifiers
- `run_single_llama_bench.py`
  - builds a `llama-bench` command
  - supports cache K/V flags, GPU layers, flash attention, dry-run mode, and
    missing-model skips
  - writes raw JSON and parsed CSV outputs
- `run_benchmark_matrix.py`
  - runs expanded benchmark jobs
  - supports quick mode
  - writes the summary report after the matrix finishes
- `parse_llama_bench.py`
  - parses JSON stdout from `llama-bench`
  - classifies rows as prefill, decode, prompt-gen, depth, or other
  - writes/appends normalized CSV rows
- `benchmark_report.py`
  - builds markdown summary reports from run summaries and parsed rows

### PowerShell Entrypoints

New PowerShell wrappers make the Python automation easier to run from Windows:

- `scripts/setup/check-environment.ps1`
- `scripts/setup/build-llamacpp.ps1`
- `scripts/bench/run-single-llama-bench.ps1`
- `scripts/bench/run-benchmark-matrix.ps1`

These wrappers forward parameters into the matching Python modules.

### Documentation

New docs explain the intended benchmark flow:

- `docs/benchmark-pipelines.md`
  - maps five pipeline stages:
    1. Environment Readiness
    2. llama.cpp Build Planning
    3. Single Benchmark Execution
    4. Benchmark Matrix Orchestration
    5. Result Normalization and Reporting
- `docs/superpowers/plans/2026-05-14-kv-cache-benchmark-automation.md`
  - records the implementation plan for the automation work
- `_meta/`
  - stores research references and Codex handoff material outside the main
    project source tree

### Tests

New tests cover the benchmark automation modules:

- config loading
- source-root resolution
- stable run-id generation
- benchmark matrix expansion
- markdown report generation
- environment/repo profile detection
- llama.cpp build-report planning
- llama-bench JSON parsing and CSV writing
- single-run benchmark behavior
- matrix quick-mode behavior

The focused test suite currently contains 35 tests for this automation layer.

## Working Tree Notes

Current tracked modifications:

- `.gitignore`
  - now ignores `.pytest_cache/`, `results/`, `tools/llama.cpp/`, and
    `tools/llama.cpp/build-*`
- `TODO-kv-cache-benchmark-automation.md`
  - the first smoke-test milestone now explicitly includes repo-shape
    detection, missing llama.cpp reporting, source-root location, build-report
    clarity, and build-tool detection
- `paper/arxiv_metadata.txt`, `paper/rotorquant.pdf`, and
  `paper/rotorquant.tex`
  - are deleted from their original tracked location
  - corresponding research copies now exist under `_meta/Research/`

The paper-file move/deletion should be reviewed before committing because it
changes tracked project artifacts, not just benchmark automation files.

## Verification

Focused benchmark automation tests were run with pytest temp storage redirected
inside the workspace:

```powershell
python -m pytest tests/test_benchmark_config.py tests/test_benchmark_manifest.py tests/test_benchmark_matrix.py tests/test_benchmark_report.py tests/test_environment_report.py tests/test_llamacpp_build.py tests/test_parse_llama_bench.py tests/test_run_benchmark_matrix.py tests/test_run_single_llama_bench.py --basetemp .pytest-tmp -p no:cacheprovider
```

Result:

```text
35 passed in 0.43s
```

A first pytest run without `--basetemp .pytest-tmp` failed because Windows
denied access to `C:\Users\dlafo\AppData\Local\Temp\pytest-of-dlafo`. That was
an environment/temp-directory issue, not a code assertion failure.

## Remaining Gaps

The benchmark automation is scaffolded and tested, but it is not yet the full
measurement pipeline. The main remaining work is:

- build or locate the experimental llama.cpp checkout under `tools/llama.cpp/`
  or at a direct llama.cpp-style root
- run actual `llama-bench` jobs against local GGUF model paths
- detect unsupported cache methods and continue the matrix safely
- add GPU telemetry collection
- add perplexity runs
- add needle-in-haystack and fact-recall accuracy harnesses
- generate final comparison tables and charts from real benchmark outputs
- decide whether the original tracked `paper/` files should remain, move to
  `_meta/Research/`, or be restored before the next commit

## Suggested Next Step

Commit the benchmark automation files as a coherent branch checkpoint after
reviewing the `paper/` relocation. After that, the next practical milestone is
to connect `tools/llama.cpp/` to the experimental fork and run the smallest
dry-run or smoke-test benchmark matrix.
