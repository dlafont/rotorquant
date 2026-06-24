from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from benchmark_config import load_benchmark_matrix, load_cache_methods, load_models


def make_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_load_models_reads_enabled_model_entries(tmp_path: Path) -> None:
    config = make_file(
        tmp_path,
        "models.yaml",
        """
models:
  qwen_3b:
    name: Qwen 3B
    path: D:/models/qwen-3b-instruct.gguf
    expected_ctx: 32768
    notes: Small validation model
""".strip()
        + "\n",
    )

    models = load_models(config)

    assert len(models) == 1
    assert models[0]["model_id"] == "qwen_3b"
    assert models[0]["path"] == "D:/models/qwen-3b-instruct.gguf"


def test_load_cache_methods_reads_baseline_entries(tmp_path: Path) -> None:
    config = make_file(
        tmp_path,
        "cache_methods.yaml",
        """
cache_methods:
  - id: f16_f16
    cache_k: f16
    cache_v: f16
    category: baseline
    description: Standard FP16 KV cache baseline
""".strip()
        + "\n",
    )

    methods = load_cache_methods(config)

    assert len(methods) == 1
    assert methods[0]["id"] == "f16_f16"
    assert methods[0]["cache_k"] == "f16"


def test_load_benchmark_matrix_reads_repetition_settings(tmp_path: Path) -> None:
    config = make_file(
        tmp_path,
        "benchmark.matrix.yaml",
        """
context_sizes:
  - 2048
prompt_tokens:
  - 512
generation_tokens:
  - 128
gpu_layers:
  - 999
seed: 42
temperature: 0
repetitions:
  performance: 3
  accuracy: 1
""".strip()
        + "\n",
    )

    matrix = load_benchmark_matrix(config)

    assert matrix["seed"] == 42
    assert matrix["repetitions"]["performance"] == 3
