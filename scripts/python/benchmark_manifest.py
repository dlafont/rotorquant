from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path


@dataclass(frozen=True)
class BenchmarkRunRequest:
    build_profile: str
    model_id: str
    model_path: Path
    ctx_size: int
    prompt_tokens: int
    gen_tokens: int
    cache_k: str
    cache_v: str
    build_backend: str = "cpu"
    enable_cuda: bool = False
    flash_attention: bool = False


def _is_llama_cpp_source_root(path: Path) -> bool:
    return all(
        [
            (path / "CMakeLists.txt").exists(),
            (path / "examples").exists(),
            (path / "ggml").exists(),
            (path / "src" / "llama.cpp").exists(),
        ]
    )


def resolve_source_root(root: Path) -> Path:
    root = root.resolve()
    for candidate in (root / "tools" / "llama.cpp", root):
        if _is_llama_cpp_source_root(candidate):
            return candidate
    raise FileNotFoundError(
        f"No llama.cpp source root found under {root} or {root / 'tools' / 'llama.cpp'}"
    )


def default_run_id(
    build_profile: str,
    executable: str,
    model_id: str,
    ctx_size: int,
    prompt_tokens: int,
    gen_tokens: int,
    cache_k: str,
    cache_v: str,
    run_iteration: int = 1,
    repetitions: int = 1,
    build_backend: str = "cpu",
    flash_attention: bool = False,
) -> str:
    payload = "|".join(
        [
            build_profile,
            build_backend,
            executable,
            model_id,
            str(ctx_size),
            str(prompt_tokens),
            str(gen_tokens),
            cache_k,
            cache_v,
            str(run_iteration),
            str(repetitions),
            "fa" if flash_attention else "no-fa",
        ]
    )
    return sha1(payload.encode("utf-8")).hexdigest()[:12]
