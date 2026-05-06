#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml


VALID_STATUSES = {"pending", "in_progress", "completed", "blocked", "skipped"}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def resolve_harness(package_root: Path, cfg: dict) -> Path:
    local_path = cfg["harness"].get("local_path", "")
    if local_path:
        return Path(local_path).resolve()
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    if candidate.exists():
        return candidate
    raise SystemExit("Harness not found. Run scripts/clone_harness.py or set harness.local_path.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a structured stage run and sync harness pipeline status.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("stage_id", help="Stage id")
    parser.add_argument("status", help="pending|in_progress|completed|blocked|skipped")
    parser.add_argument("--summary", default="", help="Short summary")
    parser.add_argument("--artifact", action="append", default=[], help="Artifact path or note")
    args = parser.parse_args()

    if args.status not in VALID_STATUSES:
        raise SystemExit(f"Invalid status: {args.status}")

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    report_path = workspace / "pipeline" / "run_report.json"
    entries = []
    if report_path.exists():
        entries = json.loads(report_path.read_text(encoding="utf-8"))

    timestamp = datetime.now().isoformat(timespec="seconds")
    entry = {
        "timestamp": timestamp,
        "stage_id": args.stage_id,
        "status": args.status,
        "summary": args.summary,
        "artifacts": args.artifact,
    }
    entries.append(entry)
    report_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    markdown = "\n".join(
        [
            f"# Stage Run: {args.stage_id}",
            "",
            f"- timestamp: `{timestamp}`",
            f"- status: `{args.status}`",
            f"- summary: {args.summary}",
            "",
            "## Artifacts",
            "",
            *([f"- {item}" for item in args.artifact] or ["- none listed"]),
        ]
    )
    md_dir = workspace / "pipeline" / "run_logs"
    md_dir.mkdir(parents=True, exist_ok=True)
    (md_dir / f"{timestamp.replace(':', '-')}_{args.stage_id}.md").write_text(markdown + "\n", encoding="utf-8")

    state_path = harness_root / "projects" / cfg["project"]["slug"] / "pipeline" / "pipeline_state.yaml"
    if state_path.exists():
        state = load_yaml(state_path)
        for row in state.get("stages", []):
            if row["id"] == args.stage_id:
                row["status"] = args.status
        dump_yaml(state_path, state)

    print(report_path)


if __name__ == "__main__":
    main()
