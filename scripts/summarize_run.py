#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a structured markdown summary from recorded stage runs.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    report_path = workspace / "pipeline" / "run_report.json"
    if not report_path.exists():
        raise SystemExit("run_report.json not found. Use record_stage_run.py first.")

    entries = json.loads(report_path.read_text(encoding="utf-8"))
    lines = [
        f"# Pipeline Summary: {cfg['project']['title']}",
        "",
        f"- target journal: `{cfg['journal']['target_name']}`",
        f"- total stage events: `{len(entries)}`",
        "",
        "## Stage events",
        "",
    ]
    for row in entries:
        lines.extend(
            [
                f"### {row['stage_id']}",
                "",
                f"- timestamp: `{row['timestamp']}`",
                f"- status: `{row['status']}`",
                f"- summary: {row['summary']}",
                "",
            ]
        )
    outpath = workspace / "pipeline" / "pipeline_summary.md"
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(outpath)


if __name__ == "__main__":
    main()
