from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from benchmark_config import load_benchmark_matrix
from benchmark_matrix import expand_matrix_jobs


def make_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_expand_matrix_jobs_creates_cartesian_product_with_repetitions(tmp_path: Path) -> None:
    make_file(
        tmp_path,
        "configs/models.yaml",
        """
models:
  qwen_3b:
    name: Qwen 3B
    path: D:/models/qwen-3b-instruct.gguf
""".strip()
        + "\n",
    )
    make_file(
        tmp_path,
        "configs/cache_methods.yaml",
        """
cache_methods:
  - id: f16_f16
    cache_k: f16
    cache_v: f16
    category: baseline
""".strip()
        + "\n",
    )
    make_file(
        tmp_path,
        "configs/benchmark.matrix.yaml",
        """
context_sizes:
  - 2048
  - 4096
prompt_tokens:
  - 512
generation_tokens:
  - 128
gpu_layers:
  - 999
seed: 42
temperature: 0
repetitions:
  performance: 2
  accuracy: 1
""".strip()
        + "\n",
    )

    jobs = expand_matrix_jobs(tmp_path)

    assert len(jobs) == 4
    assert jobs[0]["model_id"] == "qwen_3b"
    assert jobs[0]["cache_k"] == "f16"
    assert jobs[0]["ctx_size"] == 2048
    assert {job["ctx_size"] for job in jobs} == {2048, 4096}


def test_expand_matrix_jobs_includes_cpu_and_cuda_backends(tmp_path: Path) -> None:
    make_file(
        tmp_path,
        "configs/models.yaml",
        """
models:
  qwen_3b:
    name: Qwen 3B
    path: D:/models/qwen-3b-instruct.gguf
""".strip()
        + "\n",
    )
    make_file(
        tmp_path,
        "configs/cache_methods.yaml",
        """
cache_methods:
  - id: f16_f16
    cache_k: f16
    cache_v: f16
    category: baseline
""".strip()
        + "\n",
    )
    make_file(
        tmp_path,
        "configs/benchmark.matrix.yaml",
        """
build_backends:
  - cpu
  - cuda
context_sizes:
  - 2048
prompt_tokens:
  - 512
generation_tokens:
  - 128
gpu_layers:
  - 999
flash_attention:
  - true
seed: 42
temperature: 0
repetitions:
  performance: 1
  accuracy: 1
""".strip()
        + "\n",
    )

    jobs = expand_matrix_jobs(tmp_path)

    assert {job["build_backend"] for job in jobs} == {"cpu", "cuda"}
    assert any(job["build_backend"] == "cuda" and job["flash_attention"] is True for job in jobs)
    assert any(job["build_backend"] == "cpu" and job["flash_attention"] is False for job in jobs)


def test_repo_benchmark_matrix_defaults_include_cpu_and_cuda() -> None:
    matrix = load_benchmark_matrix(ROOT / "configs" / "benchmark.matrix.yaml")

    assert matrix["build_profiles"] == [
        {"build_backend": "cpu", "flash_attention": False},
        {"build_backend": "cuda", "flash_attention": True},
    ]
