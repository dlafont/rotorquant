from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# This script detects the presence of a llama.cpp-style source checkout and the availability of build tools and CUDA toolchain on the local system, then generates a markdown report with a recommended set of commands to build llama.cpp based on the findings.
@dataclass(frozen=True)
class LlamaCppSource:
    root: Path
    has_cmakelists: bool
    has_examples: bool
    has_ggml: bool
    has_src_llama_cpp: bool

    @property
    def buildable(self) -> bool:
        return all(
            [self.has_cmakelists, self.has_examples, self.has_ggml, self.has_src_llama_cpp]
        )

# detect presence of build tools (cmake, ninja, cl) and CUDA toolchain (nvcc), including bundled versions from Visual Studio if available
def detect_build_tools() -> dict[str, bool]:
    statuses = {
        "cmake": shutil.which("cmake") is not None,
        "ninja": shutil.which("ninja") is not None,
        "cl": shutil.which("cl") is not None,
    }

    if all(statuses.values()):
        return statuses

    vs_root = _find_vs_installation_root()
    if vs_root is None:
        return statuses

# If Visual Studio is installed but the tools are not on PATH, check for bundled versions of cmake, ninja, and cl.
    bundled_cmake = vs_root / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "CMake" / "bin" / "cmake.exe"
    bundled_ninja = vs_root / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "Ninja" / "ninja.exe"
    msvc_root = vs_root / "VC" / "Tools" / "MSVC"
    bundled_cl = None
    if msvc_root.exists():
        cl_candidates = sorted(msvc_root.glob("*/bin/Hostx64/x64/cl.exe"), reverse=True)
        bundled_cl = cl_candidates[0] if cl_candidates else None

    statuses["cmake"] = statuses["cmake"] or bundled_cmake.exists()
    statuses["ninja"] = statuses["ninja"] or bundled_ninja.exists()
    statuses["cl"] = statuses["cl"] or (bundled_cl is not None and bundled_cl.exists())
    return statuses

# detect presence of CUDA toolchain (nvcc)
def detect_cuda_toolchain() -> dict[str, bool]:
    return {
        "nvcc": shutil.which("nvcc") is not None,
    }

# helper to convert boolean to "yes"/"no" for report readability
def _bool_text(value: bool) -> str:
    return "yes" if value else "no"

