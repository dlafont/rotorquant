from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping


def _cell(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    return "" if value in ("", None) else str(value)


def _load_parsed_rows(root: Path) -> list[dict[str, str]]:
    parsed_path = root.resolve() / "results" / "parsed" / "performance.csv"
    if not parsed_path.exists():
        return []

    with parsed_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def build_benchmark_report(
    root: Path,
    source_root: Path,
    build_profile: str,
    run_summary: Iterable[Mapping[str, object]],
) -> str:
    root = root.resolve()
    source_root = source_root.resolve()
    parsed_rows = _load_parsed_rows(root)
    lines = [
        "# Benchmark Automation Report",
        "",
        f"- Root: `{root}`",
        f"- Source root: `{source_root}`",
        f"- Build profile: `{build_profile}`",
        "- Build backend: `cpu` or `cuda`, matching the public llama.cpp split between CPU-only and CUDA-enabled builds",
        "- Flash attention: `-fa 1` is only emitted for CUDA jobs when requested",
        "- Blank metric cells mean the row was skipped, dry-run, or did not produce parsed llama-bench output yet",
        "",
        "## Runs",
        "| run_id | status | build_backend | flash_attention | run_iteration | executable | cache_k | cache_v | prefill_tps | decode_tps | total_time_ms | command | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in run_summary:
        lines.append(
            f"| `{_cell(row, 'run_id')}` | {_cell(row, 'status')} | {_cell(row, 'build_backend')} | {_cell(row, 'flash_attention')} | {_cell(row, 'run_iteration')} | {_cell(row, 'executable')} | {_cell(row, 'cache_k')} | {_cell(row, 'cache_v')} | {_cell(row, 'prefill_tps')} | {_cell(row, 'decode_tps')} | {_cell(row, 'total_time_ms')} | {_cell(row, 'command')} | {_cell(row, 'notes')} |"
        )

    if parsed_rows:
        lines.extend(
            [
                "",
                "## Parsed llama-bench Results",
                "| test_kind | n_prompt | n_gen | avg_ts | avg_ns | prefill_tps | decode_tps | total_time_ms |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in parsed_rows:
            lines.append(
                f"| {_cell(row, 'test_kind')} | {_cell(row, 'n_prompt')} | {_cell(row, 'n_gen')} | {_cell(row, 'avg_ts')} | {_cell(row, 'avg_ns')} | {_cell(row, 'prefill_tps')} | {_cell(row, 'decode_tps')} | {_cell(row, 'total_time_ms')} |"
            )
    return "\n".join(lines) + "\n"


def write_benchmark_report(
    root: Path,
    source_root: Path,
    build_profile: str,
    run_summary: Iterable[Mapping[str, object]],
    output_path: Path | None = None,
) -> Path:
    root = root.resolve()
    source_root = source_root.resolve()
    output_path = output_path or (root / "results" / "reports" / "benchmark-automation-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_benchmark_report(root, source_root, build_profile, run_summary),
        encoding="utf-8",
    )
    return output_path
