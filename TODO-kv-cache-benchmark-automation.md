# TODO — RotorQuant / PlanarQuant / IsoQuant KV Cache Benchmark Automation

**Project root:** `D:/dev/PRJ-rotorquant`  
**Primary goal:** automate compile, setup, benchmark execution, scoring, and reporting for experimental KV-cache compression methods against baseline llama.cpp KV cache formats.

> This document is intended to be pasted into a ChatGPT Codex VSCode extension session as the implementation TODO/spec.

---

## 0. Mission

Create a reproducible benchmark harness that compares:

1. **Compression efficiency**
   - KV cache size
   - compression ratio
   - peak VRAM / RAM
   - maximum context that fits

2. **Compute performance**
   - prefill tokens/sec
   - decode tokens/sec
   - time to first token
   - total runtime
   - GPU telemetry where available

3. **Context accuracy**
   - perplexity
   - needle-in-haystack recall
   - synthetic fact recall
   - output correctness
   - optional attention/KV fidelity if instrumentation is feasible

The benchmark must compare experimental cache types such as `planar3`, `iso3`, and `turbo3` against standard llama.cpp baselines such as `f16`, `q8_0`, and `q4_0`.

---

## 1. Working assumptions

- Local development root:

  ```text
  D:/dev/PRJ-rotorquant
  ```

- OS target:

  ```text
  Windows 11
  ```

- Preferred shell:

  ```text
  PowerShell 7+
  ```

- GPU target:

  ```text
  NVIDIA RTX-class GPU, CUDA capable
  ```

- The user has already forked the RotorQuant-related repo into their own GitHub account.
- The cloned repo may be one of:
  - the RotorQuant research repo
  - a llama.cpp fork with TurboQuant / PlanarQuant / IsoQuant support
  - a wrapper repo referencing a separate llama.cpp fork

The automation must detect what kind of repo is present and adapt.

---

## 2. Expected output structure

Create or normalize this project structure:

```text
D:/dev/PRJ-rotorquant/
  README.md
  TODO-kv-cache-benchmark.md
  .gitignore

  scripts/
    setup/
      bootstrap-windows.ps1
      check-environment.ps1
      install-python-env.ps1
      build-llamacpp.ps1

    bench/
      run-benchmark-matrix.ps1
      run-single-llama-bench.ps1
      run-single-perplexity.ps1
      run-single-needle.ps1
      collect-nvidia-smi.ps1

    python/
      run_matrix.py
      parse_llama_bench.py
      parse_perplexity.py
      score_needle.py
      score_fact_recall.py
      summarize_results.py
      make_charts.py
      environment_report.py

  configs/
    benchmark.matrix.yaml
    models.yaml
    cache_methods.yaml
    prompts.yaml
    hardware.local.yaml

  prompts/
    sanity/
      basic_qa_001.txt
      summarization_001.txt

    needle/
      needle_4k.txt
      needle_8k.txt
      needle_16k.txt
      needle_32k.txt

    facts/
      facts_4k.jsonl
      facts_8k.jsonl
      facts_16k.jsonl

    realistic/
      technical_context_001.txt

  tools/
    llama.cpp/
      # optional local clone or submodule of experimental llama.cpp fork

  models/
    README.md
    # models are not committed

  results/
    raw/
    telemetry/
    parsed/
    charts/
    reports/

  reports/
    benchmark-summary.md
```

---

## 3. Repository detection TODO

Implement a script that inspects the repo and reports what it is.

### TODO

- [ ] In `scripts/python/environment_report.py`, inspect:
  - repo remote URL
  - active branch
  - commit SHA
  - whether this root contains `CMakeLists.txt`
  - whether this root contains `llama.cpp` source files
  - whether this root contains `turboquant/`
  - whether this root contains RotorQuant Python files
  - whether this root supports llama.cpp executable builds directly

### Detection rules

