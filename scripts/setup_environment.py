#!/usr/bin/env python3
"""Cross-platform environment setup script.

Creates the virtual environment, installs dependencies, and verifies the setup.

Usage:
    python scripts/setup_environment.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _pip(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def _is_windows() -> bool:
    return sys.platform == "win32"


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"

    # Ensure data directories exist
    for directory in [
        project_root / "data" / "raw",
        project_root / "data" / "processed",
        project_root / "data" / "external",
        project_root / "data" / "samples",
        project_root / "data" / "policies",
        project_root / "models",
        project_root / "vectorstore",
    ]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory.relative_to(project_root)}")

    # Copy .env.example to .env if missing
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    if not env_file.exists() and env_example.exists():
        env_file.write_text(
            env_example.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        print("  ✓ .env created from .env.example")
    elif env_file.exists():
        print("  ✓ .env already exists")

    # Backend setup
    venv_dir = backend_dir / ".venv"
    pip = _pip(venv_dir)

    if not venv_dir.exists():
        print("\nCreating backend virtual environment...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
        )
        print("  ✓ Virtual environment created")

    print("\nInstalling backend dependencies...")
    subprocess.run(
        [str(pip), "install", "-e", ".[dev]"],
        cwd=str(backend_dir),
        check=True,
    )
    print("  ✓ Backend dependencies installed")

    # Frontend setup
    if not (frontend_dir / "node_modules").exists():
        print("\nInstalling frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True,
            shell=_is_windows(),
        )
        print("  ✓ Frontend dependencies installed")
    else:
        print("\n  ✓ Frontend dependencies already installed")

    print("\n✅ Setup complete!")
    print("\nStart the backend:")
    print("  python scripts/run_backend.py")
    print("\nStart the frontend:")
    print("  python scripts/run_frontend.py")


if __name__ == "__main__":
    main()
