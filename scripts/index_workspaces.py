#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a simple JSON index of paper-builder workspaces.")
    parser.add_argument("--workspace-root", default=None)
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parents[1]
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else package_root / "workspaces"
    rows = []
    if workspace_root.exists():
        for path in sorted(p for p in workspace_root.iterdir() if p.is_dir()):
            rows.append(
                {
                    "slug": path.name,
                    "has_engine_snapshot": (path / "engine.snapshot.yaml").exists(),
                    "has_journal_intake": (path / "journal" / "journal_intake.md").exists(),
                    "has_profile_mapping": (path / "journal" / "profile_mapping.yaml").exists(),
                    "has_author_handoff": (path / "handoff" / "author_packet").exists(),
                }
            )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
