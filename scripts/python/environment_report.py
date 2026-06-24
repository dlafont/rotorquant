from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional


@dataclass(frozen=True)
class RepoProfile:
    root: Path
    has_cmakelists: bool
    has_examples: bool
    has_tools_dir: bool
    has_ggml_dir: bool
    has_llama_cpp_source: bool
    has_turboquant_dir: bool
    has_rotorquant_python: bool
    repo_kind: str
    can_build_llama_cpp_directly: bool


def _exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def detect_repo_profile(root: Path) -> RepoProfile:
    root = root.resolve()
    has_cmakelists = _exists(root, "CMakeLists.txt")
    has_examples = _exists(root, "examples")
    has_tools_dir = _exists(root, "tools")
    has_ggml_dir = _exists(root, "ggml")
    has_llama_cpp_source = _exists(root, "src/llama.cpp")
    has_turboquant_dir = _exists(root, "turboquant")
    has_rotorquant_python = _exists(root, "turboquant/rotorquant.py")

    can_build_llama_cpp_directly = all(
        [has_cmakelists, has_examples, has_tools_dir, has_ggml_dir, has_llama_cpp_source]
    )

    if can_build_llama_cpp_directly and has_rotorquant_python:
        repo_kind = "hybrid"
    elif can_build_llama_cpp_directly:
        repo_kind = "llama.cpp-style"
    elif has_rotorquant_python:
        repo_kind = "rotorquant-research"
    else:
        repo_kind = "unknown"

    return RepoProfile(
        root=root,
        has_cmakelists=has_cmakelists,
        has_examples=has_examples,
        has_tools_dir=has_tools_dir,
        has_ggml_dir=has_ggml_dir,
        has_llama_cpp_source=has_llama_cpp_source,
        has_turboquant_dir=has_turboquant_dir,
        has_rotorquant_python=has_rotorquant_python,
        repo_kind=repo_kind,
        can_build_llama_cpp_directly=can_build_llama_cpp_directly,
    )


def _run_git(root: Path, *args: str) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None

    value = completed.stdout.strip()
    return value or None


def collect_git_info(root: Path) -> dict[str, Optional[str]]:
    return {
        "remote_url": _run_git(root, "remote", "get-url", "origin"),
        "branch": _run_git(root, "branch", "--show-current"),
        "commit": _run_git(root, "rev-parse", "HEAD"),
    }


def _bool_text(value: bool) -> str:
    return "yes" if value else "no"


def _repo_kind_label(repo_kind: str) -> str:
    if repo_kind == "rotorquant-research":
        return "RotorQuant research repo"
    if repo_kind == "llama.cpp-style":
        return "llama.cpp-style repo"
    if repo_kind == "hybrid":
        return "hybrid repo"
    return "unknown repo"


def build_environment_report(
    root: Path,
    git_info: Optional[Mapping[str, Optional[str]]] = None,
    profile: Optional[RepoProfile] = None,
) -> str:
    profile = profile or detect_repo_profile(root)
    git_info = dict(git_info or collect_git_info(root))

    lines: list[str] = []
    lines.append("# Environment Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Root: `{profile.root}`")
    lines.append(f"- Repo kind: {_repo_kind_label(profile.repo_kind)}")
    lines.append(
        f"- Direct llama.cpp build: {_bool_text(profile.can_build_llama_cpp_directly)}"
    )
    lines.append(f"- Git remote: `{git_info.get('remote_url') or 'unknown'}`")
    lines.append(f"- Git branch: `{git_info.get('branch') or 'unknown'}`")
    lines.append(f"- Git commit: `{git_info.get('commit') or 'unknown'}`")
    lines.append("")
    lines.append("## Signals")
    lines.append("| Check | Result |")
    lines.append("|---|---|")
    lines.append(f"| `CMakeLists.txt` | {_bool_text(profile.has_cmakelists)} |")
    lines.append(f"| `examples/` | {_bool_text(profile.has_examples)} |")
    lines.append(f"| `tools/` | {_bool_text(profile.has_tools_dir)} |")
    lines.append(f"| `ggml/` | {_bool_text(profile.has_ggml_dir)} |")
    lines.append(f"| `src/llama.cpp` | {_bool_text(profile.has_llama_cpp_source)} |")
    lines.append(f"| `turboquant/` | {_bool_text(profile.has_turboquant_dir)} |")
    lines.append(f"| `turboquant/rotorquant.py` | {_bool_text(profile.has_rotorquant_python)} |")
    lines.append("")
    lines.append("## Smoke Test Guidance")
    if profile.can_build_llama_cpp_directly:
        lines.append(
            "- This checkout looks directly buildable as a llama.cpp-style repo, so the next step is to run the build smoke test."
        )
    elif profile.repo_kind == "rotorquant-research":
        lines.append(
            "- This checkout is RotorQuant research-only right now, so `tools/llama.cpp/` is missing and the llama.cpp build smoke test is blocked until the experimental fork is added there."
        )
    else:
        lines.append(
            "- This checkout does not match the expected llama.cpp or RotorQuant shapes, so the next step is to inspect the repository layout before attempting a build."
        )

    return "\n".join(lines) + "\n"


def write_environment_report(
    root: Path,
    output_path: Optional[Path] = None,
    git_info: Optional[Mapping[str, Optional[str]]] = None,
) -> Path:
    root = root.resolve()
    output_path = output_path or (root / "results" / "reports" / "environment-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_environment_report(root, git_info=git_info)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write the repo environment report.")
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    parser.add_argument("--output", default=None, type=Path)
    args = parser.parse_args()

    output_path = write_environment_report(args.root, output_path=args.output)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
