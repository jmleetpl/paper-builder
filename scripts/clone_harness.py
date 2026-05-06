#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone manuscript-harness-kit into the local vendor directory.")
    parser.add_argument("--repo-url", default="https://github.com/jmleetpl/manuscript-harness-kit.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--vendor-root", default=None)
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parents[1]
    vendor_root = Path(args.vendor_root).resolve() if args.vendor_root else package_root / "vendor"
    vendor_root.mkdir(parents=True, exist_ok=True)
    target = vendor_root / "manuscript-harness-kit"

    if target.exists():
        print(target)
        return

    subprocess.run(
        ["git", "clone", "--branch", args.branch, "--depth", "1", args.repo_url, str(target)],
        check=True,
    )
    print(target)


if __name__ == "__main__":
    main()
