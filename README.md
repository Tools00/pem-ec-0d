# PEM-EC Designer

**Interactive PEM Electrolysis Cell Designer & Simulator — running in your browser.**

Physics-based simulation of proton-exchange-membrane water electrolysis cells.
Designed for engineers evaluating stack sizing, operating points, and efficiency
under varying conditions.

Built as a Streamlit single-page app. Works locally, deploys to Streamlit Cloud
with one click.

---

## Features (MVP)

- **Butler-Volmer kinetics** with Tafel approximation for anode (OER) and cathode (HER)
- **Nernst equation** for temperature- and pressure-corrected reversible voltage
- **Ohmic losses** including membrane, GDL, and contact resistances
- **Polarization curve** (U vs. j) with interactive parameter sliders
- **Efficiency metrics**: voltage, Faraday, energy, specific energy (kWh/kg H2)
- **H2 production rate** in mol/s, g/h, L/min
- **CSV export** of operating-point and polarization-curve data
- **Strict SI units** internally, engineering units only in the UI

---

## Physics Model

Cell voltage is assembled as:

```
U_cell = E_rev + η_act,anode + η_act,cathode + η_ohm + η_conc
```

with

- **E_rev** from temperature-corrected Nernst equation
- **η_act** from Butler-Volmer / Tafel with exchange current densities j0,anode, j0,cathode
- **η_ohm** from total cell resistance (membrane via Nafion-thickness/conductivity + contact)
- **η_conc** from mass-transport limit at high current density

All equations documented in `docs/theory/` (copied from standalone reference).

---

## Installation

Requires Python 3.11+.

```bash
cd pem-ec-designer
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run src/streamlit_app.py
```

Opens in browser at http://localhost:8501.

---

## Tests

```bash
pytest tests/ -v
```

Includes:
- Unit-conversion round-trip (SI ↔ engineering)
- Tafel-slope validation at high current densities
- Monotonicity of polarization curve

---

## Validation

MVP-Validierung: Tafel-Slope `b = 2.303 · R·T / (α·F)` wird gegen analytisch
berechneten Wert verglichen. Toleranz < 1 %.

Eine zweite Validation gegen experimentelle Polarisationskurve aus
peer-reviewed Paper folgt in v0.5.

---

## Project Structure

```
pem-ec-designer/
├── src/
│   ├── constants.py        CODATA 2018 constants
│   ├── units.py            SI ↔ engineering unit conversion
│   ├── electrochemistry.py Butler-Volmer, Nernst, Ohm
│   └── streamlit_app.py    Streamlit UI
├── tests/
│   ├── test_electrochemistry.py
│   └── test_units.py
├── docs/
│   ├── theory/             Theory reference (chemistry, governing eqs, materials)
│   ├── references/         Citation files (BibTeX, DOIs)
│   └── validation/         Validation datasets
├── CLAUDE.md               Operating manual for Claude sessions
├── LICENSE                 MIT
└── requirements.txt
```

---

## Roadmap

| Phase | Scope | Timeline |
|---|---|---|
| **MVP (v0.1)** | Core electrochemistry + Streamlit UI + 1 validation | 7 working days |
| v0.5 | Material DB, cost estimator, stack scaling, DE/EN, 2nd validation | +2 weeks |
| v1.0 | ML surrogate, Bayesian optimizer, water management, thermal model | +4 weeks |
| v2.0 | PEMFC variant (separate folder), CFD modules | later |

---

## References

Primary sources (for v0.5 full BibTeX):

- Springer, T. E., Zawodzinski, T. A., & Gottesfeld, S. (1991). *Journal of The Electrochemical Society*, 138(8).
- Larminie, J., & Dicks, A. (2003). *Fuel Cell Systems Explained.* Wiley.
- Barbir, F. (2012). *PEM Fuel Cells: Theory and Practice.* Academic Press.
- Carmo, M., Fritz, D. L., Mergel, J., & Stolten, D. (2013). *International Journal of Hydrogen Energy*, 38(12).

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Author

Abed Qadi — Simulation Engineer.
Questions, collaborations, or feature requests: [Open an issue](https://github.com/).
