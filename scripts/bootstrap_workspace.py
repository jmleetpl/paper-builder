#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a paper-builder workspace from engine config.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    workspace_root = (package_root / cfg["paths"]["workspace_root"]).resolve()
    slug = cfg["project"]["slug"]
    project_root = workspace_root / slug

    subdirs = [
        "inputs",
        "journal",
        "generated",
        "pipeline",
        "handoff",
        "logs",
        "notes",
    ]
    for subdir in subdirs:
        (project_root / subdir).mkdir(parents=True, exist_ok=True)

    shutil.copy2(config_path, project_root / "engine.snapshot.yaml")
    for template_name in ["journal_intake.md", "study_blueprint.md", "idea_funnel.md", "profile_mapping.example.yaml"]:
        src = package_root / "templates" / template_name
        dest_name = {
            "journal_intake.md": "journal/journal_intake.md",
            "study_blueprint.md": "generated/study_blueprint.md",
            "idea_funnel.md": "generated/idea_funnel.md",
            "profile_mapping.example.yaml": "journal/profile_mapping.example.yaml",
        }[template_name]
        shutil.copy2(src, project_root / dest_name)

    readme = "\n".join(
        [
            f"# {cfg['project']['title']}",
            "",
            f"- slug: `{cfg['project']['slug']}`",
            f"- topic: `{cfg['project']['topic']}`",
            f"- target journal: `{cfg['journal']['target_name']}`",
            f"- harness mode: `{cfg['harness']['mode']}`",
            "",
            "## Workspace folders",
            "",
            *[f"- `{name}/`" for name in subdirs],
        ]
    )
    (project_root / "README_WORKSPACE.md").write_text(readme + "\n", encoding="utf-8")
    print(project_root)


if __name__ == "__main__":
    main()
