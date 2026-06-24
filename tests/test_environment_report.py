from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from environment_report import build_environment_report, detect_repo_profile


def make_file(root: Path, relative_path: str, content: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detects_rotorquant_research_repo(tmp_path):
    make_file(tmp_path, "turboquant/rotorquant.py", "print('hi')\n")

    profile = detect_repo_profile(tmp_path)

    assert profile.repo_kind == "rotorquant-research"
    assert profile.has_rotorquant_python is True
    assert profile.can_build_llama_cpp_directly is False


def test_detects_llama_cpp_style_repo(tmp_path):
    make_file(tmp_path, "CMakeLists.txt", "cmake_minimum_required(VERSION 3.20)\n")
    make_file(tmp_path, "examples/main.cpp", "// example\n")
    make_file(tmp_path, "tools/llama.cpp/README.md", "fork\n")
    make_file(tmp_path, "src/llama.cpp/CMakeLists.txt", "project(llama)\n")
    make_file(tmp_path, "ggml/README.md", "ggml\n")

    profile = detect_repo_profile(tmp_path)

    assert profile.repo_kind == "llama.cpp-style"
    assert profile.can_build_llama_cpp_directly is True


def test_build_environment_report_mentions_missing_llama_cpp_for_rotorquant_repo(tmp_path):
    make_file(tmp_path, "turboquant/rotorquant.py", "print('hi')\n")

    report = build_environment_report(
        tmp_path,
        git_info={
            "remote_url": "https://github.com/example/rotorquant.git",
            "branch": "main",
            "commit": "abc1234",
        },
    )

    assert "RotorQuant research repo" in report
    assert "tools/llama.cpp/" in report
    assert "missing" in report.lower()
