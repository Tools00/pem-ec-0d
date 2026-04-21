# Brief: Visual Stack Designer — Implementation Plan

You are a senior engineer. Produce a concrete, actionable implementation plan for a visual PEM-electrolysis stack designer inside an existing Streamlit app. Output is a Markdown file the main developer reads directly — no chit-chat, no reasoning narrative, only the plan.

---

## Project context (READ CAREFULLY BEFORE PLANNING)

- **Repo:** `pem-ec-0d` (Python 3.11+, Streamlit + Plotly, pytest). GitHub `Tools00/pem-ec-0d`.
- **Stage:** v0.3.0 released. MVP physics complete (Butler-Volmer, Nernst, Ohm, Springer σ(λ,T), Arrhenius j₀(T)). 98 tests green.
- **Scope rule (CLAUDE.md, non-negotiable):** No CFD, no 3D, no React/JS frontend in *this* project. Stays inside Streamlit. SI units strict internally; engineering units only at UI layer.
- **Material presets are hardcoded** (see inventory below). SQLite migration is a v0.5 item — plan must assume presets stay as Python dicts for now.
- **UI today:** 5 tabs (Polarization · Stack Analysis · Thermal · Materials · Export). Sidebar holds all sliders (T, p, j, hydration, active area, cell count).

## Data the app already has (use as source of truth for dimensions)

### Membranes (6 presets) — thickness, σ, λ_max, EW

| Name | Dicke [μm] | σ [S/m] | λ_max | EW [g/mol] |
|---|---|---|---|---|
| Nafion 211 | 25.4 | 10.0 | 22 | 1100 |
| Nafion 212 | 50.8 | 10.0 | 22 | 1100 |
| Nafion 115 | 127 | 10.0 | 22 | 1100 |
| Nafion 117 | 183 | 10.0 | 22 | 1100 |
| Aquivion E98-05S | 50 | 12.0 | 20 | 980 |
| Fumapem F-950 | 50 | 11.0 | 21 | 950 |

### Anode catalysts (OER, 3 presets)
| Name | j₀ [A/m²] | α | Loading [mg/cm²] | E_a [kJ/mol] |
|---|---|---|---|---|
| IrO₂ (commercial) | 10 | 0.50 | 2.0 | 52 |
| IrRuOx | 50 | 0.55 | 1.5 | 48 |
| IrO₂-TiO₂ low-loading | 5 | 0.45 | 0.4 | 56 |

### Cathode catalysts (HER, 3 presets)
| Name | j₀ [A/m²] | α | Loading [mg/cm²] | E_a [kJ/mol] |
|---|---|---|---|---|
| Pt/C | 1000 | 0.5 | 0.4 | 25 |
| Pt black | 2000 | 0.5 | 1.0 | 20 |
| PtCo/C | 1500 | 0.5 | 0.3 | 22 |

### GDL/PTL (2 anode + 2 cathode)
| Name | Side | Thickness [mm] | Porosity | r [Ω·m²] |
|---|---|---|---|---|
| Ti felt | Anode | 1.00 | 0.70 | 2e-6 |
| Ti mesh | Anode | 0.50 | 0.60 | 1.5e-6 |
| Toray TGP-H-060 | Cathode | 0.19 | 0.78 | 1e-6 |
| Carbon cloth ELAT | Cathode | 0.40 | 0.85 | 8e-7 |

### Operating ranges (UI sliders)
- T: 30–90 °C · p: 1–30 bar · j: 0.01–2.5 A/cm² · λ/λ_max: 0.30–1.00 · A: 1–500 cm² · N_cells: 1–200

## Components that are NOT modeled today (must be added for the designer)

- **Bipolar plate (BPP)** — material (Ti / graphite / stainless), thickness, flow-field pattern (serpentine / parallel / interdigitated), channel width, channel depth, channel pitch, land width.
- **End plate** — material, thickness.
- **Current collector** — material, thickness.
- **Gasket** — material (PTFE/EPDM), thickness.
- **Tie-rods** — count, diameter.
- **Ports/manifolds** — inlet/outlet diameter, position on BPP.

These will need new `ComponentSpec` dataclasses + realistic preset values from literature (Carmo 2013, Barbir 2012, Lettenmeier 2016 are already cited elsewhere in the repo — prefer those).

## Target feature (what the designer must do)

