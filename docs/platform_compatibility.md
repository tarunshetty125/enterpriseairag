# Platform Compatibility

The project runs on both macOS and Windows without source code modifications.

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| macOS 13+ (Intel/Apple Silicon) | ✅ Fully supported | Primary development platform |
| Windows 11 | ✅ Supported | All paths use `pathlib.Path`; no POSIX assumptions |
| Linux | ✅ Expected to work | Same as macOS path handling |

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

## Cross-Platform Setup

```bash
# Works on macOS, Windows (PowerShell), and Linux
python scripts/setup_environment.py
python scripts/run_backend.py
python scripts/run_frontend.py
```

## Platform-Specific Startup (Manual)

### macOS / Linux

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Windows (PowerShell)

```powershell
# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Windows (Command Prompt)

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e ".[dev]"
uvicorn app.main:app --reload

cd frontend
npm install
npm run dev
```

## Path Handling

All file paths in the backend use `pathlib.Path`. No manual `/` or `\\` string concatenation exists in the source code.

- **Config resolution**: `resolve_from_backend()` in `core/config.py` resolves relative paths from the backend root using `pathlib`.
- **SQLAlchemy URL**: Uses `Path.as_posix()` for the SQLite connection string, which SQLAlchemy requires in URI format regardless of platform.
- **Data directories**: All configured via environment variables with relative paths (e.g., `../data/raw`). `pathlib` handles path separator conversion.
- **Model artifacts**: Stored and loaded via `pathlib.Path`. The artifact path in the model registry uses the `str()` of a `Path` object.
- **Vector store**: Index directory created with `Path.mkdir(parents=True, exist_ok=True)`.
- **Prompt templates**: Loaded via `Path.glob("*.md")` and `Path.read_text(encoding="utf-8")`.

## Line Endings

The `.gitattributes` file normalizes all source files to LF (`eol=lf`). This prevents CRLF/LF conflicts on Windows:

- All `.py`, `.ts`, `.tsx`, `.js`, `.json`, `.md`, `.toml`, `.css`, `.html` files → LF
- Binary files (`.png`, `.jpg`, `.joblib`, `.faiss`) → binary (no conversion)

## File Encoding

All text file operations use explicit `encoding="utf-8"`:
- CSV reading: `encoding="utf-8-sig"` (handles Windows BOM)
- CSV writing: `encoding="utf-8"` with `newline=""`
- Prompt templates: `encoding="utf-8"`
- Policy documents: `encoding="utf-8"`
- JSON files: `encoding="utf-8"`

## Dependencies

All Python and Node.js dependencies are cross-platform:

| Dependency | Windows Support |
|------------|----------------|
| FastAPI | ✅ |
| SQLAlchemy | ✅ |
| uvicorn | ✅ |
| scikit-learn | ✅ |
| pandas | ✅ |
| numpy | ✅ |
| joblib | ✅ |
| httpx | ✅ |
| FAISS (faiss-cpu) | ✅ (pip install faiss-cpu) |
| sentence-transformers | ✅ |
| Next.js | ✅ |
| Tailwind CSS | ✅ |

## Known Platform Differences

| Area | Difference | Impact |
|------|-----------|--------|
| Virtual environment | `.venv/bin/` (macOS) vs `.venv/Scripts/` (Windows) | Handled by `scripts/run_backend.py` |
| npm commands | Direct on macOS, requires `shell=True` on Windows | Handled by `scripts/run_frontend.py` |
| File case sensitivity | macOS HFS+ is case-insensitive; NTFS is case-insensitive | All filenames use lowercase/snake_case |
| SQLite path in URL | `as_posix()` normalizes to forward slashes | Required by SQLAlchemy URI format |

## Troubleshooting

### Windows: `uvicorn` not found
Use the full path or run as a module:
```powershell
python -m uvicorn app.main:app --reload
```

### Windows: `npm` commands fail in subprocess
The helper scripts use `shell=True` on Windows to resolve npm via PATH.

### Windows: FAISS installation
```powershell
pip install faiss-cpu
```
If installation fails, the platform falls back to NumPy cosine similarity automatically.

### Windows: sentence-transformers
```powershell
pip install sentence-transformers
```
If installation fails, the platform falls back to deterministic hash embeddings automatically.