# helper to find Visual Studio installation root using vswhere.exe, which is the recommended way to locate Visual Studio installations on Windows. Returns None if vswhere.exe is not found or if it fails to find a suitable installation.
def _find_vs_installation_root() -> Optional[Path]:
    vswhere = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") 
    if not vswhere.exists():
        return None
    completed = subprocess.run(
        [str(vswhere), "-latest", "-products", "*", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        capture_output=True,
        text=True,
        check=False,
    )
#   If vswhere fails (e.g. due to an unexpected error), treat it as if Visual Studio is not installed. We don't want to raise an exception here since the presence of Visual Studio is just an optional enhancement for build tool detection. 
    if completed.returncode != 0:
        return None
    output = completed.stdout.strip()
    return Path(output) if output else None

# helper to probe a given path for the presence of llama.cpp source files and structure. Returns a LlamaCppSource object if the path looks like a valid llama.cpp source root, or None otherwise.
def _probe_source_root(path: Path) -> Optional[LlamaCppSource]:
    path = path.resolve()
    source = LlamaCppSource(
        root=path,
        has_cmakelists=(path / "CMakeLists.txt").exists(),
        has_examples=(path / "examples").exists(),
        has_ggml=(path / "ggml").exists(),
        has_src_llama_cpp=(path / "src" / "llama.cpp").exists(),
    )
    return source if source.buildable else None


def detect_llama_cpp_source_root(root: Path) -> Optional[Path]:
    root = root.resolve()
    for candidate in (root, root / "tools" / "llama.cpp"):
        source = _probe_source_root(candidate)
        if source is not None:
            return source.root
    return None


def _cmake_build_type(build_profile: str) -> str:
    return build_profile[:1].upper() + build_profile[1:].lower() if build_profile else "Release"


def build_llama_cpp_report(
    root: Path,
    build_profile: str = "release",
    build_backend: str = "cpu",
    flash_attention: bool = False,
) -> str:
    root = root.resolve()
    source_root = detect_llama_cpp_source_root(root)
    build_tools = detect_build_tools()
    cuda_toolchain = detect_cuda_toolchain()
    effective_flash_attention = bool(flash_attention and build_backend == "cuda")

    lines: list[str] = []
    lines.append("# llama.cpp Build Report")
    lines.append("")
    lines.append(f"- Workspace root: `{root}`")
    lines.append(f"- Requested profile: `{build_profile}`")
    lines.append(f"- Requested backend: `{build_backend}`")
    lines.append(f"- Flash attention: `{_bool_text(effective_flash_attention)}`")
    lines.append("")
    lines.append("## Prerequisites")
    lines.append("| Tool | Status |")
    lines.append("|---|---|")
    lines.append(f"| `cmake` | {'present' if build_tools['cmake'] else 'missing'} |")
    lines.append(f"| `ninja` | {'present' if build_tools['ninja'] else 'missing'} |")
    lines.append(f"| `cl` | {'present' if build_tools['cl'] else 'missing'} |")
    lines.append(f"| `nvcc` | {'present' if cuda_toolchain['nvcc'] else 'missing'} |")

    if source_root is None:
        lines.append("")
        lines.append("- Source checkout: missing")
        lines.append("")
        lines.append("## Status")
        lines.append(
            "- Build is blocked because no llama.cpp-style checkout was found at the repo root or under `tools/llama.cpp/`."
        )
        return "\n".join(lines) + "\n"

    build_dir = root / "build" / f"{build_backend}-{build_profile}"
    if source_root != root:
        rel_source = source_root.relative_to(root)
        lines.append(f"- Source checkout: `{rel_source}`")
    else:
        lines.append("- Source checkout: repo root")
    lines.append(f"- Build directory: `{build_dir}`")
    if build_backend == "cuda" and not cuda_toolchain["nvcc"]:
        lines.append("- CUDA build note: CUDA backend was requested but `nvcc` was not detected locally.")
    lines.append("")
    lines.append("## Planned Commands")
    if build_backend == "cuda":
        cmake_cmd = [
            "cmake",
            "-S",
            f'"{source_root}"',
            "-B",
            f'"{build_dir}"',
            "-G",
            "Ninja",
            f"-DCMAKE_BUILD_TYPE={_cmake_build_type(build_profile)}",
            "-DGGML_CUDA=ON",
        ]
        if effective_flash_attention:
            cmake_cmd.append("-DGGML_CUDA_FA=ON")
        lines.append(f"1. `{' '.join(cmake_cmd)}`")
    else:
        lines.append(f"1. `cmake -S \"{source_root}\" -B \"{build_dir}\" -G Ninja -DCMAKE_BUILD_TYPE={_cmake_build_type(build_profile)}`")
    lines.append(f"2. `cmake --build \"{build_dir}\" --config {_cmake_build_type(build_profile)} -j`")
    lines.append("3. `llama-bench --help`")
    return "\n".join(lines) + "\n"


def write_build_report(
    root: Path,
    output_path: Optional[Path] = None,
    build_profile: str = "release",
    build_backend: str = "cpu",
    flash_attention: bool = False,
) -> Path:
    root = root.resolve()
    output_path = output_path or (root / "results" / "reports" / "llamacpp-build-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_llama_cpp_report(
            root,
            build_profile=build_profile,
            build_backend=build_backend,
            flash_attention=flash_attention,
        ),
        encoding="utf-8",
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or report a llama.cpp build.")
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    parser.add_argument("--output", default=None, type=Path)
    parser.add_argument("--profile", default="release")
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--flash-attention", action="store_true")
    args = parser.parse_args()

    output_path = write_build_report(
        args.root,
        output_path=args.output,
        build_profile=args.profile,
        build_backend=args.backend,
        flash_attention=args.flash_attention,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
