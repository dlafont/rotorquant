from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from benchmark_report import build_benchmark_report, write_benchmark_report


def test_build_benchmark_report_mentions_cuda_as_optional(tmp_path: Path) -> None:
    report = build_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[
            {
                "run_id": "abc123",
                "status": "skipped",
                "cache_k": "f16",
                "cache_v": "f16",
                "notes": "dry-run",
            }
        ],
    )

    assert "CUDA" in report
    assert "dry-run" in report
    assert "abc123" in report


def test_build_benchmark_report_explains_blank_metrics_for_skipped_runs(tmp_path: Path) -> None:
    report = build_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[
            {
                "run_id": "abc123",
                "status": "skipped",
                "cache_k": "f16",
                "cache_v": "f16",
                "notes": "dry-run",
            }
        ],
    )

    assert "blank" in report.lower()
    assert "dry-run" in report


def test_build_benchmark_report_includes_parsed_results_section(tmp_path: Path) -> None:
    parsed = tmp_path / "results" / "parsed" / "performance.csv"
    parsed.parent.mkdir(parents=True, exist_ok=True)
    parsed.write_text(
        "test_kind,n_prompt,n_gen,avg_ts,avg_ns,prefill_tps,decode_tps,total_time_ms\n"
        "prefill,512,0,7100.002165,72135640,7100.002165,,72.13564\n"
        "decode,0,128,119.915244,1067431600,,119.915244,1067.4316\n",
        encoding="utf-8",
    )

    report = build_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[],
    )

    assert "Parsed llama-bench Results" in report
    assert "prefill" in report
    assert "decode" in report


def test_write_benchmark_report_creates_file(tmp_path: Path) -> None:
    output = write_benchmark_report(
        root=tmp_path,
        source_root=tmp_path / "tools" / "llama.cpp",
        build_profile="release",
        run_summary=[],
    )

    assert output.exists()
