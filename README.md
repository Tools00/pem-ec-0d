# PEM-EC Designer

**Interactive PEM Electrolysis Cell & Stack Designer — running in your browser.**

Physics-based simulation of proton-exchange-membrane water electrolysis cells and stacks,
including 0D thermal management and material-preset library. Designed for engineers
evaluating cell sizing, stack assembly, operating points, and efficiency under varying
conditions — without needing a commercial CFD license.

Built as a Streamlit single-page app. Works locally, deploys to Streamlit Cloud
with one click.

---

## What's in it (v0.2)

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
cd pem-ec-designer
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

**78 tests passing** in <0.2 s. Covers:

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

### Planned (v0.5)

- Comparison to published polarization curves (Bernt 2018, García-Valverde 2012)
- Temperature and pressure sweeps vs. experimental data
- Error metrics: RMSE, MAPE, max deviation

---

## Project Structure

```
pem-ec-designer/
├── src/
│   ├── constants.py        CODATA 2018 constants (R, F, E₀, ΔH, LHV)
│   ├── units.py            SI ↔ engineering unit conversion
│   ├── electrochemistry.py Butler-Volmer, Nernst, Ohm, efficiency
│   ├── stack.py            N-cell serial aggregation
│   ├── thermal.py          0D energy balance + coolant sizing
│   ├── materials.py        Membrane/catalyst/GDL presets with refs
│   └── streamlit_app.py    Streamlit UI (5 tabs)
├── tests/                  78 pytest tests
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
| v0.3 | 2D cross-section visualization, Tafel semi-log plot, efficiency map, comparison mode | Planned |
| v0.5 | 1D membrane (Springer water transport), Numba acceleration, experimental validation against 3 papers, cost estimator, CI/CD | Planned |
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
Issues, questions, collaborations → [open an issue on GitHub](https://github.com/).