- [ ] If root contains `examples/`, `tools/`, `src/llama.cpp`, `ggml/`, and `CMakeLists.txt`, treat it as a llama.cpp-style repo.
- [ ] If root contains `turboquant/rotorquant.py`, treat it as the RotorQuant research repo.
- [ ] If root is RotorQuant research repo only, create `tools/llama.cpp/` and clone/build the experimental llama.cpp fork there.
- [ ] Do not overwrite user work.
- [ ] Write a clear environment report to:

  ```text
  results/reports/environment-report.md
  ```

---

## 4. Environment setup TODO

Create a Windows PowerShell bootstrap that checks and installs only what is missing.

### Required tools

- [ ] Git
- [ ] CMake
- [ ] Ninja
- [ ] Visual Studio Build Tools / MSVC compiler
- [ ] Python 3.11 or newer
- [ ] CUDA Toolkit, if NVIDIA GPU build is requested
- [ ] NVIDIA driver
- [ ] `nvidia-smi`
- [ ] PowerShell 7+

### Script

Create:

```text
scripts/setup/bootstrap-windows.ps1
```

### Script behavior

- [ ] Print system summary.
- [ ] Verify PowerShell version.
- [ ] Verify Git.
- [ ] Verify Python.
- [ ] Verify CMake.
- [ ] Verify Ninja.
- [ ] Verify MSVC compiler availability.
- [ ] Verify CUDA availability using:
  - `nvcc --version`
  - `nvidia-smi`
- [ ] Create Python virtual environment:

  ```text
  .venv/
  ```

- [ ] Install Python packages:

  ```text
  pandas
  numpy
  pyyaml
  matplotlib
  tqdm
  rich
  jsonlines
  psutil
  ```

- [ ] Optionally install PyTorch only if RotorQuant research scripts require it.
- [ ] Do not install large dependencies without a clear prompt comment in the script.
- [ ] Save dependency versions to:

  ```text
  results/reports/python-freeze.txt
  ```

---

## 5. Build automation TODO

Create:

```text
scripts/setup/build-llamacpp.ps1
```

### Build modes

Support these build profiles:

```text
cpu
cuda
cuda-fa
debug
release
```

### Expected build directories

```text
build/cpu-release
build/cuda-release
build/cuda-fa-release
build/debug
```

### CUDA build candidate

Use a command pattern like this, adapting to the repo’s actual CMake options:

```powershell
cmake -S . -B build/cuda-release -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DGGML_CUDA=ON

cmake --build build/cuda-release --config Release -j
```

If Flash Attention is supported by the fork, add a separate profile:

```powershell
cmake -S . -B build/cuda-fa-release -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DGGML_CUDA=ON `
  -DGGML_CUDA_FA=ON
```

### TODO

- [ ] Detect actual llama.cpp source directory:
  - repo root, or
  - `tools/llama.cpp/`
- [ ] Configure build.
- [ ] Build.
- [ ] Locate built executables:
  - `llama-cli`
  - `llama-server`
  - `llama-bench`
  - `llama-perplexity`
- [ ] Save executable paths to:

  ```text
  configs/local.executables.json
  ```

- [ ] Run smoke test:

  ```powershell
  llama-bench --help
  ```

- [ ] Detect available cache types if possible.
- [ ] Fail clearly if experimental cache types are not registered.

---

## 6. Model management TODO

Create:

```text
models/README.md
configs/models.yaml
```

### TODO

- [ ] Do not commit GGUF model files.
- [ ] Add placeholder model path entries.
- [ ] Support local model paths such as:

  ```yaml
  models:
    qwen_3b:
      name: "Qwen 2.5/3B Instruct GGUF"
      path: "D:/models/qwen-3b-instruct.gguf"
      expected_ctx: 32768
      notes: "Small validation model"

    llama_8b:
      name: "Llama 3.1/3.2 8B Instruct GGUF"
      path: "D:/models/llama-8b-instruct.gguf"
      expected_ctx: 32768
      notes: "Practical local benchmark model"
  ```

- [ ] Add SHA256 calculation for model files.
- [ ] Include model hash in every result row.
- [ ] Validate model exists before running benchmark matrix.
- [ ] Skip unavailable models but record skip reason.

---

## 7. Cache method matrix TODO

Create:

```text
configs/cache_methods.yaml
```

Start with:

```yaml
cache_methods:
  - id: f16_f16
    cache_k: f16
    cache_v: f16
    category: baseline
    description: "Standard FP16 KV cache baseline"

  - id: q8_q8
    cache_k: q8_0
    cache_v: q8_0
    category: baseline
    description: "Existing llama.cpp Q8 KV cache"

  - id: q4_q4
    cache_k: q4_0
    cache_v: q4_0
    category: baseline
    description: "Existing llama.cpp Q4 KV cache"

  - id: turbo3_turbo3
    cache_k: turbo3
    cache_v: turbo3
    category: experimental
    description: "TurboQuant 3-bit K/V, if supported by fork"

  - id: planar3_planar3
    cache_k: planar3
    cache_v: planar3
    category: experimental
    description: "PlanarQuant 3-bit K/V, if supported by fork"

  - id: iso3_iso3
    cache_k: iso3
    cache_v: iso3
    category: experimental
    description: "IsoQuant 3-bit K/V, if supported by fork"

  - id: planar3_f16
    cache_k: planar3
    cache_v: f16
    category: asymmetric
    description: "Compressed K with FP16 V, if supported"

  - id: f16_planar3
    cache_k: f16
    cache_v: planar3
    category: asymmetric
    description: "FP16 K with compressed V, if supported"

  - id: q8_planar3
    cache_k: q8_0
    cache_v: planar3
    category: asymmetric
    description: "Q8 K with Planar V, if supported"
