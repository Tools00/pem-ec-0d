# Model Card — PEM-EC Designer

Scientific description of the simulation model, its scope, assumptions, and
validity. Inspired by the Model Cards framework (Mitchell et al., 2019) adapted
for physics-based simulation rather than ML.

**Version:** 0.3.0
**Date:** 2026-04-20
**Authors:** Abed Qadi (with AI-assisted implementation)

---

## 1. Intended use

### Primary use cases

- **Early-stage PEM-EC cell sizing** — pick membrane, catalysts, area, operating point
- **Stack-level performance estimation** — voltage, power, hydrogen output for given N cells
- **Thermal management sizing** — waste heat, cooling-loop requirement
- **Sensitivity analysis** — effect of temperature, pressure, material choice on performance
- **Engineering education** — visualize where the voltage losses go

### Not intended for

- Final design validation (use ANSYS Fluent, COMSOL, STAR-CCM+, AVL Fire M)
- Degraded-cell performance prediction (no aging model)
- Transient behavior (start-up, load-following, shutdown)
- Local flow-field optimization
- Safety certification
- Commercial product warranty calculations

---

## 2. Model scope & approach

### Physical dimensionality: 0D (lumped, zero-dimensional)

All quantities are treated as uniform across the cell. No spatial variation.
Stack extension adds aggregation but no spatial coupling between cells.

### Steady-state

No time dependence. Operating point is assumed instantaneously achieved and stable.

### Governing equations

| Domain | Equation | Reference |
|---|---|---|
| Thermodynamics | Nernst (T + p corrected) | Larminie & Dicks (2003), Eq. 2.22 |
| Kinetics | **Full Butler-Volmer** (Newton-inverted, no Tafel approx.) | Bard & Faulkner (2001), Eq. 3.3.11; ADR 005 |
| j₀ temperature dep. | **Arrhenius**: j₀(T) = j₀_ref · exp(−E_a/R·(1/T − 1/T_ref)) | Carmo et al. (2013), Eq. 9; ADR 004 |
| Membrane conductivity | **Springer (1991)**: σ(λ, T) = (0.005139·λ − 0.00326)·exp(1268·(1/303 − 1/T)) | Springer et al. (1991), Eq. 23; ADR 003 |
| Ohmic transport | Ohm's law, area-specific | Barbir (2012), Ch. 2 |
| Mass transport | Concentration overpotential | Larminie & Dicks (2003), Eq. 3.36 |
| Energy balance | Thermoneutral-voltage formulation | Tijani et al. (2018), IJHE 43 |
| Stack aggregation | Electrical series | Barbir (2012), Ch. 6 |

---

## 3. Assumptions (explicit)

### Always assumed

- **Isothermal** cell (no internal temperature gradient)
- **Isobaric** cell (anode and cathode at same pressure)
- **Liquid water** supply (water activity ≈ 1 on the anode side)
- **Constant Faraday efficiency** (default 98 %)
- **Single rate-determining electron-transfer step** per electrode
  (α_forward + α_backward = 1 in the Butler-Volmer form)
- **No gas crossover effects on voltage**
- **Ideal gas behavior** for Nernst pressure term
- **Linear stack aggregation** (all cells identical, no inhomogeneity)
- **No bubble effects** on electrolyte conductivity

### Assumptions that users can override

- Membrane thickness, λ_max, E_w → via material preset or explicit value
- **Membrane hydration ratio λ/λ_max** → UI slider (0.30–1.00), feeds Springer σ(λ, T)
- Catalyst j₀_ref, α, **E_a (activation energy)** → via material preset; j₀(T) auto-corrected
- GDL resistance → via material preset
- Operating T, p, j → via sidebar sliders
- Coolant cp, ΔT → via sidebar

---

## 4. Validation status

### Green (validated)

