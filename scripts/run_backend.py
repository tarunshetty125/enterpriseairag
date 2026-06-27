#!/usr/bin/env python3
"""Cross-platform backend startup script.

Usage:
    python scripts/run_backend.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    venv_dir = backend_dir / ".venv"

    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
        uvicorn = venv_dir / "Scripts" / "uvicorn.exe"
    else:
        python = venv_dir / "bin" / "python"
        uvicorn = venv_dir / "bin" / "uvicorn"

    if not python.exists():
        print(f"Virtual environment not found at {venv_dir}")
        print("Create it with:")
        print(f"  cd {backend_dir}")
        print("  python -m venv .venv")
        print('  pip install -e ".[dev]"')
        sys.exit(1)

    cmd = [str(uvicorn), "app.main:app", "--reload"]
    if not uvicorn.exists():
        cmd = [str(python), "-m", "uvicorn", "app.main:app", "--reload"]

    print(f"Starting backend from {backend_dir}")
    subprocess.run(cmd, cwd=str(backend_dir), check=False)


if __name__ == "__main__":
    main()