```

### TODO

- [ ] Implement cache-type support detection.
- [ ] If a cache type fails with “invalid value” or equivalent, mark method unsupported and continue.
- [ ] Do not abort the whole benchmark matrix because one experimental type is unavailable.

---

## 8. Benchmark matrix TODO

Create:

```text
configs/benchmark.matrix.yaml
```

Initial conservative matrix:

```yaml
context_sizes:
  - 2048
  - 4096
  - 8192
  - 16384

generation_tokens:
  - 256

prompt_tokens:
  - 512
  - 2048
  - 4096

gpu_layers:
  - 999

flash_attention:
  - true

threads:
  - auto

seed: 42
temperature: 0

repetitions:
  performance: 3
  accuracy: 1
```

### TODO

- [ ] Keep the first matrix small enough to run on RTX 3070-class hardware.
- [ ] Add a `--dry-run` mode.
- [ ] Add a `--quick` mode.
- [ ] Add a `--full` mode.
- [ ] Add resume support so completed runs are skipped.
- [ ] Add per-run timeout.
- [ ] Record failed runs with reason.

---

## 9. Performance benchmark TODO

Create:

```text
scripts/python/run_matrix.py
scripts/python/parse_llama_bench.py
scripts/bench/run-single-llama-bench.ps1
```

### Run target

Use `llama-bench` when available.

Candidate command pattern:

```powershell
& $LlamaBench `
  -m $ModelPath `
  -p $PromptTokens `
  -n $GenTokens `
  -c $ContextSize `
  -ngl $GpuLayers `
  -ctk $CacheTypeK `
  -ctv $CacheTypeV
```

If the fork uses long flags:

```powershell
& $LlamaBench `
  -m $ModelPath `
  -p $PromptTokens `
  -n $GenTokens `
  -c $ContextSize `
  -ngl $GpuLayers `
  --cache-type-k $CacheTypeK `
  --cache-type-v $CacheTypeV
```

### TODO

- [ ] Detect whether short flags `-ctk` / `-ctv` are supported.
- [ ] Fall back to long flags if needed.
- [ ] Capture stdout.
- [ ] Capture stderr.
- [ ] Parse prefill tok/s.
- [ ] Parse decode tok/s.
- [ ] Parse total time if available.
- [ ] Include executable version and commit if available.
- [ ] Write raw logs to:

  ```text
  results/raw/
  ```

- [ ] Write parsed rows to:

  ```text
  results/parsed/performance.csv
  ```

---

## 10. GPU telemetry TODO

Create:

```text
scripts/bench/collect-nvidia-smi.ps1
```

### TODO

- [ ] Start telemetry collection before each benchmark run.
- [ ] Poll `nvidia-smi` every 1 second.
- [ ] Capture:
  - timestamp
  - GPU name
  - driver version
  - utilization
  - memory used
  - memory total
  - power draw
  - temperature
- [ ] Save telemetry to:

  ```text
  results/telemetry/{run_id}.csv
  ```

Candidate command:

```powershell
nvidia-smi `
  --query-gpu=timestamp,name,driver_version,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu `
  --format=csv