| Check | Method | Tolerance | Status |
|---|---|---|---|
| Tafel slope at high j | vs. analytical b = 2.303·R·T/(α·F) — BV→Tafel limit | < 0.5 % | ✅ passing |
| Butler-Volmer roundtrip | η = solve(j) → j = BV(η) recovers j | < 1e-8 | ✅ passing |
| BV → Tafel at high η | |j_BV − j_Tafel| / j_Tafel at η = 0.5 V | < 1e-6 | ✅ passing |
| Springer σ at 303 K, λ = 22 | vs. literature 10.98 S/m | rel_tol 1e-9 | ✅ passing |
| Springer T-ratio σ(353)/σ(303) | vs. Arrhenius-like 1.6–2.0 | bracket | ✅ passing |
| Arrhenius IrO₂ drop at RT | j₀(298)/j₀(353) with E_a=52 kJ/mol | 0.03–0.08 | ✅ passing |
| E_rev at standard conditions | vs. 1.229 V literature | abs_tol 1e-9 | ✅ passing |
| dE_rev/dT | vs. -0.846 mV/K literature | rel_tol 1e-6 | ✅ passing |
| U_cell at 80 °C, 10 bar, 1 A/cm² | vs. Carmo 2013 Fig. 6 | 1.6–2.2 V plausible | ✅ passing |
| Stack linearity in N | U_stack = N·U_cell | rel_tol 1e-12 | ✅ passing |
| Heat-balance conservation | ṁ·cp·ΔT = Q | rel_tol 1e-12 | ✅ passing |
| H₂ scaling with area | linear | rel_tol 1e-9 | ✅ passing |

### Amber (plausible but not experimentally validated)

- **Absolute polarization curve** — values fall within literature range but have not been
  compared point-by-point to a specific experiment
- **Thermal efficiency** — formula correct, magnitudes plausible, no experimental comparison yet
- **Cooling-flow predictions** — consistent with energy balance, no field-data comparison

### Red (not validated)

- **Concentration overpotential magnitude** — uses a generic limiting-current form,
  not calibrated to a specific catalyst/GDL combination
- **Multi-phase effects** — not modeled at all
- **Long-term performance** — no aging mechanism

---

## 5. Known limitations & domain of validity

### Operating range where the model is trustworthy

| Parameter | Valid range | Confidence outside |
|---|---|---|
| Temperature | 30–90 °C | Membrane data thin below 25 °C; Arrhenius extrapolation OK within [273, 423] K |
| Pressure | 1–30 bar | Above 30 bar: ideal gas assumption deteriorates |
| Current density | 0.01–2.5 A/cm² | Full BV handles low-j regime; above 2.5: needs better j_lim |
| Membrane hydration | λ > 5 (UI slider ≥ 0.30) | Below λ ≈ 0.63: Springer yields non-physical σ, guard raises ValueError |

### Known systematic errors

- **E_a literature scatter ±15 %** for some catalysts — translates to ±5 %
  j₀ error when |T − T_ref| > 30 K
- **Underpredicts ohmic losses** if contact resistance is poorly specified
- **No correction** for cell-to-cell variability in stack operation
- **No correction** for pressure-drop across the flow field
- **Nafion-specific σ correlation applied to non-Nafion PFSA membranes**
  (Aquivion, Fumapem) — accurate to ~10 % but not material-specific

---

## 6. Reproducibility

- **Deterministic** — no random components
- **Version-pinned dependencies** — see `requirements.txt`
- **Physical constants** — CODATA 2018 (`src/constants.py`)
- **All equations sourced** — `@ref:` annotations in every public function
- **Tests document expected behavior** — 98 tests, all green

Given the same inputs and the same commit hash, the model produces
byte-identical outputs.

---

## 7. Comparison to commercial tools

| Capability | This tool (v0.3) | Full CFD (ANSYS/COMSOL/STAR-CCM+/AVL) |
|---|---|---|
| Cell-level U(j) accuracy | ±5–10 % (unvalidated against exp.) | ±1–3 % |
| Stack aggregation | Linear, exact | Can handle non-uniformity |
| Thermal (0D lumped) | ±10 % on waste heat | ±2 % with FEM |
| Runtime per point | < 100 ms | hours to days |
| Spatial fields (j(x,y), T(x,y)) | ❌ none | ✅ full |
| Transient | ❌ | ✅ |
| Multi-phase | ❌ | ✅ |
| 3D geometry | ❌ | ✅ |
| Cost / license | $0, MIT | €15k–70k/year + HPC |

---

## 8. How to cite

```bibtex
@software{qadi_pem_ec_designer_2026,
  author  = {Qadi, Abed},
  title   = {{PEM-EC Designer: Physics-Based Simulation of PEM Water Electrolysis}},
  version = {0.3.0},
  year    = {2026},
  url     = {https://github.com/Tools00/pem-ec-0d}
}
```

---

## 9. Ethics & responsible use

- This tool is for **engineering education and early-stage design**, not for
  safety-critical decisions
- **Do not** rely on its outputs for commissioning real electrolyser systems
  without independent expert review
- **Do not** use numerical results as-is in regulatory filings — commercial
  CFD and/or experimental data is required

If in doubt: ask a senior electrochemist.

---

## 10. Contact & feedback

Issues or questions → GitHub issue tracker (see [README.md](../README.md)).
