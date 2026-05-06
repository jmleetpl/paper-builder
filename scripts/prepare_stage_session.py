#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_harness(package_root: Path, cfg: dict) -> Path:
    local_path = cfg["harness"].get("local_path", "")
    if local_path:
        return Path(local_path).resolve()
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    if candidate.exists():
        return candidate
    raise SystemExit("Harness not found. Run scripts/clone_harness.py or set harness.local_path.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a structured stage session packet from the harness runbook.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("stage_id", help="Stage id, e.g. 01_literature_scout")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    harness_project = harness_root / "projects" / cfg["project"]["slug"]
    stage_brief = harness_project / "pipeline" / "stage_briefs" / f"{args.stage_id}.md"
    pipeline_state = harness_project / "pipeline" / "pipeline_state.yaml"
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    outdir = workspace / "pipeline" / "session_packets"
    outdir.mkdir(parents=True, exist_ok=True)

    if not stage_brief.exists():
        raise SystemExit(f"Stage brief not found: {stage_brief}")

    state = load_yaml(pipeline_state) if pipeline_state.exists() else {"stages": []}
    stage_state = next((row for row in state.get("stages", []) if row["id"] == args.stage_id), None)
    packet = "\n".join(
        [
            f"# Stage Session: {args.stage_id}",
            "",
            f"- project: `{cfg['project']['title']}`",
            f"- target journal: `{cfg['journal']['target_name']}`",
            f"- current status: `{stage_state['status'] if stage_state else 'unknown'}`",
            "",
            "## Stage brief",
            "",
            stage_brief.read_text(encoding="utf-8"),
            "",
            "## Session checklist",
            "",
            "- Confirm all upstream artifacts exist before starting.",
            "- Save exact outputs to disk before summarizing them.",
            "- Record the completion in `record_stage_run.py` after finishing.",
        ]
    )
    outpath = outdir / f"{args.stage_id}.md"
    outpath.write_text(packet + "\n", encoding="utf-8")
    print(outpath)


if __name__ == "__main__":
    main()