```

---

## 11. Perplexity benchmark TODO

Create:

```text
scripts/bench/run-single-perplexity.ps1
scripts/python/parse_perplexity.py
```

### TODO

- [ ] Locate `llama-perplexity`.
- [ ] Add a small text corpus file under:

  ```text
  prompts/perplexity/wikitext_small.txt
  ```

- [ ] Allow user to provide a larger local corpus.
- [ ] Run perplexity for each cache method.
- [ ] Use the same context size and model across methods.
- [ ] Parse final PPL.
- [ ] Write:

  ```text
  results/parsed/perplexity.csv
  ```

### Candidate command pattern

```powershell
& $LlamaPerplexity `
  -m $ModelPath `
  -f $CorpusPath `
  -c $ContextSize `
  -ngl $GpuLayers `
  --cache-type-k $CacheTypeK `
  --cache-type-v $CacheTypeV
```

---

## 12. Needle-in-haystack accuracy TODO

Create:

```text
scripts/bench/run-single-needle.ps1
scripts/python/score_needle.py
```

### Prompt generation

Create synthetic prompt files with a known hidden value:

```text
The secret calibration phrase is: maple-iron-739.
```

Generate variants where the needle appears at:

```text
10%
25%
50%
75%
90%
```

of the context.

### TODO

- [ ] Generate filler text deterministically.
- [ ] Insert needle phrase at controlled positions.
- [ ] Ask final question:

  ```text
  What is the secret calibration phrase?
  ```

- [ ] Run with deterministic decoding:
  - temperature `0`
  - fixed seed `42`
- [ ] Score:
  - exact match
  - contains phrase
  - normalized edit distance
  - failure reason
- [ ] Write:

  ```text
  results/parsed/needle.csv
  ```

---

## 13. Synthetic fact recall TODO

Create:

```text
scripts/python/score_fact_recall.py
prompts/facts/
```

### Dataset format

Use JSONL:

```json
{"id":"fact_001","fact":"The access code for Blue Falcon is 71842.","question":"What is the access code for Blue Falcon?","answer":"71842"}
{"id":"fact_002","fact":"The maintenance window for Delta Relay is Tuesday 03:15.","question":"What is the maintenance window for Delta Relay?","answer":"Tuesday 03:15"}
```

### TODO

- [ ] Generate fact sets for:
  - 4K
  - 8K
  - 16K
  - 32K, if possible
- [ ] Place facts at known positions.
- [ ] Ask questions at the end of the context.
- [ ] Score exact answer presence.
- [ ] Score per-position accuracy.
- [ ] Write:

  ```text
  results/parsed/fact_recall.csv
  ```

---

## 14. Optional direct KV / attention fidelity TODO

This is advanced and optional.

### Goal

Compare original K/V tensors against compressed/decompressed K/V tensors.

### TODO

- [ ] Check whether fork exposes a debugging or dump option for K/V cache.
- [ ] If not available, do not block the main benchmark.
- [ ] Consider adding instrumentation only after basic harness works.
- [ ] Metrics:
  - K cosine similarity
  - V cosine similarity
  - per-layer similarity
  - per-head similarity
  - attention top-1 match
  - attention top-5 overlap
  - attention distribution KL divergence
- [ ] Write:

  ```text
  results/parsed/kv_fidelity.csv
  ```

---

## 15. Result schema TODO

Create a unified CSV:

```text
results/parsed/all_runs.csv
```

Required columns:

```csv
run_id,timestamp,host,os,gpu,driver,cuda_version,repo_url,branch,commit,build_profile,executable,model_id,model_path,model_sha256,ctx_size,prompt_tokens,gen_tokens,cache_k,cache_v,flash_attention,gpu_layers,seed,temp,status,error,peak_vram_mb,prefill_tps,decode_tps,total_time_ms,time_to_first_token_ms,ppl,needle_exact,needle_contains,fact_accuracy,notes
```

### TODO

- [ ] Every script must emit enough metadata to populate this schema.
- [ ] Failed runs must still produce a row.
- [ ] Unsupported cache methods must be marked as:

  ```text
  status=unsupported
  ```

- [ ] Out-of-memory failures must be marked as:

  ```text
  status=oom
  ```

---

## 16. Charts and reports TODO

Create:

```text
scripts/python/make_charts.py
scripts/python/summarize_results.py
reports/benchmark-summary.md
```

### Charts

Generate one chart per output PNG:

```text
results/charts/decode_tps_by_cache.png
results/charts/prefill_tps_by_cache.png
results/charts/peak_vram_by_context.png
results/charts/perplexity_by_cache.png
results/charts/needle_accuracy_by_context.png
results/charts/compression_vs_accuracy.png
```

### Report sections

```markdown
# KV Cache Compression Benchmark Summary

