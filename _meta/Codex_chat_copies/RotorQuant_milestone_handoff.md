# RotorQuant Milestone Handoff

Use this as the paste-in context for a fresh Codex chat.

## Goal
Build a Windows benchmark harness for RotorQuant / PlanarQuant / IsoQuant KV-cache methods against llama.cpp baselines, then run smoke benchmarks and report results.

## Current Branch / Repo State
- Working branch: `eval/kv-cache-benchmark-automation`
- Repo is a RotorQuant research checkout, not a direct llama.cpp tree
- Experimental fork cloned into `tools/llama.cpp/`
- `git config --global --add safe.directory D:/Dev/PRJ-rotorquant/tools/llama.cpp` was set so Git commands work on the cloned fork

## What We Already Finished
- Environment report script added: `scripts/python/environment_report.py`
- PowerShell entry point added: `scripts/setup/check-environment.ps1`
- Build report / source-root helper added: `scripts/python/llamacpp_build.py`
- PowerShell build report entry point added: `scripts/setup/build-llamacpp.ps1`
- Tests added and passing for both helpers
- TODO updated so the smoke-test milestone starts with environment detection, source-root detection, and build-tool detection

## Toolchain Installed
- Visual Studio 2022 Build Tools
- MSVC C++ workload
- CMake tools
- Ninja
- Clang / LLVM toolset support
- Windows 11 SDK

## Verified Smoke-Test Results
- `cmake --preset x64-windows-msvc-release` succeeded in the Visual Studio developer shell
- `cmake --build build-x64-windows-msvc-release --config Release --target llama-bench -j 8` succeeded
- `build-x64-windows-msvc-release\bin\llama-bench.exe --help` succeeded

## Important Paths
- Repo README direction: clone `johndpope/llama-cpp-turboquant` and use `feature/planarquant-kv-cache`
- Build report: `results/reports/llamacpp-build-report.md`
- Environment report: `results/reports/environment-report.md`
- Built binary: `tools/llama.cpp/build-x64-windows-msvc-release/bin/llama-bench.exe`

## Notes
- Plain shell PATH does not show `cmake`, `ninja`, or `cl`, but they are available through the Visual Studio developer shell and were found by the build report helper.
- The current build is MSVC/Ninja CPU-only smoke validation. CUDA Toolkit has not been installed yet.
- OpenSSL is missing, so llama.cpp configure warned that HTTPS support is disabled, but the configure and build still completed.

## Suggested Next Step
Decide whether to:
- install CUDA Toolkit and enable `GGML_CUDA=ON`, or
- start wiring the benchmark automation scripts to run real model tests now that the toolchain is proven.
