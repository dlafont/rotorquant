from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

import run_single_llama_bench as runner
from run_single_llama_bench import (
    build_command,
    find_llama_bench_executable,
    run_single_benchmark,
    summarize_run,
)


def test_build_command_uses_short_cache_flags_when_requested() -> None:
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

    assert "-o" in cmd
    assert "json" in cmd
    assert "-r" in cmd
    assert "-ctk" in cmd
    assert "-ctv" in cmd


def test_summarize_run_marks_dry_run() -> None:
    row = summarize_run(run_id="abc123", status="skipped", notes="dry-run")

    assert row["run_id"] == "abc123"
    assert row["status"] == "skipped"
    assert row["notes"] == "dry-run"


def test_find_llama_bench_executable_prefers_existing_build_tree(tmp_path: Path) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)
    executable = tmp_path / "tools" / "llama.cpp" / "build-x64-windows-msvc-release" / "bin" / "llama-bench.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_text("binary", encoding="utf-8")

    found = find_llama_bench_executable(tmp_path, "cpu", "release")

    assert found == executable


def test_find_llama_bench_executable_prefers_backend_specific_build_tree(tmp_path: Path) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)
    executable = source_root / "build" / "cuda-release" / "bin" / "llama-bench.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_text("binary", encoding="utf-8")

    found = find_llama_bench_executable(tmp_path, "cuda", "release")

    assert found == executable


def test_build_command_adds_flash_attention_flag_for_cuda_runs() -> None:
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
        flash_attention=True,
    )

    assert "-fa" in cmd
    assert "1" in cmd


def test_run_single_benchmark_skips_when_model_is_missing(tmp_path: Path) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / "models" / "missing.gguf"

    row = run_single_benchmark(
        root=tmp_path,
        build_profile="release",
        build_backend="cuda",
        model_id="qwen_3b",
        model_path=model_path,
        ctx_size=2048,
        prompt_tokens=512,
        gen_tokens=128,
        cache_k="f16",
        cache_v="f16",
        gpu_layers=999,
        flash_attention=True,
        short_cache_flags=False,
        dry_run=False,
    )

    assert row["status"] == "skipped"
    assert "missing model" in row["notes"]
    assert row["build_backend"] == "cuda"


def test_run_single_benchmark_writes_raw_and_parsed_outputs(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)
    executable = source_root / "build-x64-windows-msvc-release" / "bin" / "llama-bench.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_text("binary", encoding="utf-8")
    model_path = tmp_path / "models" / "model.gguf"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text("model", encoding="utf-8")

    sample_output = """
[
  {
    "build_commit": "8cf427ff",
    "build_number": 5163,
    "model_filename": "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    "model_type": "qwen2 7B Q4_K - Medium",
    "n_prompt": 512,
    "n_gen": 0,
    "n_depth": 0,
    "avg_ns": 72135640,
    "stddev_ns": 1453752,
    "avg_ts": 7100.002165,
    "stddev_ts": 140.341520
  },
  {
    "build_commit": "8cf427ff",
    "build_number": 5163,
    "model_filename": "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    "model_type": "qwen2 7B Q4_K - Medium",
    "n_prompt": 0,
    "n_gen": 128,
    "n_depth": 0,
    "avg_ns": 1067431600,
    "stddev_ns": 3834831,
    "avg_ts": 119.915244,
    "stddev_ts": 0.430617
  }
]
""".strip()

    class Completed:
        returncode = 0
        stdout = sample_output
        stderr = ""

    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: Completed())

    row = run_single_benchmark(
        root=tmp_path,
        build_profile="release",
        build_backend="cuda",
        model_id="qwen_3b",
        model_path=model_path,
        ctx_size=2048,
        prompt_tokens=512,
        gen_tokens=128,
        cache_k="f16",
        cache_v="f16",
        gpu_layers=999,
        flash_attention=True,
        short_cache_flags=False,
        repetitions=1,
        dry_run=False,
    )

    assert row["status"] == "passed"
    assert row["prefill_tps"] == "7100.002165"
    assert row["decode_tps"] == "119.915244"
    assert "-fa" in row["command"]
    assert Path(row["raw_output"]).exists()
    assert (tmp_path / "results" / "parsed" / "performance.csv").exists()
