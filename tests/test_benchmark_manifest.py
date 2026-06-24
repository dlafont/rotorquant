from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from benchmark_manifest import (
    BenchmarkRunRequest,
    default_run_id,
    resolve_source_root,
)


def make_file(root: Path, relative_path: str, content: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_resolve_source_root_prefers_tools_llama_cpp(tmp_path: Path) -> None:
    make_file(tmp_path, "tools/llama.cpp/CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "tools/llama.cpp/examples/main.cpp", "// example\n")
    make_file(tmp_path, "tools/llama.cpp/ggml/README.md", "ggml\n")
    make_file(tmp_path, "tools/llama.cpp/src/llama.cpp/CMakeLists.txt", "project(llama)\n")

    assert resolve_source_root(tmp_path) == tmp_path / "tools" / "llama.cpp"


def test_resolve_source_root_raises_clear_error_when_missing_checkout(tmp_path: Path) -> None:
    try:
        resolve_source_root(tmp_path)
    except FileNotFoundError as exc:
        assert "llama.cpp" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")


def test_default_run_id_is_stable_for_identical_inputs() -> None:
    a = default_run_id("release", "llama-bench", "model_a", 2048, 512, 128, "f16", "f16")
    b = default_run_id("release", "llama-bench", "model_a", 2048, 512, 128, "f16", "f16")

    assert a == b


def test_default_run_id_differs_for_cpu_and_cuda_build_backends() -> None:
    cpu = default_run_id(
        "release",
        "llama-bench",
        "model_a",
        2048,
        512,
        128,
        "f16",
        "f16",
        build_backend="cpu",
    )
    cuda = default_run_id(
        "release",
        "llama-bench",
        "model_a",
        2048,
        512,
        128,
        "f16",
        "f16",
        build_backend="cuda",
    )

    assert cpu != cuda


def test_benchmark_run_request_retains_optional_cuda_flag() -> None:
    request = BenchmarkRunRequest(
        build_profile="release",
        build_backend="cuda",
        model_id="model_a",
        model_path=Path("D:/models/model.gguf"),
        ctx_size=2048,
        prompt_tokens=512,
        gen_tokens=128,
        cache_k="f16",
        cache_v="f16",
        enable_cuda=False,
    )

    assert request.build_backend == "cuda"
    assert request.enable_cuda is False
