#!/usr/bin/env python3
"""Render all .mmd files in docs/diagrams/ to PNG using mermaid.ink API."""

import base64
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DIAGRAMS_DIR = Path(__file__).resolve().parent.parent / "docs" / "diagrams"

def render(mmd_file: Path) -> None:
    content = mmd_file.read_text()
    encoded = base64.urlsafe_b64encode(content.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{encoded}?type=png&bgColor=white"
    out = mmd_file.with_suffix(".png")
    print(f"  {mmd_file.name} -> {out.name} ... ", end="", flush=True)
    try:
        urllib.request.urlretrieve(url, str(out))
        size_kb = out.stat().st_size / 1024
        print(f"OK ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"FAILED: {e}")

def main():
    files = sorted(DIAGRAMS_DIR.glob("*.mmd"))
    if not files:
        print("No .mmd files found")
        sys.exit(1)
    print(f"Rendering {len(files)} diagrams from {DIAGRAMS_DIR}:\n")
    for f in files:
        render(f)
    print(f"\nDone. PNGs saved in {DIAGRAMS_DIR}")

if __name__ == "__main__":
    main()
