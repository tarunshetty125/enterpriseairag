# Windows Setup Guide — Step by Step

## Prerequisites

1. **Python 3.11+** — Download from [python.org](https://www.python.org/downloads/)
   - During install, check **"Add Python to PATH"**
2. **Node.js 18+** — Download from [nodejs.org](https://nodejs.org/)
3. **Git** — Download from [git-scm.com](https://git-scm.com/download/win)

Verify installations by opening **PowerShell** and running:

```powershell
python --version
node --version
npm --version
git --version
```

---

## Step 1 — Clone the Repository

```powershell
git clone https://github.com/<your-username>/enterprise-ai-financial-platform.git
cd enterprise-ai-financial-platform
```

---

## Step 2 — Automatic Setup (Recommended)

```powershell
python scripts/setup_environment.py
```

This will:
- Create all required data directories
- Create `.env` from `.env.example` (if missing)
- Create the Python virtual environment
- Install all backend dependencies
- Install all frontend dependencies

---

## Step 3 — Start the Backend

Open **PowerShell Terminal 1**:

```powershell
python scripts/run_backend.py
```

Or manually:

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Step 4 — Start the Frontend

Open **PowerShell Terminal 2**:

```powershell
python scripts/run_frontend.py
```

Or manually:

```powershell
cd frontend
npm run dev
```

You should see:

```
  ▲ Next.js 15.x
  - Local: http://localhost:3000
```

---

## Step 5 — Seed the Data (One-Time)

Open **PowerShell Terminal 3** and run these commands one at a time:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/v1/datasets/ingest
```

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/v1/ml/train/risk
```

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/v1/ml/train/segmentation
```

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/v1/knowledge/ingest
```

Each command will return a JSON response. Wait for each to complete before running the next.

---

## Step 6 — Open the Platform

Open your browser and go to:

```
http://localhost:3000
```

---

## Step 7 — Generate an Intelligence Report

1. Click any customer from the dashboard
2. Click **"Generate Customer Report"**
3. Wait for the report to generate (uses Groq AI)
4. Explore the tabs: Risk, Behaviour, Recommendations, Policy Evidence, AI Report

---

## Troubleshooting

### `python` not found

Use `python3` instead, or reinstall Python with **"Add to PATH"** checked.

### `uvicorn` not found

Run it as a module instead:

```powershell
python -m uvicorn app.main:app --reload
```

### PowerShell execution policy error

If `.venv\Scripts\Activate.ps1` fails:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `npm` not recognized

Close and reopen PowerShell after installing Node.js.

### Port already in use

Kill the process using the port:

```powershell
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### FAISS installation fails

This is optional. The platform automatically falls back to NumPy similarity search.

```powershell
pip install faiss-cpu
```

### sentence-transformers installation fails

This is optional. The platform falls back to deterministic hash embeddings.

```powershell
pip install sentence-transformers
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start backend | `python scripts/run_backend.py` |
| Start frontend | `python scripts/run_frontend.py` |
| Full setup | `python scripts/setup_environment.py` |
| Activate venv | `.venv\Scripts\Activate.ps1` |
| Deactivate venv | `deactivate` |
| Run tests | `cd backend && python -m pytest tests/ -v` |
| Check lint | `cd backend && python -m ruff check app/` |
