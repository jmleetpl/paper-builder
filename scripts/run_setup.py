#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, check=True, cwd=str(cwd))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the paper-builder setup sequence end-to-end.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-materialize", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)

    run(["python3", "scripts/bootstrap_workspace.py", str(config_path)], package_root)
    run(["python3", "scripts/clone_harness.py"], package_root)
    run(["python3", "scripts/create_journal_intake.py", str(config_path)], package_root)
    run(["python3", "scripts/discover_journal.py", str(config_path)], package_root)
    if cfg["journal"].get("guideline_url") and not args.skip_fetch:
        run(["python3", "scripts/fetch_journal_guide.py", str(config_path)], package_root)
    run(["python3", "scripts/map_journal_profile.py", str(config_path)], package_root)
    run(["python3", "scripts/install_harness_profile.py", str(config_path)], package_root)
    if not args.skip_materialize:
        run(["python3", "scripts/materialize_harness_project.py", str(config_path)], package_root)
        run(["python3", "scripts/prepare_stage_session.py", str(config_path), "01_literature_scout"], package_root)
    run(["python3", "scripts/preflight_check.py", str(config_path)], package_root)


if __name__ == "__main__":
    main()