Let a user assemble a stack visually and see real-thickness-scaled geometry, with live coupling to the existing physics tabs:

1. **Layer-stack cross-section (side view):** End plate → Current collector → BPP → GDL → Catalyst layer → Membrane → Catalyst layer → GDL → BPP → (repeat for N cells) → Current collector → End plate. Thicknesses to scale. Hover → thickness + material + ref.
2. **BPP top view:** Flow-field SVG pattern (serpentine / parallel / interdigitated), adjustable channel width + pitch + depth. Ports at configurable corners.
3. **Gasket outline** overlaid on BPP top view with cut-out for active area.
4. **Component picker:** Dropdowns for each component (BPP material, flow pattern, gasket material, etc.). Dimension sliders for non-preset values. Saving / loading full "assembly" configs to/from JSON.
5. **Live coupling:** Changing a BPP material updates contact resistance; changing membrane preset updates layer-stack thickness visually AND the Polarization tab; active area slider sets BPP + gasket + layer widths.

## Technical constraints

- Pure Streamlit + Plotly. No JS components. No external drawing canvas unless it's a pip-installable Streamlit component with zero config (e.g., `streamlit-plotly-events` is acceptable; React/dnd-kit is NOT).
- Must not break the existing 5-tab layout. Add as a 6th tab, OR split Materials into Materials + Assembly — justify your choice.
- Must reuse existing `materials.py` specs as the source of dimensions. Do not duplicate presets.
- All new code under `src/`. New tests under `tests/`. Keep SI units internally.
- Ruff-clean, pytest-green before merge. No new heavy deps (>50 MB).
- Follow existing Conventional Commits and ADR pattern (`docs/adr/NNN-title.md`).

---

## What you must produce (strict output format)

Write a single Markdown document with EXACTLY these sections, in order. No preamble, no epilogue, no "here is the plan" — just the content.

```markdown
# Visual Stack Designer — Implementation Plan

## 1. Component inventory (new specs to add)
For each new component (BPP, end plate, current collector, gasket, tie-rod, flow field):
- Proposed `dataclass` name, fields with SI units and types
- 2–4 realistic presets with literature references
- Validity range where applicable

## 2. File structure (new & modified files)
Full tree under `src/` and `tests/`. For each NEW file: 1-line purpose. For each MODIFIED file: what changes.

## 3. Function signatures (public API of new modules)
Full Python type-hinted signatures for:
- `src/components.py` (new BPP/gasket/end-plate/tie-rod specs)
- `src/visualization.py` (drawing functions)
- `src/assembly.py` (optional orchestration layer)
Include one-line docstrings. No implementation.

## 4. UI layout
Exact Streamlit widget plan for the Assembly tab: columns, widgets, which existing sidebar sliders are reused, which new widgets are added. Include a rough ASCII wireframe.

## 5. Coupling to existing physics
Specific list of where the designer's choices feed back into `electrochemistry.py` / `stack.py` / `thermal.py`. Concretely: which field of which preset becomes which input variable. Flag fields that currently have no physics consumer — those are display-only.

## 6. Implementation phases (day-by-day, max 5 days)
Phase 1: … (day 1–2)
Phase 2: … (day 3)
…
Each phase ends with a commit-worthy deliverable and a pytest check.

## 7. Test plan
New pytest cases for: component-spec validation, thickness-sum consistency (layer-stack height == sum of presets), JSON save/load roundtrip, flow-field pattern parametrization.

## 8. Risks and open questions
Bulleted list. Include at least:
- How to handle active area vs BPP area (they differ — gasket takes the delta)
- How to render N=1..200 cells without Plotly choking (answer needed)
- Whether Materials tab is replaced or kept alongside
- Licensing for any component image assets (if used)
- One thing I am uncertain about and want the main developer to decide

## 9. Out-of-scope (do NOT implement in this plan)
Explicitly list 3–5 things that belong in v0.5 or later, so scope creep is prevented (examples: real BPP CAD import, multi-cell CFD coupling, manufacturing DFM checks).
```

## Style rules for the plan you produce

- No filler, no "it is important to note", no summaries at the start or end.
- Code blocks for signatures, file trees, wireframes.
- Tables for component presets.
- Every numeric value with SI unit and a reference where possible.
- If a section needs a decision and you have two reasonable options, pick one and state the tradeoff in one line.
- Plan must be buildable by one person in 3–5 working days.

Begin the plan now.
