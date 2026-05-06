#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_harness(package_root: Path, cfg: dict) -> Path:
    if cfg["harness"].get("local_path"):
        return Path(cfg["harness"]["local_path"]).resolve()
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    if candidate.exists():
        return candidate
    raise SystemExit("Harness not found. Run scripts/clone_harness.py or set harness.local_path.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a final author handoff bundle using manuscript-harness-kit outputs.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("--source-dir", default=None, help="Optional explicit final-output source directory")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    harness_project = harness_root / "projects" / cfg["project"]["slug"]
    profile_id = (
        cfg["journal"].get("generated_profile_id", "").strip()
        or cfg["journal"].get("profile_id", "generic-original-research")
    )
    journal_profile = harness_root / "config" / "journals" / f"{profile_id}.yaml"

    command = [
        "python3",
        str(harness_root / "scripts" / "assemble_submission_folder.py"),
        str(harness_project),
        str(journal_profile),
    ]
    if args.source_dir:
        command.extend(["--source-dir", str(Path(args.source_dir).resolve())])
    subprocess.run(command, check=True, cwd=str(harness_root))

    handoff_root = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"] / "handoff" / "author_packet").resolve()
    handoff_root.mkdir(parents=True, exist_ok=True)
    source_final = harness_project / "submission" / "final_submission"
    if source_final.exists():
        target = handoff_root / "final_submission"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source_final, target)

    readme = "\n".join(
        [
            f"# Author Handoff: {cfg['project']['title']}",
            "",
            f"- target journal: `{cfg['journal']['target_name']}`",
            f"- harness project: `{harness_project}`",
            f"- bundled final submission: `{source_final}`",
            "",
            "## Notes",
            "",
            "- Review the final upload order before submission.",
            "- Confirm the live journal instructions manually.",
            "- If Word live Zotero fields are required, finish that step in the author's Zotero Word environment.",
        ]
    )
    (handoff_root / "README_AUTHOR_HANDOFF.md").write_text(readme + "\n", encoding="utf-8")
    print(handoff_root)


if __name__ == "__main__":
    main()
