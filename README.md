# PEM-EC Designer

[![CI](https://github.com/Tools00/pem-ec-0d/actions/workflows/ci.yml/badge.svg)](https://github.com/Tools00/pem-ec-0d/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**Interactive PEM Electrolysis Cell & Stack Designer — running in your browser.**

Physics-based simulation of proton-exchange-membrane water electrolysis cells and stacks,
including 0D thermal management and material-preset library. Designed for engineers
evaluating cell sizing, stack assembly, operating points, and efficiency under varying
conditions — without needing a commercial CFD license.

Built as a Streamlit single-page app. Works locally, deploys to Streamlit Cloud
with one click.

---

## What's new in v0.5

### Flow-field pressure drop + pump power (Phase 1)

- **`src/fluid.py`** — Hagen-Poiseuille ΔP in laminaren Kanälen +
  explizite Darcy-Weisbach-Warnung bei Re > 2000 (keine stille
  Extrapolation).
- **Anoden-Wasser-Fluss aus Faraday + λ** — stoichiometrische
  Volumen-Flussrate pro Zelle, N Zellen hydraulisch parallel am Stack-
  Manifold.
- **Assembly-Tab: `ΔP [kPa]`, `v [cm/s]`, `Re`, `Pump [W]`, Parasit-Anteil**
  der Stack-Leistung als Metrics. Pump-Leistung fließt nicht (noch) in
  den η-Wert, wird aber transparent daneben gezeigt.

### Rectangular stacks (Phase 2)

- Neues Feld `aspect_ratio` (dimensionslos, default 1.0) auf
  `StackAssembly` — area-preserving: `w·h = active_area_m²`, `w/h = ratio`.
  v0.4-JSONs laden weiter als quadratisch.
- BPP-Außenmaße folgen als `(w + 2·frame, h + 2·frame)` — echte
  rechteckige Plates. Flow-Field-Rendering (alle drei Pattern) richtet
  sich nach den rechteckigen Dimensionen.
- Sidebar-Slider 0.25…4.0, Caption zeigt resultierende w × h.

### Literature validation (Phase 3)

Zero-Fit-Property: nur dokumentierte Betriebsbedingungen (T, p, Membran)
werden als Inputs genutzt — keine kinetischen Parameter auf die
Test-Kurve gefittet.

| Datensatz | Typ | Status |
|---|---|---|
| Bernt 2020 Fig. 1 (2 mg Ir/cm², 80 °C, Nafion 212) | 15 Punkte, ein Setup | Low-j PASS (~35 mV), Full-range strict-xfail @ 510 mV |
| Zimmer 2026 Fig. 1c (N115 + 80 °C, 127 Paper) | Envelope + ±σ, 5 Benchmark j | **Envelope PASS**, ±1σ strict-xfail (+175 mV bias) |

Beide xfails sind dokumentierte v0.6-Kalibrierungsziele
(`docs/validation/bernt2020_v0.5.md`, `docs/validation/zimmer2026_v0.5.md`).
Rationale für die xfail-Strategie: [ADR-007](docs/adr/007-v0.5-architecture.md).

---

## What's in it (v0.4)

### Visual Stack Designer (new in v0.4)

- **Assembly tab** — pick bipolar plate, end plate, current collector, gasket,
  tie-rod from literature-referenced presets
- **Plotly cross-section** — to-scale side view of the full stack in mm, with
  compressed mid-section for N > 6 cells
- **BPP top view** — flow-field pattern (serpentine / parallel / interdigitated)
  with gasket frame and diagonal inlet/outlet ports
- **Stack KPIs** — total height, approximate mass, BPP outer edge, open-area ratio
- **JSON save / load** of the full assembly configuration

See [ADR 006](docs/adr/006-visual-stack-designer.md) for design rationale.

## What's in it (v0.2 core)

### Electrochemistry (cell-level)

- **Butler-Volmer kinetics** (Tafel approximation) for OER on IrO₂ (anode) and HER on Pt (cathode)
- **Nernst equation** with temperature and pressure correction
- **Ohmic losses** (membrane + GDL + contact + bipolar plate)
- **Concentration overpotential** near limiting current density
- **Polarization curve** with interactive parameter control

### Stack assembly

- **N cells in series** — voltage addition, power aggregation, H₂ production
- **Stack-level KPIs** — U_stack, P_electric (kW), m_H₂ (kg/h), η_energy
- **Stack polarization & power curves**

### Thermal management (0D)

- **Thermoneutral voltage** E_tn = ΔH/(n·F) ≈ 1.481 V (HHV basis)
- **Waste-heat generation** per cell and per stack
- **Required coolant flow** from ṁ·cp·ΔT energy balance
- **Exo/endothermic mode detection**

### Materials library (literature-referenced)

- **6 membranes** — Nafion 211/212/115/117, Aquivion E98-05S, Fumapem F-950
- **3 anode catalysts** — IrO₂, IrRuOx, IrO₂-TiO₂ low-loading
- **3 cathode catalysts** — Pt/C, Pt black, PtCo/C alloy
- **4 GDLs** — Ti felt, Ti mesh, carbon paper, carbon cloth

### Output

- **CSV export** of polarization curve and operating-point summary
- **Voltage decomposition table** at operating point
- **All calculations in strict SI**, display in engineering units (°C, bar, A/cm², Ω·cm²)

---

## Physics Model

Cell voltage is assembled as:

```
U_cell = E_rev + η_act,anode + η_act,cathode + η_ohm + η_conc
```

with

- **E_rev** from temperature- and pressure-corrected Nernst equation
- **η_act** from Butler-Volmer / Tafel with exchange current densities j₀,anode, j₀,cathode
- **η_ohm** from area-specific cell resistance (membrane via Nafion thickness/conductivity + GDL + contact + BPP)
- **η_conc** from mass-transport limit at high current density

Stack voltage:  `U_stack = N · U_cell`
Waste heat:     `Q_stack = N · (U_cell − E_tn · η_F) · I`

All equations referenced in `docs/theory/` and in-code `@ref:` annotations.

---

## Quick start

### Requirements

- Python **3.11+**

### Install

```bash
cd pem-ec-0d
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
streamlit run src/streamlit_app.py
```

Opens at http://localhost:8501.

See [docs/INSTALL.md](docs/INSTALL.md) for detailed setup and troubleshooting.

---

## Tests

```bash
pytest tests/ -v
```

**161 tests passing + 2 strict-xfail** in ~2 s. Covers:

- **Tafel-slope validation** against analytical `b = 2.303·R·T/(α·F)` (<0.5 % error)
- **Monotonicity** of polarization curve
- **Nernst consistency** at standard conditions and across T, p
- **Stack aggregation** linearity in N, area-scaling of current
- **Material presets** — preset consistency, Nafion thickness ordering, GDL resistance ranges
- **Thermal balance** — exothermic mode detection, heat-flow conservation, cooling sanity
- **Input validation** — 9 physical-parameter guards

---

## Validation

### Analytical (GREEN)

- Tafel slope `b = 2.303·R·T/(α·F)` matched to < 0.5 %
- U_cell at 80 °C, 10 bar, 1 A/cm²: 1.7–2.1 V (Carmo et al. 2013 Fig. 6)

### Literature (v0.5, zero-fit)

- **Bernt 2020, Fig. 1** — Low-j-Shape PASS bei ~35 mV RMSE (j ≤ 0.1 A/cm²,
  Tafel-Region). Full-range strict-xfail bei 510 mV — R_ohm-Overshoot und
  generisches j₀,Anode unterschätzen das Umicore-Elyst-Ir75-Premium-Setup.
  Dokumentiert in [`docs/validation/bernt2020_v0.5.md`](docs/validation/bernt2020_v0.5.md).
- **Zimmer 2026, Fig. 1c** — aggregierte Literatur, 127 Paper, gefiltert
  auf Nafion N115 + 80 °C. **Envelope-Test PASS** an allen 5 Benchmark-j
  (Model bleibt in [E_min, E_max]). ±1σ-Band strict-xfail mit +175 mV
  Bias. Dokumentiert in [`docs/validation/zimmer2026_v0.5.md`](docs/validation/zimmer2026_v0.5.md).
- **Warum zwei Papers + xfail statt fit:** Calibrating to Bernt würde die
  Zero-Fit-Property der Test-Suite brechen und das Model auf ein
  Premium-Setup coupeln. Zimmer's σ > 500 mV bei gleicher j zeigt, dass
  kein einzelnes Paper als Wahrheit gilt. Rationale in
  [ADR-007](docs/adr/007-v0.5-architecture.md).
- **v0.6-Pfad:** Katalysator-/Kontakt-Resistenz-Preset-System mit
  unabhängig extrahierten kinetischen Parametern. Strict-xfail zwingt
  explizites Re-Baseline, wenn die Kalibrierung landet.

---

## Project Structure

```
pem-ec-0d/
├── src/
│   ├── constants.py        CODATA 2018 constants (R, F, E₀, ΔH, LHV)
│   ├── units.py            SI ↔ engineering unit conversion
│   ├── electrochemistry.py Butler-Volmer, Nernst, Ohm, efficiency
│   ├── stack.py            N-cell serial aggregation
│   ├── thermal.py          0D energy balance + coolant sizing
│   ├── materials.py        Membrane/catalyst/GDL presets with refs
│   ├── components.py       Stack-component presets (BPP, end plate, ...)
│   ├── assembly.py         StackAssembly dataclass + ΔP/pump composition
│   ├── fluid.py            Hagen-Poiseuille / Darcy-Weisbach (v0.5)
│   ├── visualization.py    Plotly cross-section + BPP top view
│   └── streamlit_app.py    Streamlit UI (6 tabs)
├── tests/                  161 pytest tests + 2 strict-xfail (v0.6 targets)
├── docs/
│   ├── HOW-IT-WORKS.md     User-facing guide with screenshots
│   ├── INSTALL.md          Detailed setup + troubleshooting
│   ├── MODEL_CARD.md       Scientific model card (scope, assumptions, validity)
│   ├── KNOWN_ISSUES.md     Honest list of limitations
│   ├── adr/                Architecture Decision Records
│   ├── theory/             Theory reference (chemistry, governing eqs, materials)
│   ├── references/         Citation files
│   └── validation/         Validation datasets (planned v0.5)
├── CHANGELOG.md            SemVer changelog (Keep a Changelog format)
├── CLAUDE.md               Operating manual for Claude sessions
├── CONTRIBUTING.md         Contribution guidelines
├── LICENSE                 MIT
├── pyproject.toml          PEP 621 project metadata
└── requirements.txt        Legacy pinned dependencies (retained for Streamlit Cloud)
```

---

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| **v0.1** | Cell electrochemistry + Streamlit UI + 1 analytical validation | ✅ Done |
| **v0.2** | Stack aggregation, 0D thermal, material presets, tabbed UI | ✅ Done |
| **v0.3** | Springer-Membran-σ(λ, T), Arrhenius-j₀(T), Full-Butler-Volmer | ✅ Done |
| **v0.4** | Visual Stack Designer (Assembly-Tab, presets, JSON save/load), r_bpp wired | ✅ Done |
| **v0.5** | Fluid-Modul (ΔP/pump), rechteckige Stacks, zero-fit Literatur-Validation (Bernt 2020 + Zimmer 2026) | ✅ Done |
| v0.6 | Katalysator- + Kontakt-Resistenz-Preset-System, xfail-Tests grünschalten | Planned |
| v1.0 | Pseudo-2D along-channel + through-MEA, surrogate layer from published CFD data, REST API | Planned |
| v2.0 | 3D exploded-view visualization, parametric CAD for bipolar plates (CadQuery), external OpenFOAM runner | Optional |

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and [docs/adr/002-hybrid-vs-cfd.md](docs/adr/002-hybrid-vs-cfd.md) for the strategic positioning vs. commercial CFD tools (AVL Fire M, ANSYS Fluent, COMSOL, STAR-CCM+).

---

## Positioning vs. Commercial CFD

This tool is **not** a replacement for ANSYS Fluent, COMSOL Multiphysics, Siemens STAR-CCM+, or AVL Fire M. It is a **fast early-stage design tool** that covers ~85–95 % of cell- and stack-performance use cases those tools are used for — at 10⁴× the speed and 10⁴× lower cost — leaving detailed 3D flow-field design and local distribution analysis to the commercial suites.

| Use case | This tool | Commercial CFD |
|---|---|---|
| Polarization curve, η(j), H₂-rate | ✅ ±3–5 % | ✅ ±1–3 % |
| Stack sizing, operating-point optimization | ✅ | ✅ |
| Early-stage design screening | ✅ 1000 variants/min | ❌ days per variant |
| Local current density j(x,y) | ❌ | ✅ |
| Flow-field hotspots, flooding | ❌ | ✅ |
| Certification / final design sign-off | ❌ | ✅ |

---

## References

Primary sources:

- **Larminie & Dicks (2003)** — *Fuel Cell Systems Explained*, 2nd ed. Wiley.
- **Barbir (2012)** — *PEM Fuel Cells: Theory and Practice*, 2nd ed. Academic Press.
- **Carmo, Fritz, Mergel & Stolten (2013)** — *Int. J. Hydrogen Energy* 38(12), 4901–4934.
- **Springer, Zawodzinski & Gottesfeld (1991)** — *J. Electrochem. Soc.* 138(8).
- **Bernt, Siebel & Gasteiger (2018)** — *J. Electrochem. Soc.* 165(5), F305–F314.
- **Kusoglu & Weber (2017)** — *Chem. Rev.* 117(3), 987–1104.
- **Tijani, Yusup & Rahim (2018)** — *Int. J. Hydrogen Energy* 43(20).

Full citation list in `docs/references/` (BibTeX, DOIs).

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

Abed Qadi — Simulation Engineer.
Issues, questions, collaborations → [open an issue on GitHub](https://github.com/Tools00/pem-ec-0d/issues).

---

## Development note

This project is developed with AI-assisted tooling (Claude Code).
Physics, architecture, and scope decisions are human-reviewed; every
equation carries a literature reference, and all results are validated
against analytical checks and published data (see [MODEL_CARD.md](docs/MODEL_CARD.md)).
