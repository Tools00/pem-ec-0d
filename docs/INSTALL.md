# Installation Guide

Detailed setup instructions for development and local use.

## Prerequisites

- **Python 3.11 or newer** — check with `python --version`
- **pip** — bundled with Python
- **git** — for cloning the repo

### Optional

- **uv** or **poetry** — faster dependency management (see below)
- **VS Code** or **PyCharm** — any Python-capable editor

---

## Option A — Standard venv + pip (recommended for Streamlit Cloud compatibility)

```bash
# Clone
git clone https://github.com/USER/pem-ec-designer.git
cd pem-ec-designer

# Virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate          # Windows PowerShell

# Dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/streamlit_app.py

# Run tests
pytest tests/ -v
```

---

## Option B — Modern Python tooling with `uv`

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone
git clone https://github.com/USER/pem-ec-designer.git
cd pem-ec-designer

# Create env and install from pyproject.toml
uv sync

# Run the app
uv run streamlit run src/streamlit_app.py

# Run tests
uv run pytest
```

---

## Verify Installation

Three sanity checks before using the app:

```bash
# 1. Module imports OK
python -c "from src.electrochemistry import Electrochemistry; print('OK')"

# 2. All tests green
pytest tests/ -q
# Expected: "78 passed in <0.5s"

# 3. App starts
streamlit run src/streamlit_app.py
# Then open http://localhost:8501
```

---

## Troubleshooting

### ImportError: attempted relative import with no known parent package

You ran Streamlit with relative imports but without a package context.
The current codebase handles this — if you see this error, you have an
outdated `streamlit_app.py`. Pull the latest `main`.

### ModuleNotFoundError: No module named 'streamlit'

Your venv is not activated, or pip install didn't complete.

```bash
source venv/bin/activate    # make sure (venv) appears in your prompt
pip install -r requirements.txt
```

### Port 8501 already in use

Another Streamlit instance is running. Kill it or use a different port:

```bash
# macOS/Linux: find and kill
lsof -i :8501
kill <PID>

# Or use a different port
streamlit run src/streamlit_app.py --server.port 8502
```

### Tests fail on test_cooling_flow_realistic_for_5kw_stack

This test depends on typical PEM-EC operating parameters. If you tweaked
the default cell/thermal parameters, the sanity bounds may need updating.
Revert `src/constants.py` and `src/electrochemistry.py` defaults to verify.

### App runs but chart is empty / NaN in results

Check that your operating current density is **below** the limiting
current (default j_L = 3 A/cm²). At j ≥ j_L, the concentration
overpotential diverges and U_cell becomes NaN.

### `streamlit` command not found

Your venv is not activated. Activation is per-shell-session — you need to
re-activate after opening a new terminal.

---

## Deploying to Streamlit Cloud

See [docs/DEPLOY.md](DEPLOY.md) (coming in v0.3).

Quick version:

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. "New app" → select repo → main file path: `src/streamlit_app.py`
5. Streamlit Cloud auto-installs from `requirements.txt`

---

## Supported platforms

| Platform | Tested | Notes |
|---|---|---|
| macOS 13+ | ✅ | Primary dev platform |
| Linux (Ubuntu 22.04+) | ✅ | CI runs here |
| Windows 11 + PowerShell | ⚠️ | Should work — activate venv with `venv\Scripts\activate` |
| Python 3.11, 3.12, 3.13 | ✅ | Enforced by CI |
| Python 3.10 and older | ❌ | Uses `list[str]` syntax and other PEP 604 features |

---

## Updating

```bash
cd pem-ec-designer
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
pytest tests/ -q    # verify nothing broke
```
