from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

from benchmark_manifest import default_run_id, resolve_source_root
from benchmark_report import write_benchmark_report
from parse_llama_bench import append_llama_bench_csv, parse_llama_bench_output, summarize_llama_bench_rows


def build_command(
    executable: Path,
    model_path: Path,
    ctx_size: int,
    prompt_tokens: int,
    gen_tokens: int,
    gpu_layers: int,
    cache_k: str,
    cache_v: str,
    short_cache_flags: bool,
    repetitions: int = 1,
    output_format: str = "json",
    flash_attention: bool = False,
) -> list[str]:
    command = [
        str(executable),
        "-m",
        str(model_path),
        "-r",
        str(repetitions),
        "-o",
        output_format,
        "-p",
        str(prompt_tokens),
        "-n",
        str(gen_tokens),
        "-c",
        str(ctx_size),
        "-ngl",
        str(gpu_layers),
    ]
    if short_cache_flags:
        command.extend(["-ctk", cache_k, "-ctv", cache_v])
    else:
        command.extend(["--cache-type-k", cache_k, "--cache-type-v", cache_v])
    if flash_attention:
        command.extend(["-fa", "1"])
    return command


def summarize_run(run_id: str, status: str, notes: str = "", **extra: Any) -> dict[str, str]:
    row: dict[str, str] = {
        "run_id": run_id,
        "status": status,
        "notes": notes,
    }
    for key, value in extra.items():
        row[key] = "" if value is None else str(value)
    return row


def find_llama_bench_executable(root: Path, build_backend: str, build_profile: str) -> Path:
    source_root = resolve_source_root(root)
    search_roots = [
        source_root,
        root.resolve(),
    ]
    backend_specific_patterns = [
        f"build/{build_backend}-{build_profile}/bin/llama-bench.exe",
        f"build/{build_backend}-{build_profile}/bin/llama-bench",
        f"build/{build_backend}-{build_profile}/llama-bench.exe",
        f"build/{build_backend}-{build_profile}/llama-bench",
        f"build-{build_backend}-{build_profile}/bin/llama-bench.exe",
        f"build-{build_backend}-{build_profile}/bin/llama-bench",
        f"build-{build_backend}-{build_profile}/llama-bench.exe",
        f"build-{build_backend}-{build_profile}/llama-bench",
    ]
    candidates: list[Path] = []
    for search_root in search_roots:
        for pattern in (
            *backend_specific_patterns,
            "build*/bin/llama-bench.exe",
            "build*/bin/llama-bench",
            "build*/llama-bench.exe",
            "build*/llama-bench",
        ):
            candidates.extend(sorted(path for path in search_root.glob(pattern) if path.exists()))

    if candidates:
        return candidates[0]

    build_dir = source_root / f"build-{build_profile}"
    fallback = build_dir / "bin" / "llama-bench.exe"
    if fallback.exists():
        return fallback
    return fallback


