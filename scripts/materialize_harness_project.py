#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


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


def build_harness_project(cfg: dict) -> dict:
    profile_id = (
        cfg["journal"].get("generated_profile_id", "").strip()
        or cfg["journal"].get("profile_id", "").strip()
        or "generic-original-research"
    )
    return {
        "project": {
            "slug": cfg["project"]["slug"],
            "title": cfg["project"]["title"],
            "topic": cfg["project"]["topic"],
            "study_question": cfg["project"]["study_question"],
            "study_design": cfg["project"]["study_design"],
            "reporting_language": cfg["project"]["reporting_language"],
            "progress_report_language": cfg["project"]["progress_report_language"],
            "generate_korean_progress_reports": cfg["project"]["progress_report_language"] == "ko",
        },
        "data": {
            "primary_dataset": cfg["data"]["primary_dataset"],
            "dictionary": cfg["data"]["dictionary"],
            "metadata": cfg["data"]["metadata"],
        },
        "analysis": {
            "primary_outcome": cfg["analysis"]["primary_outcome"],
            "candidate_predictor_count": cfg["analysis"]["candidate_predictor_count"],
            "preferred_models": cfg["analysis"]["preferred_models"],
            "internal_validation": cfg["analysis"]["internal_validation"],
        },
        "journal": {
            "profile": f"config/journals/{profile_id}.yaml",
            "target_name": cfg["journal"]["target_name"],
        },
        "paths": {
            "output_root": "./projects",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize a manuscript-harness project from engine config.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)

    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    engine_project = build_harness_project(cfg)
    harness_cfg_path = workspace / "generated" / "project.for_harness.yaml"
    dump_yaml(harness_cfg_path, engine_project)

    subprocess.run(
        ["python3", str(harness_root / "scripts" / "init_project.py"), str(harness_cfg_path)],
        check=True,
        cwd=str(harness_root),
    )
    subprocess.run(
        ["python3", str(harness_root / "scripts" / "run_pipeline.py"), str(harness_root / "projects" / cfg["project"]["slug"] / "project.snapshot.yaml")],
        check=True,
        cwd=str(harness_root),
    )

    print(harness_root / "projects" / cfg["project"]["slug"])


if __name__ == "__main__":
    main()
