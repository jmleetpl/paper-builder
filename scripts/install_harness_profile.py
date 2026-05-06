#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def build_expected_files(journal: dict) -> dict:
    return {
        "title_page": {"required": journal.get("title_page_required", True), "preferred_names": ["title_page.docx", "title_page.pdf"]},
        "blinded_main_manuscript": {"required": journal.get("double_blind_review", False), "preferred_names": ["main_blinded_manuscript.docx", "main_blinded_manuscript.pdf"]},
        "main_manuscript": {"required": not journal.get("double_blind_review", False), "preferred_names": ["main_manuscript.docx", "main_manuscript.pdf"]},
        "highlights": {"required": journal.get("highlights_required", False), "preferred_names": ["highlights.docx", "highlights.pdf"]},
        "main_tables": {"required": journal.get("tables_separate", True), "preferred_names": ["tables_main.docx", "tables_main.pdf"]},
        "supplementary_tables": {"required": False, "preferred_names": ["supplementary_tables.docx", "supplementary_tables.pdf"]},
        "figure_legends": {"required": journal.get("figure_legends_separate", True), "preferred_names": ["figure_legends.docx", "figure_legends.pdf"]},
        "figures": {"required": journal.get("figures_separate", True), "preferred_names": ["figures.pdf"]},
        "references_ris": {"required": False, "preferred_names": ["references.ris"]},
    }


def build_upload_order(mapping: dict) -> list[str]:
    journal = mapping["journal"]
    return [
        "title_page",
        "blinded_main_manuscript" if journal.get("double_blind_review", False) else "main_manuscript",
        "highlights" if journal.get("highlights_required", False) else "main_tables",
        "main_tables",
        "supplementary_tables",
        "figure_legends",
        "figures",
        "references_ris",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Install a generated journal profile into the linked manuscript harness.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    mapping_path = workspace / "journal" / "profile_mapping.yaml"
    if not mapping_path.exists():
        raise SystemExit("profile_mapping.yaml not found. Run scripts/map_journal_profile.py first.")

    mapping = load_yaml(mapping_path)
    journal = mapping["journal"]
    generated_profile_id = cfg["journal"].get("generated_profile_id", "").strip()
    if generated_profile_id:
        journal["id"] = generated_profile_id
    payload = {"journal": dict(journal)}
    payload["journal"]["upload_order"] = build_upload_order(mapping)
    if journal.get("use_harness_default_expected_files", True):
        payload["journal"]["expected_files"] = build_expected_files(journal)

    profile_id = journal["id"]
    dump_yaml(workspace / "generated" / "journal_profile.generated.yaml", payload)
    dump_yaml(harness_root / "config" / "journals" / f"{profile_id}.yaml", payload)
    print(harness_root / "config" / "journals" / f"{profile_id}.yaml")


if __name__ == "__main__":
    main()
