#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def which_ok(name: str) -> bool:
    return shutil.which(name) is not None


def gh_auth_ok() -> bool:
    if not which_ok("gh"):
        return False
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    return result.returncode == 0


def resolve_harness(package_root: Path, cfg: dict) -> str:
    local_path = cfg["harness"].get("local_path", "")
    if local_path:
        return str(Path(local_path).resolve())
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    return str(candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run environment and dependency checks for paper-builder.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_path = Path(resolve_harness(package_root, cfg))
    zotero_db = Path("/Users/macair/Zotero/zotero.sqlite")
    profiles_ini = Path("/Users/macair/Library/Application Support/Zotero/profiles.ini")

    report = {
        "python": which_ok("python3"),
        "git": which_ok("git"),
        "gh": which_ok("gh"),
        "gh_auth": gh_auth_ok(),
        "harness_path": str(harness_path),
        "harness_exists": harness_path.exists(),
        "zotero_db_exists": zotero_db.exists(),
        "zotero_profiles_exists": profiles_ini.exists(),
        "guideline_url_present": bool(cfg["journal"].get("guideline_url", "").strip()),
        "workspace_exists": (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).exists(),
        "journal_intake_exists": (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"] / "journal" / "journal_intake.md").exists(),
        "profile_mapping_exists": (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"] / "journal" / "profile_mapping.yaml").exists(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
