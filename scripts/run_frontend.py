#!/usr/bin/env python3
"""Cross-platform frontend startup script.

Usage:
    python scripts/run_frontend.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    use_shell = sys.platform == "win32"

    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True,
            shell=use_shell,
        )

    print(f"Starting frontend from {frontend_dir}")
    subprocess.run(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        check=False,
        shell=use_shell,
    )


if __name__ == "__main__":
    main()
