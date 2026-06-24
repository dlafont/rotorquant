# RotorQuant Next-Steps Handoff - 2026-06-24

This file is a handoff prompt for continuing the RotorQuant course project in a
new Codex chat session.

## Copy/Paste Prompt

Paste the following prompt into the next Codex chat after opening this workspace:

```text
You are working in my local repo:

D:\Dev\PRJ-rotorquant

Project context:
This is my Language Models course project. The approved proposal is to evaluate
whether RotoQuant-style KV-cache/context compression can make local long-context
LLM inference more practical, especially on my local Windows + NVIDIA GPU setup.
The immediate objective is not to finish the whole research project. The next
objective is to prove the benchmark harness with one real smoke-test benchmark
run and saved output.

Read these files first, in this order:

1. AGENTS.md
2. docs/llm_work_stack_rotoquant_evaluation_plan.md
3. docs/weekly-status-report-2026-06-10.md
4. TODO-kv-cache-benchmark-automation.md
5. docs/benchmark-pipelines.md
6. docs/superpowers/plans/2026-05-14-kv-cache-benchmark-automation.md
7. configs/models.yaml
8. configs/cache_methods.yaml
9. configs/benchmark.matrix.yaml

Current high-level plan:

1. Check git status and do not overwrite or revert user work.
2. Verify the harness still passes its focused tests.
3. Generate the environment report.
4. Generate the llama.cpp build report.
5. Locate or connect the experimental llama.cpp checkout.
6. Confirm one local GGUF model path.
7. Run one dry-run baseline benchmark with f16/f16.
8. Run one real f16/f16 smoke-test benchmark if the binary and model exist.
9. Try one compressed KV-cache method only after the baseline path works.
10. Save raw logs, parsed CSV rows, and a markdown report under results/.

Important constraints:

- Do not assume this repo itself is a llama.cpp checkout.
- The experimental llama.cpp source may need to live under tools/llama.cpp/.
- Do not clone or download anything without asking for approval.
- Do not commit GGUF model files, build output, or large benchmark results.
- Keep generated benchmark outputs under results/.
- Prefer the smallest smoke test first: ctx 2048, prompt 512, generation 128.
- Treat unsupported cache methods as expected experimental failures and record
  the reason instead of aborting the whole effort.
- If a compressed method fails, preserve the f16/f16 baseline result and report
  the compressed-method blocker clearly.

Useful commands to start with:

git status --short --branch

python -m pytest tests/test_benchmark_config.py tests/test_benchmark_manifest.py tests/test_benchmark_matrix.py tests/test_benchmark_report.py tests/test_environment_report.py tests/test_llamacpp_build.py tests/test_parse_llama_bench.py tests/test_run_benchmark_matrix.py tests/test_run_single_llama_bench.py --basetemp .pytest-tmp -p no:cacheprovider

.\scripts\setup\check-environment.ps1

.\scripts\setup\build-llamacpp.ps1 -Backend cuda -Profile release -FlashAttention

.\scripts\bench\run-single-llama-bench.ps1 -Backend cuda -Profile release -ModelId qwen_3b -ModelPath <local-gguf-path> -CtxSize 2048 -PromptTokens 512 -GenTokens 128 -CacheK f16 -CacheV f16 -GpuLayers 999 -FlashAttention -DryRun

After the dry run is correct and the executable/model path exists, run the same
single benchmark without -DryRun.

Expected first useful deliverable:

- results/raw/<run_id>.json
- results/parsed/performance.csv
- results/reports/benchmark-automation-report.md
- a short markdown note or report section summarizing whether the baseline run
  worked, what model/path was used, what context size was used, and what blocked
  any compressed-method attempt.

Current project reasoning:
The approved proposal asks for a compression evaluation, but the next practical
milestone is simpler: prove that the local benchmark harness can produce one
trustworthy baseline result. After that, compare one compressed KV-cache method
against the same model/context setup.
```

## Handoff Notes

At the time this handoff was created, the main planning files already existed
and the branch was `eval/kv-cache-benchmark-automation`, tracking
`origin/eval/kv-cache-benchmark-automation`.

The next session should start with a fresh `git status --short --branch`
because this file and related planning updates may be uncommitted.

## Primary Files

| Role                            | File                                                                   |
| ------------------------------- | ---------------------------------------------------------------------- |
| Approved project proposal       | `docs/llm_work_stack_rotoquant_evaluation_plan.md`                   |
| Course-facing weekly report     | `docs/weekly-status-report-2026-06-10.md`                            |
| Main active TODO/backlog        | `TODO-kv-cache-benchmark-automation.md`                              |
| Pipeline architecture map       | `docs/benchmark-pipelines.md`                                        |
| Implementation plan             | `docs/superpowers/plans/2026-05-14-kv-cache-benchmark-automation.md` |
| Model config                    | `configs/models.yaml`                                                |
| Cache-method config             | `configs/cache_methods.yaml`                                         |
| Benchmark matrix config         | `configs/benchmark.matrix.yaml`                                      |
| Single-run benchmark entrypoint | `scripts/bench/run-single-llama-bench.ps1`                           |
| Matrix benchmark entrypoint     | `scripts/bench/run-benchmark-matrix.ps1`                             |
| Environment report entrypoint   | `scripts/setup/check-environment.ps1`                                |
| Build planning entrypoint       | `scripts/setup/build-llamacpp.ps1`                                   |

## Immediate Success Criteria

The next session should count as successful if it can do at least this much:

1. Confirm the environment/build state in markdown reports.
2. Confirm one model path or clearly document that no local model path is ready.
3. Produce a dry-run command for the f16/f16 baseline.
4. If possible, run one actual f16/f16 baseline benchmark.
5. Save or update a short status note with the exact command, output files, and
   blockers.

Compressed KV-cache methods and GPU telemetry are important, but they should not
block recording the first baseline result.