## Environment

## Models

## Cache methods tested

## Unsupported methods

## Performance results

## Memory results

## Perplexity results

## Needle-in-haystack results

## Fact recall results

## Best tradeoffs

## Known caveats

## Raw result files
```

### TODO

- [ ] Include tables sorted by:
  - best decode speed
  - lowest VRAM
  - best perplexity
  - best long-context recall
  - best balanced score
- [ ] Include caveat for experimental forks and possible implementation anomalies.
- [ ] Do not claim experimental methods are better unless local measurements support that.

---

## 17. Balanced scoring TODO

Create a simple ranking score, but keep raw metrics visible.

### Suggested formula

```text
decode_retention = method_decode_tps / f16_decode_tps
accuracy_retention = method_accuracy / f16_accuracy
ppl_retention = f16_ppl / method_ppl
memory_gain = f16_peak_vram_mb / method_peak_vram_mb

balanced_score =
  memory_gain
  * decode_retention
  * accuracy_retention
  * ppl_retention
```

### TODO

- [ ] Compute score only when all required metrics are available.
- [ ] Do not compute score for failed or unsupported runs.
- [ ] Report missing metrics clearly.
- [ ] Keep this score secondary to raw measurements.

---

## 18. Validation checks TODO

Before trusting results:

- [ ] Confirm same model SHA256 across all methods.
- [ ] Confirm same prompt tokens across methods.
- [ ] Confirm deterministic seed and temperature.
- [ ] Confirm same build profile.
- [ ] Confirm same GPU layer count.
- [ ] Confirm same context size.
- [ ] Confirm no other major GPU workload is running.
- [ ] Repeat performance runs at least 3 times.
- [ ] Report median, min, max.
- [ ] Compare against f16 and q8 baselines before comparing experimental methods.

---

## 19. Known external caveats to encode into the benchmark notes

The benchmark must explicitly watch for these issues:

- Experimental cache types may not exist in upstream llama.cpp.
- Some reported cache types may allocate more K-cache memory than expected.
- Some implementations may quantize/dequantize at attention time instead of write time.
- Some methods may improve perplexity but hurt throughput.
- Some methods may behave differently by model architecture, head dimension, GPU backend, and FlashAttention support.
- Repo-reported benchmark claims must be reproduced locally before trusting them.
- Open GitHub issues may exist for high graph splits, GPU-specific slowdowns, or unsupported model architectures.

---

## 20. First milestone: quick local smoke test

Implement this first before the full matrix.

### TODO

- [ ] Detect the repository shape and write `results/reports/environment-report.md`.
- [ ] If the root is RotorQuant research-only, report that `tools/llama.cpp/` is still missing and stop the smoke test cleanly until the experimental fork is available.
- [ ] Locate the experimental `llama.cpp` checkout at the repo root or under `tools/llama.cpp/`.
- [ ] Write a build report that clearly says when the experimental fork is missing instead of failing cryptically.
- [ ] Detect missing build tools (`cmake`, `ninja`, `cl`) before trying to compile.
- [ ] Build experimental llama.cpp fork successfully.
- [ ] Confirm `llama-bench` runs.
- [ ] Run one model with:

  ```text
  ctx_size = 2048
  prompt_tokens = 512
  gen_tokens = 128
  ```

- [ ] Test these methods:

  ```text
  f16/f16
  q8_0/q8_0
  q4_0/q4_0
  planar3/planar3
  iso3/iso3
  turbo3/turbo3
  ```

- [ ] Write raw logs.
- [ ] Write parsed CSV.
- [ ] Generate first summary table.

---

## 21. Second milestone: accuracy harness

### TODO

- [ ] Generate 4K and 8K needle prompts.
- [ ] Run deterministic generation with each supported cache method.
- [ ] Score exact match.
- [ ] Generate fact recall prompts.
- [ ] Score fact recall.
- [ ] Add results to summary report.

---

## 22. Third milestone: larger context scaling

### TODO

- [ ] Run context sizes:

  ```text
  2K
  4K
  8K
  16K
  32K
  ```

- [ ] Stop at first OOM per method/model unless `--continue-after-oom` is set.
- [ ] Chart peak VRAM by context size.
- [ ] Chart accuracy by context size.
- [ ] Identify maximum usable context per cache method.

---

## 23. Codex implementation prompt

Paste the following into Codex after opening this repo in VSCode:

```text
You are working in my local repo at D:/dev/PRJ-rotorquant.

