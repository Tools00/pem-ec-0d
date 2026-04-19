# Contributing to PEM-EC Designer

Thanks for considering a contribution. This is a small, opinionated project —
please read this before opening a PR.

---

## Ground rules

1. **Physics first.** Every equation needs a literature reference in the docstring
   (`@ref:` annotation). No invented formulas.
2. **SI internally.** All calculations use SI units (m, Pa, A/m², K, Ω·m²).
   Only the UI layer displays engineering units, and conversion goes through
   `src/units.py`.
3. **CODATA 2018 constants.** Import from `src/constants.py`. Do not hardcode
   rounded values (`R = 8.314` is a no-go).
4. **Tests before commit.** `pytest tests/ -v` must be green.
5. **No scope creep.** Features not in the current version's scope belong in
   the roadmap, not in a PR. See [README.md](README.md) for scope.

---

## Dev setup

```bash
git clone https://github.com/USER/pem-ec-designer.git
cd pem-ec-designer
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

See [docs/INSTALL.md](docs/INSTALL.md) for details.

---

## Workflow

1. **Open an issue first** for anything larger than a typo. Align on scope
   before writing code.
2. **Branch from `main`** — name it `feat/<short>`, `fix/<short>`, or
   `docs/<short>`.
3. **One PR, one concern.** Don't bundle a refactor with a feature.
4. **Tests alongside code.** Not after.
5. **Commit messages follow Conventional Commits:**
   - `feat:` new user-facing capability
   - `fix:` bug fix
   - `refactor:` no behavior change
   - `test:` adding or fixing tests
   - `docs:` documentation only
   - `chore:` build, CI, tooling
6. **Open a PR** against `main`. CI must pass (pytest + ruff).

---

## Code style

- **Formatter:** `ruff format`
- **Linter:** `ruff check`
- **Line length:** 100
- **Python:** 3.11+ syntax (PEP 604 unions, `list[str]`, etc.)
- **Type hints:** on public functions
- **Docstrings:** on public functions, with `@ref:` for physics

Run before pushing:

```bash
ruff format src/ tests/
ruff check src/ tests/
pytest tests/ -v
```

---

## What kinds of contributions fit

### Yes please

- Validation against published polarization curves (Bernt 2018, García-Valverde 2012, Abdin 2015)
- Additional material presets with full literature references
- 1D membrane (Springer) implementation
- Better plots, better UI, better error messages
- Docs improvements, typo fixes, clearer explanations
- More tests, especially for edge cases

### Needs discussion first (open an issue)

- New physics modules (water management, two-phase, degradation)
- New dependencies
- UI restructuring
- API surface changes

### Out of scope (won't merge)

- 3D CFD, spatial fields, transient simulation — use commercial tools for that
- Commercial tool integrations that require licenses
- Code without literature references for the physics
- Features that break SI discipline

---

## Reporting bugs

Open a GitHub issue with:

- What you did (minimal reproduction)
- What you expected
- What happened
- Python version, OS, browser
- Full traceback if applicable

---

## Reporting physics errors

**These get priority.** If you find a wrong equation, unit mismatch, or a
reference that doesn't actually support the formula:

1. Open an issue labeled `physics-error`
2. Cite the correct source
3. Propose the fix

The project values correctness over shipping velocity.

---

## Questions

Open a GitHub Discussion or an issue with the `question` label.
