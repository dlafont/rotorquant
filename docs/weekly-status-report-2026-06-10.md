# Weekly Status Report - RotoQuant KV-Cache Compression Evaluation

**Student:** Donald Lafont
**Course:** Language Models
**Week ending:** 2026-06-10
**Project focus:** Local LLM KV-cache/context compression evaluation

## 1. Summary of Progress

This week I moved the project from the approved proposal stage into a more
concrete evaluation-harness stage. The original proposal focused on testing
whether RotoQuant-style KV-cache compression can make local long-context LLM
workflows more practical, especially on constrained local hardware.

The main work completed so far is the setup of the benchmark automation layer
that will support that evaluation. I now have project documentation,
configuration files, Python automation scripts, PowerShell entrypoints, and unit
tests that define how the local benchmark process should work.

The most important progress is that the project is no longer only a research
idea. It now has a structured local workflow for:

- detecting the project/runtime environment
- planning a `llama.cpp` build
- defining benchmark models and KV-cache methods
- expanding benchmark matrix jobs
- running a single `llama-bench` job
- parsing benchmark output
- writing normalized CSV and markdown reports
- testing the automation code before running larger experiments

Actual full benchmark measurements are still a next-step item, but the project
now has the harness structure needed to produce those results in a repeatable
way.

## 2. Alignment With Approved Proposal

| Proposal objective | Work completed so far | Status |
| --- | --- | --- |
| Build an evaluation harness for local LLM KV-cache/context compression | Added Python benchmark automation modules under `scripts/python/` and Windows wrappers under `scripts/bench/` and `scripts/setup/` | In progress, main scaffold complete |
| Compare standard uncompressed KV-cache against compressed methods | Added cache-method config entries for `f16_f16`, `q8_q8`, `q4_q4`, `turbo3_turbo3`, `planar3_planar3`, and `iso3_iso3` | Configured, not fully benchmarked yet |
| Use `llama.cpp` as the practical runtime target | Added source-root detection, build-report planning, and `llama-bench` command construction | In progress |
| Measure performance metrics such as latency and throughput | Added `llama-bench` JSON parsing and normalized CSV/report generation | Parser/report layer complete for initial runs |
| Measure local-machine practicality under hardware constraints | Added CPU/CUDA build profiles, context-size matrix, and model placeholders for local GGUF files | Configured, measurement still pending |
| Begin with long-context baseline tests | Added benchmark matrix support for multiple context sizes from 2048 to 16384 | First benchmark path prepared |
| Move toward codebase-oriented evaluation if setup succeeds | Current work is focused on the general benchmark harness first | Future step |
| Validate results rather than only claiming compression benefits | Added report generation and tests so results can be recorded with run metadata | In progress |

## 3. Completed Work

### 3.1 Project Proposal Connected to the Work Stack

The approved proposal frames the project as one focused part of a larger local
AI/LLM work stack. I kept the current implementation aligned with the proposal
by focusing on the following stack areas:

- **Context Engineering:** defining how context length and KV-cache methods will
  be varied during testing.
- **Model Layer:** preparing `llama.cpp` and GGUF model paths as the local
  inference target.
- **Agent / Harness / Orchestration:** building scripts that can coordinate
  repeatable benchmark runs.
- **Validation / Evals:** creating parsers, reports, and tests so results can be
  checked instead of only manually observed.
- **Infrastructure & Operations:** handling local Windows, CUDA, build-tool, and
  file-path concerns.

This is important because the course proposal was not just about compression in
the abstract. It was about whether compression improves the practical usefulness
of a local LLM workflow.

### 3.2 Benchmark Automation Scripts

I added a first version of the benchmark automation layer:

- `scripts/python/environment_report.py`
- `scripts/python/llamacpp_build.py`
- `scripts/python/benchmark_config.py`
- `scripts/python/benchmark_manifest.py`
- `scripts/python/benchmark_matrix.py`
- `scripts/python/run_single_llama_bench.py`
- `scripts/python/run_benchmark_matrix.py`
- `scripts/python/parse_llama_bench.py`
- `scripts/python/benchmark_report.py`

These scripts cover the main pieces needed for the evaluation harness:

- environment detection
- build planning
- config loading
- benchmark job expansion
- run ID generation
- `llama-bench` command construction
- raw output capture
- output parsing
- CSV/report writing

This directly supports the proposal's goal of building an evaluation harness
rather than doing only an informal one-off benchmark.

### 3.3 Windows Entrypoints

I added PowerShell wrappers so the workflow can be run more easily on my local
Windows machine:

- `scripts/setup/check-environment.ps1`
- `scripts/setup/build-llamacpp.ps1`
- `scripts/bench/run-single-llama-bench.ps1`
- `scripts/bench/run-benchmark-matrix.ps1`

This aligns with the proposal because the local test environment is explicitly
based on my own practical machine setup, including Windows, local GPU limits,
and `llama.cpp`.

### 3.4 Benchmark Configuration

I added configuration files under `configs/`:

- `configs/models.yaml`
- `configs/cache_methods.yaml`
- `configs/benchmark.matrix.yaml`

The benchmark config currently includes:

- two local model placeholders:
  - Qwen 2.5/3B-style validation model
  - Llama 3.1/3.2 8B-style practical benchmark model
- baseline KV-cache methods:
  - `f16_f16`
  - `q8_q8`
  - `q4_q4`
- experimental methods:
  - `turbo3_turbo3`
  - `planar3_planar3`
  - `iso3_iso3`
- context sizes:
  - 2048
  - 4096
  - 8192
  - 16384
- CPU and CUDA build profiles

The approved proposal originally described RotoQuant-style compression compared
against the uncompressed baseline. The current config expands this slightly to
include related experimental KV-cache methods already present in the project
context, while still keeping `f16_f16` as the main baseline.

### 3.5 Documentation and Handoff Notes

I added documentation so the project is easier to explain and continue:

- `docs/benchmark-pipelines.md`
- `docs/project-workspace-status-2026-06-10.md`
- `docs/superpowers/plans/2026-05-14-kv-cache-benchmark-automation.md`
- `_meta/` handoff and research reference files

The benchmark pipeline document is especially useful for the course project
because it gives a high-level map of the system:

1. Environment Readiness
2. `llama.cpp` Build Planning
3. Single Benchmark Execution
4. Benchmark Matrix Orchestration
5. Result Normalization and Reporting

This makes the work easier to present as a project architecture, not just a
collection of scripts.

### 3.6 Unit Tests

I added focused tests for the new benchmark automation layer:

- `tests/test_benchmark_config.py`
- `tests/test_benchmark_manifest.py`
- `tests/test_benchmark_matrix.py`
- `tests/test_benchmark_report.py`
- `tests/test_environment_report.py`
- `tests/test_llamacpp_build.py`
- `tests/test_parse_llama_bench.py`
- `tests/test_run_benchmark_matrix.py`
- `tests/test_run_single_llama_bench.py`

The tests verify that the harness can load configs, detect source roots, build
stable run IDs, expand benchmark jobs, parse `llama-bench` output, and generate
reports.

Verification result:

```text
35 passed in 0.43s
```

I had to run pytest with a workspace-local temp directory because the default
Windows temp path had a permission problem. After redirecting temp storage into
the workspace, the test suite passed.

## 4. Evidence of Completed Artifacts

The main completed artifacts are:

| Area | Artifact |
| --- | --- |
| Approved proposal reference | `docs/llm_work_stack_rotoquant_evaluation_plan.md` |
| Workspace progress summary | `docs/project-workspace-status-2026-06-10.md` |
| Benchmark pipeline map | `docs/benchmark-pipelines.md` |
| Benchmark plan | `docs/superpowers/plans/2026-05-14-kv-cache-benchmark-automation.md` |
| Model and method configs | `configs/models.yaml`, `configs/cache_methods.yaml`, `configs/benchmark.matrix.yaml` |
| Automation scripts | `scripts/python/` |
| Windows entrypoints | `scripts/setup/`, `scripts/bench/` |
| Test coverage | `tests/test_benchmark_*.py`, `tests/test_run_*.py`, and related automation tests |

## 5. Current Limitations

The biggest limitation is that the project is still at the harness and setup
stage. The full local benchmark results are not complete yet.

The remaining gaps are:

- connect or build the experimental `llama.cpp` fork
- confirm the exact local GGUF model paths
- run the first smoke-test benchmark matrix
- collect actual throughput, latency, and memory numbers
- add GPU telemetry collection with `nvidia-smi`
- add long-context recall tests such as needle/passkey retrieval
- later add codebase-oriented context tests if the first benchmark track works

This means the current progress is strongest on the engineering and evaluation
setup side. The next stage needs to produce measured results.

## 6. Plan for Next Week

Next week I plan to focus on turning the harness into actual measured
experiments:

1. Connect the local `llama.cpp` experimental checkout.
2. Confirm the model files and update the model config paths.
3. Run a small smoke-test benchmark using the uncompressed `f16_f16` baseline.
4. Run at least one compressed KV-cache method if the local fork supports it.
5. Save raw benchmark logs, parsed CSV rows, and a markdown report.
6. Start adding memory telemetry so VRAM usage can be compared across methods.

The goal for the next report is to move from "the harness is ready" to "the
first benchmark comparison has been run and recorded."

## 7. Short Instructor-Facing Summary

This week I made concrete progress toward the approved project proposal by
building the first version of the local evaluation harness. The proposal is
about testing whether RotoQuant-style KV-cache compression can make local
long-context LLM inference more practical. The completed work now supports that
goal by defining benchmark methods, context sizes, model placeholders, run
automation, result parsing, report generation, and unit tests.

The main accomplishment is that the project has moved from a proposed idea into
a structured benchmark workflow. The next step is to connect the experimental
`llama.cpp` runtime and begin collecting actual local performance and memory
results.