Implement the TODO-kv-cache-benchmark.md plan.

Primary objective:
Create a reproducible Windows/PowerShell + Python benchmark harness that can compile the local RotorQuant / llama.cpp experimental repo, detect supported KV-cache compression types, run performance and accuracy benchmarks, collect GPU telemetry, parse results, and generate a Markdown benchmark report.

Do not assume this repo is directly buildable as llama.cpp. First inspect the repo structure. If this repo is the RotorQuant research repo and not a llama.cpp fork, create a tools/llama.cpp/ directory and add setup logic that can clone or use the experimental llama.cpp fork specified by the repo README. Do not overwrite existing files or user work.

Implement in phases:
1. Environment/reporting scripts.
2. Build scripts.
3. Config YAML files.
4. Performance benchmark runner using llama-bench.
5. GPU telemetry using nvidia-smi.
6. Needle-in-haystack and fact-recall prompt generation/scoring.
7. Perplexity runner if llama-perplexity is available.
8. Result parsing into CSV.
9. Markdown report generation and charts.

Use defensive coding:
- support dry-run mode
- support quick mode
- skip unsupported cache methods instead of crashing
- record failed runs with reason
- keep raw logs
- keep all generated files under results/
- do not commit models or build artifacts

Target machine:
Windows 11, CUDA-capable NVIDIA GPU, development root D:/dev/PRJ-rotorquant.

Initial cache methods:
f16/f16, q8_0/q8_0, q4_0/q4_0, turbo3/turbo3, planar3/planar3, iso3/iso3, planar3/f16, f16/planar3.

Initial contexts:
2048, 4096, 8192, 16384.

Initial generation:
prompt tokens 512 and 2048, generation tokens 256, seed 42, temperature 0.

Create a first working smoke test before expanding the full benchmark matrix.
```

---

## 24. Definition of done

The task is done when:

- [ ] `scripts/setup/bootstrap-windows.ps1` runs successfully.
- [ ] `scripts/setup/build-llamacpp.ps1` builds or clearly reports why it cannot.
- [ ] Supported cache methods are detected.
- [ ] A quick benchmark matrix runs without manual intervention.
- [ ] Raw logs are saved.
- [ ] GPU telemetry is saved.
- [ ] Parsed CSV files are generated.
- [ ] At least one Markdown report is generated.
- [ ] Unsupported experimental cache types are skipped safely.
- [ ] The report clearly compares:
  - f16
  - q8_0
  - q4_0
  - supported experimental methods
- [ ] No model files, build artifacts, or huge result files are committed accidentally.
