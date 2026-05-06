#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


DEFAULTS = {
    "article_type": "Original Research",
    "double_blind_review": True,
    "citation_style": "numeric-in-order-of-appearance",
    "citation_rendering": "bracketed_numeric",
    "abstract_word_limit": 350,
    "body_word_limit_excluding_references": 5000,
    "highlights_required": False,
    "title_page_required": True,
    "figure_legends_separate": True,
    "figures_separate": True,
    "tables_separate": True,
    "supplementary_allowed": True,
    "use_harness_default_expected_files": True,
}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_id(value: str) -> str:
    return "-".join(value.lower().strip().replace("_", "-").split())


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an editable profile-mapping template for the target journal.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    journal_dir = workspace / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    existing_snapshot = journal_dir / "profile_snapshot.yaml"
    generated_id = cfg["journal"].get("generated_profile_id", "").strip()
    base_id = generated_id or cfg["journal"].get("profile_id", "").strip() or normalize_id(cfg["journal"]["target_name"])
    payload = {"journal": {"id": base_id, "display_name": cfg["journal"]["target_name"]}}
    payload["journal"].update(DEFAULTS)

    if existing_snapshot.exists():
        snapshot = load_yaml(existing_snapshot).get("journal", {})
        for key in DEFAULTS:
            if key in snapshot:
                payload["journal"][key] = snapshot[key]
        if not generated_id:
            payload["journal"]["id"] = snapshot.get("id", payload["journal"]["id"])
        payload["journal"]["display_name"] = snapshot.get("display_name", payload["journal"]["display_name"])

    outpath = journal_dir / "profile_mapping.yaml"
    outpath.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(outpath)


if __name__ == "__main__":
    main()
