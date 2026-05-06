#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_harness(package_root: Path, cfg: dict) -> Path | None:
    if cfg["harness"]["local_path"]:
        return Path(cfg["harness"]["local_path"]).resolve()
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    return candidate if candidate.exists() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a journal intake packet for a paper-builder workspace.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    intake = workspace / "journal" / "journal_intake.md"

    lines = [
        "# Journal Intake",
        "",
        f"- target journal: {cfg['journal']['target_name']}",
        f"- journal profile id: {cfg['journal'].get('profile_id', '')}",
        f"- guideline url: {cfg['journal'].get('guideline_url', '')}",
        "- article type: ",
        "- abstract limit: ",
        "- body limit: ",
        "- title page required: ",
        "- highlights required: ",
        "- figures separate: ",
        "- tables separate: ",
        "- notes: ",
        "",
        "## Next step",
        "",
        "- Confirm journal instructions manually or paste them into `journal/guideline_notes.md`.",
        "- If a harness profile already exists, compare it with the live guide before final submission formatting.",
    ]
    intake.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if cfg["journal"].get("guideline_url"):
        (workspace / "journal" / "guideline_source.txt").write_text(cfg["journal"]["guideline_url"] + "\n", encoding="utf-8")

    harness_root = resolve_harness(package_root, cfg)
    profile_id = cfg["journal"].get("profile_id")
    if harness_root and profile_id:
        source_profile = harness_root / "config" / "journals" / f"{profile_id}.yaml"
        if source_profile.exists():
            shutil.copy2(source_profile, workspace / "journal" / "profile_snapshot.yaml")

    print(intake)


if __name__ == "__main__":
    main()
