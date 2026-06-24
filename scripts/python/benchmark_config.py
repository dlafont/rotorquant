from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at top level in {path}")
    return data


def load_models(path: Path) -> list[dict[str, Any]]:
    data = load_yaml_file(path)
    models = data.get("models", {})
    if not isinstance(models, dict):
        raise ValueError("models must be a mapping")
    result: list[dict[str, Any]] = []
    for model_id, model in models.items():
        if not isinstance(model, dict):
            raise ValueError(f"model {model_id} must be a mapping")
        row = dict(model)
        row["model_id"] = model_id
        result.append(row)
    return result


def load_cache_methods(path: Path) -> list[dict[str, Any]]:
    data = load_yaml_file(path)
    methods = data.get("cache_methods", [])
    if not isinstance(methods, list):
        raise ValueError("cache_methods must be a list")
    result: list[dict[str, Any]] = []
    for method in methods:
        if not isinstance(method, dict):
            raise ValueError("cache method entries must be mappings")
        result.append(dict(method))
    return result


def load_benchmark_matrix(path: Path) -> dict[str, Any]:
    data = load_yaml_file(path)
    return data
