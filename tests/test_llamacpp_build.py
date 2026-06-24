from pathlib import Path
import sys
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

import llamacpp_build
from llamacpp_build import (
    build_llama_cpp_report,
    detect_cuda_toolchain,
    detect_llama_cpp_source_root,
)


def make_file(root: Path, relative_path: str, content: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detects_source_root_in_tools_directory(tmp_path):
    make_file(tmp_path, "tools/llama.cpp/CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "tools/llama.cpp/examples/main.cpp", "// example\n")
    make_file(tmp_path, "tools/llama.cpp/ggml/README.md", "ggml\n")
    make_file(tmp_path, "tools/llama.cpp/src/llama.cpp/CMakeLists.txt", "project(llama)\n")

    assert detect_llama_cpp_source_root(tmp_path) == tmp_path / "tools/llama.cpp"


def test_detects_source_root_at_repo_root(tmp_path):
    make_file(tmp_path, "CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "examples/main.cpp", "// example\n")
    make_file(tmp_path, "ggml/README.md", "ggml\n")
    make_file(tmp_path, "src/llama.cpp/CMakeLists.txt", "project(llama)\n")

    assert detect_llama_cpp_source_root(tmp_path) == tmp_path


def test_build_report_flags_missing_llama_cpp_checkout(tmp_path):
    report = build_llama_cpp_report(tmp_path)

    assert "missing" in report.lower()
    assert "tools/llama.cpp/" in report


def test_build_report_lists_missing_tools(tmp_path, monkeypatch):
    make_file(tmp_path, "tools/llama.cpp/CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "tools/llama.cpp/examples/main.cpp", "// example\n")
    make_file(tmp_path, "tools/llama.cpp/ggml/README.md", "ggml\n")
    make_file(tmp_path, "tools/llama.cpp/src/llama.cpp/CMakeLists.txt", "project(llama)\n")

    monkeypatch.setattr(shutil, "which", lambda name: None)
    monkeypatch.setattr(llamacpp_build, "_find_vs_installation_root", lambda: None)

    report = build_llama_cpp_report(tmp_path)

    assert "cmake" in report.lower()
    assert "ninja" in report.lower()
    assert "cl" in report.lower()


def test_detect_cuda_toolchain_reports_nvcc_presence(monkeypatch):
    def fake_which(name):
        return "C:/CUDA/bin/nvcc.exe" if name == "nvcc" else None

    monkeypatch.setattr(shutil, "which", fake_which)

    tools = detect_cuda_toolchain()

    assert tools["nvcc"] is True


def test_build_report_plans_cuda_build_flags(tmp_path, monkeypatch):
    make_file(tmp_path, "tools/llama.cpp/CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "tools/llama.cpp/examples/main.cpp", "// example\n")
    make_file(tmp_path, "tools/llama.cpp/ggml/README.md", "ggml\n")
    make_file(tmp_path, "tools/llama.cpp/src/llama.cpp/CMakeLists.txt", "project(llama)\n")

    def fake_which(name):
        if name == "nvcc":
            return "C:/CUDA/bin/nvcc.exe"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(llamacpp_build, "_find_vs_installation_root", lambda: None)

    report = build_llama_cpp_report(
        tmp_path,
        build_profile="release",
        build_backend="cuda",
        flash_attention=True,
    )

    assert "GGML_CUDA=ON" in report
    assert "GGML_CUDA_FA=ON" in report
