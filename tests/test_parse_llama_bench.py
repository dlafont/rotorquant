from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from parse_llama_bench import (
    parse_llama_bench_output,
    summarize_llama_bench_rows,
    write_llama_bench_csv,
)


def test_parse_llama_bench_output_labels_prefill_and_decode() -> None:
    output = """
[
  {
    "build_commit": "8cf427ff",
    "build_number": 5163,
    "model_filename": "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    "model_type": "qwen2 7B Q4_K - Medium",
    "n_prompt": 512,
    "n_gen": 0,
    "n_depth": 0,
    "avg_ns": 72135640,
    "stddev_ns": 1453752,
    "avg_ts": 7100.002165,
    "stddev_ts": 140.341520
  },
  {
    "build_commit": "8cf427ff",
    "build_number": 5163,
    "model_filename": "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    "model_type": "qwen2 7B Q4_K - Medium",
    "n_prompt": 0,
    "n_gen": 128,
    "n_depth": 0,
    "avg_ns": 1067431600,
    "stddev_ns": 3834831,
    "avg_ts": 119.915244,
    "stddev_ts": 0.430617
  }
]
""".strip()

    rows = parse_llama_bench_output(output)
    summary = summarize_llama_bench_rows(rows)

    assert len(rows) == 2
    assert rows[0]["test_kind"] == "prefill"
    assert rows[1]["test_kind"] == "decode"
    assert summary["prefill_tps"] == 7100.002165
    assert summary["decode_tps"] == 119.915244


def test_write_llama_bench_csv_creates_file(tmp_path: Path) -> None:
    rows = [
        {
            "test_kind": "prefill",
            "n_prompt": 512,
            "n_gen": 0,
            "n_depth": 0,
            "avg_ts": 7100.002165,
        }
    ]

    output = write_llama_bench_csv(rows, tmp_path / "performance.csv")

    assert output.exists()
