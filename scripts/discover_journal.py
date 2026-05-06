#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(lowered.split())


def resolve_harness(package_root: Path, cfg: dict) -> Path:
    local_path = cfg["harness"].get("local_path", "")
    if local_path:
        return Path(local_path).resolve()
    candidate = (package_root / cfg["paths"]["vendor_root"] / "manuscript-harness-kit").resolve()
    if candidate.exists():
        return candidate
    raise SystemExit("Harness not found. Run scripts/clone_harness.py or set harness.local_path.")


def journal_candidates(harness_root: Path, catalog: dict) -> list[dict]:
    profiles = []
    catalog_map = {row["id"]: row for row in catalog.get("journals", [])}
    for path in sorted((harness_root / "config" / "journals").glob("*.yaml")):
        payload = load_yaml(path).get("journal", {})
        journal_id = payload.get("id", path.stem)
        cat = catalog_map.get(journal_id, {})
        aliases = set(cat.get("aliases", []))
        aliases.add(payload.get("display_name", journal_id))
        aliases.add(journal_id)
        profiles.append(
            {
                "id": journal_id,
                "display_name": payload.get("display_name", journal_id),
                "aliases": sorted(a for a in aliases if a),
                "guideline_url": cat.get("guideline_url", ""),
                "path": str(path),
            }
        )
    return profiles


def score_match(target: str, candidate: dict) -> float:
    target_norm = normalize(target)
    best = 0.0
    for alias in candidate["aliases"]:
        alias_norm = normalize(alias)
        if target_norm == alias_norm:
            return 1.0
        best = max(best, difflib.SequenceMatcher(None, target_norm, alias_norm).ratio())
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover likely journal profile matches from the target journal name.")
    parser.add_argument("config", help="Path to engine YAML config")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    harness_root = resolve_harness(package_root, cfg)
    catalog = load_yaml(package_root / "data" / "journal_catalog.yaml")
    candidates = journal_candidates(harness_root, catalog)
    target_name = cfg["journal"]["target_name"]

    scored = []
    for row in candidates:
        score = score_match(target_name, row)
        scored.append({**row, "score": round(score, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    best = scored[0] if scored else None

    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    journal_dir = workspace / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "target_name": target_name,
        "current_profile_id": cfg["journal"].get("profile_id", ""),
        "current_generated_profile_id": cfg["journal"].get("generated_profile_id", ""),
        "best_match": best,
        "matches": scored[: args.top_k],
    }
    (journal_dir / "discovery_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Journal Discovery Report",
        "",
        f"- target journal: {target_name}",
        "",
        "## Best match",
        "",
    ]
    if best:
        lines.extend(
            [
                f"- id: `{best['id']}`",
                f"- display name: `{best['display_name']}`",
                f"- score: `{best['score']}`",
                f"- guideline url: `{best['guideline_url']}`",
                f"- harness profile path: `{best['path']}`",
                "",
            ]
        )
    else:
        lines.extend(["- no match found", ""])
    lines.append("## Top candidates")
    lines.append("")
    for row in scored[: args.top_k]:
        lines.append(f"- `{row['id']}` | score `{row['score']}` | {row['display_name']}")
    (journal_dir / "discovery_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(journal_dir / "discovery_report.json")


if __name__ == "__main__":
    main()
