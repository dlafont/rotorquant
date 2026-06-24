from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from benchmark_manifest import resolve_source_root
from benchmark_matrix import expand_matrix_jobs
from benchmark_report import write_benchmark_report
from run_single_llama_bench import run_single_benchmark


def run_matrix(
    root: Path,
    build_profile: str,
    build_backend: str = "cpu",
    dry_run: bool = False,
    quick: bool = False,
) -> list[dict[str, Any]]:
    root = root.resolve()
    jobs = expand_matrix_jobs(root)
    if quick and jobs:
        jobs = jobs[:1]
    rows: list[dict[str, Any]] = []
    for job in jobs:
        row = run_single_benchmark(
            root=root,
            build_profile=build_profile,
            build_backend=str(job.get("build_backend", build_backend)),
            model_id=str(job["model_id"]),
            model_path=Path(str(job["model_path"])),
            ctx_size=int(job["ctx_size"]),
            prompt_tokens=int(job["prompt_tokens"]),
            gen_tokens=int(job["gen_tokens"]),
            cache_k=str(job["cache_k"]),
            cache_v=str(job["cache_v"]),
            gpu_layers=int(job["gpu_layers"]),
            flash_attention=bool(job.get("flash_attention", False)),
            short_cache_flags=False,
            run_iteration=int(job.get("repetition", 1)),
            repetitions=1,
            dry_run=dry_run,
        )
        rows.append(row)

    source_root = resolve_source_root(root)
    write_benchmark_report(
        root=root,
        source_root=source_root,
        build_profile=build_profile,
        run_summary=rows,
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the benchmark matrix.")
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    parser.add_argument("--profile", default="release")
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    run_matrix(
        root=args.root,
        build_profile=args.profile,
        build_backend=args.backend,
        dry_run=args.dry_run,
        quick=args.quick,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
