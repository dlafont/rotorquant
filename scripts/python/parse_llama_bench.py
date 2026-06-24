from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable


def _test_kind(n_prompt: int, n_gen: int, n_depth: int) -> str:
    if n_prompt > 0 and n_gen == 0:
        return "prefill"
    if n_prompt == 0 and n_gen > 0:
        return "decode"
    if n_prompt > 0 and n_gen > 0:
        return "prompt_gen"
    if n_depth > 0:
        return "depth"
    return "other"


def parse_llama_bench_output(stdout: str) -> list[dict[str, Any]]:
    data = json.loads(stdout)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("llama-bench JSON output must be an array or object")

    rows: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("llama-bench JSON records must be objects")

        row = dict(item)
        n_prompt = int(row.get("n_prompt", 0) or 0)
        n_gen = int(row.get("n_gen", 0) or 0)
        n_depth = int(row.get("n_depth", 0) or 0)
        row["test_kind"] = _test_kind(n_prompt, n_gen, n_depth)
        row["prefill_tps"] = float(row["avg_ts"]) if row["test_kind"] == "prefill" else ""
        row["decode_tps"] = float(row["avg_ts"]) if row["test_kind"] == "decode" else ""
        row["total_time_ms"] = float(row["avg_ns"]) / 1_000_000.0 if "avg_ns" in row else ""
        rows.append(row)
    return rows


def summarize_llama_bench_rows(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    prefill_tps = ""
    decode_tps = ""
    total_time_ms = 0.0
    for row in rows:
        if row.get("test_kind") == "prefill" and row.get("prefill_tps") != "":
            prefill_tps = float(row["prefill_tps"])
        elif row.get("test_kind") == "decode" and row.get("decode_tps") != "":
            decode_tps = float(row["decode_tps"])
        if row.get("total_time_ms") != "":
            total_time_ms += float(row["total_time_ms"])

    return {
        "prefill_tps": prefill_tps,
        "decode_tps": decode_tps,
        "total_time_ms": total_time_ms if total_time_ms else "",
    }


def write_llama_bench_csv(rows: Iterable[dict[str, Any]], output_path: Path) -> Path:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def append_llama_bench_csv(rows: Iterable[dict[str, Any]], output_path: Path) -> Path:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        return output_path

    fieldnames: list[str] = []
    existing_rows: list[dict[str, Any]] = []
    if output_path.exists():
        with output_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            existing_rows = list(reader)

    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    combined_rows = existing_rows + rows
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in combined_rows:
            writer.writerow(row)
    return output_path
