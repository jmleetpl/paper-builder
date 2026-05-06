#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def expected_prefix(index: int, key: str) -> str:
    return f"{index:02d}_{key}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the assembled author handoff submission packet.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("--handoff-root", default=None, help="Optional explicit author_packet directory")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    profile_id = cfg["journal"].get("generated_profile_id", "").strip() or cfg["journal"].get("profile_id", "generic-original-research")
    journal = load_yaml(harness_root / "config" / "journals" / f"{profile_id}.yaml")["journal"]

    if args.handoff_root:
        handoff_root = Path(args.handoff_root).resolve()
    else:
        handoff_root = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"] / "handoff" / "author_packet").resolve()
    upload_dir = handoff_root / "final_submission" / "UPLOAD_FILES"
    figures_dir = handoff_root / "final_submission" / "FIGURES_INDIVIDUAL"

    report = {
        "handoff_root": str(handoff_root),
        "upload_dir_exists": upload_dir.exists(),
        "figures_dir_exists": figures_dir.exists(),
        "required_files": [],
        "missing_files": [],
        "unexpected_files": [],
        "figure_count": 0,
        "valid": True,
    }

    present_files = sorted(p.name for p in upload_dir.glob("*")) if upload_dir.exists() else []
    allowed_prefixes = []
    for idx, key in enumerate(journal.get("upload_order", []), start=1):
        meta = journal.get("expected_files", {}).get(key, {})
        required = meta.get("required", False)
        prefix = expected_prefix(idx, key)
        allowed_prefixes.append(prefix)
        matched = [name for name in present_files if name.startswith(prefix + ".") or name.startswith(prefix)]
        report["required_files"].append({"key": key, "required": required, "matched": matched})
        if required and not matched:
            report["missing_files"].append(key)

    for name in present_files:
        stem = Path(name).stem
        if not any(stem.startswith(prefix) for prefix in allowed_prefixes):
            report["unexpected_files"].append(name)

    if figures_dir.exists():
        report["figure_count"] = len([p for p in figures_dir.glob("*") if p.is_file()])
    if journal.get("figures_separate", False) and report["figure_count"] == 0:
        report["missing_files"].append("individual_figures")

    report["valid"] = len(report["missing_files"]) == 0

    validation_dir = handoff_root / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    json_path = validation_dir / "submission_validation.json"
    md_path = validation_dir / "submission_validation.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Submission Validation",
        "",
        f"- valid: `{report['valid']}`",
        f"- figure count: `{report['figure_count']}`",
        "",
        "## Missing required items",
        "",
        *([f"- {item}" for item in report["missing_files"]] or ["- none"]),
        "",
        "## Unexpected files",
        "",
        *([f"- {item}" for item in report["unexpected_files"]] or ["- none"]),
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)


if __name__ == "__main__":
    main()
