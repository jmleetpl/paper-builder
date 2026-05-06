#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import yaml


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.parts)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extension_from_headers(url: str, content_type: str) -> str:
    lowered = content_type.lower()
    if "pdf" in lowered or url.lower().endswith(".pdf"):
        return ".pdf"
    if "html" in lowered or url.lower().endswith((".htm", ".html")):
        return ".html"
    return ".txt"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a journal guide URL into the paper-builder workspace.")
    parser.add_argument("config", help="Path to engine YAML config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    package_root = Path(__file__).resolve().parents[1]
    cfg = load_yaml(config_path)
    url = cfg["journal"].get("guideline_url", "").strip()
    if not url:
        raise SystemExit("No journal.guideline_url set in the engine config.")

    workspace = (package_root / cfg["paths"]["workspace_root"] / cfg["project"]["slug"]).resolve()
    journal_dir = workspace / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "paper-builder/0.2 (+https://github.com/jmleetpl/paper-builder)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        ext = extension_from_headers(url, content_type)
        raw_path = journal_dir / f"guideline_source{ext}"
        raw_path.write_bytes(payload)
        meta = {
            "url": url,
            "content_type": content_type,
            "content_length": len(payload),
            "saved_path": str(raw_path),
        }
        (journal_dir / "guideline_fetch_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        if ext == ".html":
            text = payload.decode("utf-8", errors="ignore")
            parser_obj = TextExtractor()
            parser_obj.feed(text)
            cleaned = re.sub(r"\n{3,}", "\n\n", parser_obj.get_text())
            (journal_dir / "guideline_notes.md").write_text(cleaned + "\n", encoding="utf-8")

    print(raw_path)


if __name__ == "__main__":
    main()
