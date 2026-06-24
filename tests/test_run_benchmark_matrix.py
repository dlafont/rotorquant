from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

import run_benchmark_matrix


def test_run_matrix_executes_each_job_once(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)

    jobs = [
        {
            "model_id": "qwen_3b",
            "model_path": "D:/models/qwen-3b-instruct.gguf",
            "cache_id": "f16_f16",
            "cache_k": "f16",
            "cache_v": "f16",
            "build_backend": "cuda",
            "flash_attention": True,
            "ctx_size": 2048,
            "prompt_tokens": 512,
            "gen_tokens": 128,
            "gpu_layers": 999,
            "repetition": 1,
            "seed": 42,
            "temperature": 0,
        }
    ]
    seen = []

    monkeypatch.setattr(run_benchmark_matrix, "expand_matrix_jobs", lambda root: jobs)
    monkeypatch.setattr(
        run_benchmark_matrix,
        "run_single_benchmark",
        lambda **kwargs: seen.append(kwargs) or {"run_id": "abc123", "status": "skipped", "notes": "dry-run"},
    )
    monkeypatch.setattr(
        run_benchmark_matrix,
        "write_benchmark_report",
        lambda **kwargs: tmp_path / "results" / "reports" / "benchmark-automation-report.md",
    )

    rows = run_benchmark_matrix.run_matrix(
        root=tmp_path,
        build_profile="release",
        dry_run=True,
    )

    assert len(rows) == 1
    assert len(seen) == 1
    assert seen[0]["model_id"] == "qwen_3b"
    assert seen[0]["build_backend"] == "cuda"


def test_run_matrix_quick_mode_limits_to_first_job(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "tools" / "llama.cpp"
    (source_root / "CMakeLists.txt").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")
    (source_root / "examples").mkdir(parents=True, exist_ok=True)
    (source_root / "ggml").mkdir(parents=True, exist_ok=True)
    (source_root / "src" / "llama.cpp").mkdir(parents=True, exist_ok=True)

    jobs = [
        {
            "model_id": "qwen_3b",
            "model_path": "D:/models/qwen-3b-instruct.gguf",
            "cache_id": "f16_f16",
            "cache_k": "f16",
            "cache_v": "f16",
            "build_backend": "cpu",
            "flash_attention": False,
            "ctx_size": 2048,
            "prompt_tokens": 512,
            "gen_tokens": 128,
            "gpu_layers": 999,
            "repetition": 1,
            "seed": 42,
            "temperature": 0,
        },
        {
            "model_id": "qwen_3b",
            "model_path": "D:/models/qwen-3b-instruct.gguf",
            "cache_id": "f16_f16",
            "cache_k": "f16",
            "cache_v": "f16",
            "build_backend": "cpu",
            "flash_attention": False,
            "ctx_size": 4096,
            "prompt_tokens": 512,
            "gen_tokens": 128,
            "gpu_layers": 999,
            "repetition": 1,
            "seed": 42,
            "temperature": 0,
        },
    ]
    seen = []

    monkeypatch.setattr(run_benchmark_matrix, "expand_matrix_jobs", lambda root: jobs)
    monkeypatch.setattr(
        run_benchmark_matrix,
        "run_single_benchmark",
        lambda **kwargs: seen.append(kwargs) or {"run_id": "abc123", "status": "skipped", "notes": "dry-run"},
    )
    monkeypatch.setattr(
        run_benchmark_matrix,
        "write_benchmark_report",
        lambda **kwargs: tmp_path / "results" / "reports" / "benchmark-automation-report.md",
    )

    rows = run_benchmark_matrix.run_matrix(
        root=tmp_path,
        build_profile="release",
        dry_run=True,
        quick=True,
    )

    assert len(rows) == 1
    assert len(seen) == 1
    assert seen[0]["ctx_size"] == 2048