def run_single_benchmark(
    *,
    root: Path,
    build_profile: str,
    build_backend: str = "cpu",
    model_id: str,
    model_path: Path,
    ctx_size: int,
    prompt_tokens: int,
    gen_tokens: int,
    cache_k: str,
    cache_v: str,
    gpu_layers: int,
    flash_attention: bool = False,
    short_cache_flags: bool,
    run_iteration: int = 1,
    repetitions: int = 1,
    dry_run: bool,
) -> dict[str, str]:
    source_root = resolve_source_root(root)
    flash_attention = bool(flash_attention and build_backend == "cuda")
    if not dry_run and not model_path.exists():
        run_id = default_run_id(
            build_profile,
            "llama-bench",
            model_id,
            ctx_size,
            prompt_tokens,
            gen_tokens,
            cache_k,
            cache_v,
            run_iteration=run_iteration,
            repetitions=repetitions,
            build_backend=build_backend,
            flash_attention=flash_attention,
        )
        return summarize_run(
            run_id=run_id,
            status="skipped",
            notes=f"missing model: {model_path}",
            model_id=model_id,
            model_path=str(model_path),
            cache_k=cache_k,
            cache_v=cache_v,
            build_profile=build_profile,
            build_backend=build_backend,
            flash_attention=str(flash_attention),
        )

    executable = find_llama_bench_executable(root, build_backend, build_profile)
    run_id = default_run_id(
        build_profile,
        executable.name,
        model_id,
        ctx_size,
        prompt_tokens,
        gen_tokens,
        cache_k,
        cache_v,
        run_iteration=run_iteration,
        repetitions=repetitions,
        build_backend=build_backend,
        flash_attention=flash_attention,
    )

    command = build_command(
        executable=executable,
        model_path=model_path,
        ctx_size=ctx_size,
        prompt_tokens=prompt_tokens,
        gen_tokens=gen_tokens,
        gpu_layers=gpu_layers,
        cache_k=cache_k,
        cache_v=cache_v,
        short_cache_flags=short_cache_flags,
        repetitions=repetitions,
        flash_attention=flash_attention,
    )

    if dry_run:
        return summarize_run(
            run_id=run_id,
            status="skipped",
            notes="dry-run",
            executable=str(executable),
            command=" ".join(command),
            model_id=model_id,
            cache_k=cache_k,
            cache_v=cache_v,
            build_profile=build_profile,
            build_backend=build_backend,
            flash_attention=str(flash_attention),
            run_iteration=str(run_iteration),
            repetitions=str(repetitions),
        )

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    status = "passed" if completed.returncode == 0 else "failed"
    notes = completed.stderr.strip() if completed.stderr else ""
    raw_dir = root.resolve() / "results" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_output_path = raw_dir / f"{run_id}.json"
    raw_output_path.write_text(completed.stdout, encoding="utf-8")

    parsed_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    if completed.returncode == 0 and completed.stdout.strip():
        parsed_rows = parse_llama_bench_output(completed.stdout)
        append_llama_bench_csv(parsed_rows, root.resolve() / "results" / "parsed" / "performance.csv")
        summary = summarize_llama_bench_rows(parsed_rows)

    return summarize_run(
        run_id=run_id,
        status=status,
        notes=notes,
        executable=str(executable),
        command=" ".join(command),
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
        returncode=completed.returncode,
        model_id=model_id,
        cache_k=cache_k,
        cache_v=cache_v,
        build_profile=build_profile,
        build_backend=build_backend,
        flash_attention=str(flash_attention),
        run_iteration=str(run_iteration),
        repetitions=str(repetitions),
        prefill_tps=summary.get("prefill_tps", ""),
        decode_tps=summary.get("decode_tps", ""),
        total_time_ms=summary.get("total_time_ms", ""),
        raw_output=str(raw_output_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single llama-bench benchmark.")
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    parser.add_argument("--profile", default="release")
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-path", required=True, type=Path)
    parser.add_argument("--ctx-size", default=2048, type=int)
    parser.add_argument("--prompt-tokens", default=512, type=int)
    parser.add_argument("--gen-tokens", default=128, type=int)
    parser.add_argument("--cache-k", default="f16")
    parser.add_argument("--cache-v", default="f16")
    parser.add_argument("--gpu-layers", default=999, type=int)
    parser.add_argument("--flash-attention", action="store_true")
    parser.add_argument("--short-cache-flags", action="store_true")
    parser.add_argument("--run-iteration", default=1, type=int)
    parser.add_argument("--repetitions", default=1, type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    row = run_single_benchmark(
        root=args.root,
        build_profile=args.profile,
        build_backend=args.backend,
        model_id=args.model_id,
        model_path=args.model_path,
        ctx_size=args.ctx_size,
        prompt_tokens=args.prompt_tokens,
        gen_tokens=args.gen_tokens,
        cache_k=args.cache_k,
        cache_v=args.cache_v,
        gpu_layers=args.gpu_layers,
        flash_attention=args.flash_attention,
        short_cache_flags=args.short_cache_flags,
        run_iteration=args.run_iteration,
        repetitions=args.repetitions,
        dry_run=args.dry_run,
    )

    source_root = resolve_source_root(args.root)
    report_path = write_benchmark_report(
        root=args.root,
        source_root=source_root,
        build_profile=args.profile,
        run_summary=[row],
    )
    print(report_path)
    return 0 if row["status"] in {"skipped", "passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
