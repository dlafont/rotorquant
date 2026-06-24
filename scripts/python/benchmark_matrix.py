from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Any

from benchmark_config import load_benchmark_matrix, load_cache_methods, load_models


def _config_path(root: Path, name: str) -> Path:
    return root.resolve() / "configs" / name


def _as_list(value: Any, default: list[Any]) -> list[Any]:
    if value is None:
        return list(default)
    if isinstance(value, list):
        return list(value)
    return [value]


def _build_profiles(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = matrix.get("build_profiles")
    if profiles is None:
        build_backends = [str(item) for item in _as_list(matrix.get("build_backends", matrix.get("build_backend")), ["cpu"])]
        flash_attention_values = [bool(item) for item in _as_list(matrix.get("flash_attention"), [False])]
        return [
            {
                "build_backend": build_backend,
                "flash_attention": bool(flash_attention and build_backend == "cuda"),
            }
            for build_backend in build_backends
            for flash_attention in flash_attention_values
        ]

    if not isinstance(profiles, list):
        raise ValueError("build_profiles must be a list")

    result: list[dict[str, Any]] = []
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("build_profiles entries must be mappings")
        build_backend = str(profile.get("build_backend", "cpu"))
        flash_attention = bool(profile.get("flash_attention", False) and build_backend == "cuda")
        result.append(
            {
                "build_backend": build_backend,
                "flash_attention": flash_attention,
            }
        )
    return result


def expand_matrix_jobs(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    models = load_models(_config_path(root, "models.yaml"))
    cache_methods = load_cache_methods(_config_path(root, "cache_methods.yaml"))
    matrix = load_benchmark_matrix(_config_path(root, "benchmark.matrix.yaml"))

    build_profiles = _build_profiles(matrix)
    context_sizes = list(matrix.get("context_sizes", []))
    prompt_tokens = list(matrix.get("prompt_tokens", []))
    generation_tokens = list(matrix.get("generation_tokens", []))
    gpu_layers = list(matrix.get("gpu_layers", []))
    repetitions = int((matrix.get("repetitions") or {}).get("performance", 1))
    seed = matrix.get("seed")
    temperature = matrix.get("temperature")

    jobs: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for model, cache_method, build_profile, ctx_size, prompt, gen, layer, repetition in product(
        models,
        cache_methods,
        build_profiles,
        context_sizes,
        prompt_tokens,
        generation_tokens,
        gpu_layers,
        range(repetitions),
    ):
        build_backend = str(build_profile["build_backend"])
        effective_flash_attention = bool(build_profile["flash_attention"])
        job = {
            "model_id": model.get("model_id", ""),
            "model_path": model.get("path", ""),
            "cache_id": cache_method.get("id", ""),
            "cache_k": cache_method.get("cache_k", ""),
            "cache_v": cache_method.get("cache_v", ""),
            "build_backend": build_backend,
            "flash_attention": effective_flash_attention,
            "ctx_size": ctx_size,
            "prompt_tokens": prompt,
            "gen_tokens": gen,
            "gpu_layers": layer,
            "repetition": repetition + 1,
            "seed": seed,
            "temperature": temperature,
        }
        dedupe_key = (
            job["model_id"],
            job["cache_id"],
            job["build_backend"],
            job["flash_attention"],
            job["ctx_size"],
            job["prompt_tokens"],
            job["gen_tokens"],
            job["gpu_layers"],
            job["repetition"],
            job["seed"],
            job["temperature"],
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        jobs.append(
            job
        )
    return jobs
