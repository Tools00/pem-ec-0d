# How It Works — User Guide

A step-by-step walkthrough for evaluating a PEM electrolyser cell or stack with this tool.
No prior electrochemistry background required, but basic engineering literacy helps.

---

## 1. What this app does

You move sliders in the sidebar to set operating conditions, materials, and stack
geometry. The app computes the steady-state performance and shows:

- How much voltage your stack needs (U_stack in V)
- How much electric power it draws (P in kW)
- How much hydrogen it produces (m_H₂ in g/h or kg/h)
- How much waste heat it generates (Q in kW)
- How much coolant flow you need to remove the heat
- A polarization curve (U vs. j) and a power curve (P vs. j)
- A full breakdown of where the voltage goes (reversible + losses)

All in under a second, on a laptop.

---

## 2. The UI layout

### Sidebar (left) — your inputs

| Section | Controls |
|---|---|
| **Materials** | Dropdown for membrane (Nafion 212, 117, …), anode catalyst (IrO₂, …), cathode catalyst (Pt/C, …), GDLs |
| **Operating conditions** | Temperature (°C), pressure (bar), operating current density (A/cm²) |
| **Stack geometry** | Number of cells, active area per cell (cm²) |
| **Thermal management** | Allowed coolant ΔT, coolant heat capacity cp |

### Main area — your outputs

Top row of 5 KPI cards shows the stack-level headline numbers, then 5 tabs
below for details:

| Tab | What you see |
|---|---|
| **Polarization** | U(j) curve with η_act, η_ohm, η_conc breakdown + E_rev and E_tn reference lines |
| **Stack Analysis** | Stack voltage curve, power curve, full stack summary table |
| **Thermal** | Heat generation, cooling flow, Q(j) curve |
| **Materials** | Currently selected presets + full library reference |
| **Export** | CSV download of polarization curve + operating-point summary |

---

## 3. Typical workflow — "size my 5 kW electrolyser"

### Step 1 — Set operating point

- Temperature: **80 °C** (standard for commercial PEM-EC)
- Pressure: **10 bar** (typical balance-of-plant)
- Operating current density: **1.0 A/cm²** (typical design point)

### Step 2 — Pick materials

- Membrane: **Nafion 212** (50 μm, balanced ohmic/mechanical)
- Anode catalyst: **IrO₂ (commercial)**
- Cathode catalyst: **Pt/C (commercial)**

### Step 3 — Tune stack geometry

Play with **N cells** and **active area** until the top KPI cards show
**P_electric ≈ 5 kW**. A reasonable starting point:

- 20 cells, 100 cm² → check the power KPI
- If too low: increase N or area. If too high: decrease.

### Step 4 — Check thermal feasibility

Go to the **Thermal** tab:

- Look at **Waste heat** — this is what your cooling system has to dissipate
- Look at **Coolant volume flow** — this is what your pump must deliver
- Typical: 5 kW stack → 0.5–1.5 kW waste heat → 1–5 L/min water @ ΔT = 5 K

### Step 5 — Export

Go to the **Export** tab:

- Download the polarization-curve CSV
- Download the operating-point-summary CSV

Both can be opened in Excel/pandas for further analysis.

---

## 4. How to interpret the polarization curve

```
      U_cell [V]
         │
     2.0 ├─┬──────── (loss buildup)
         │ ╲
         │  ╲ ╱─ U_cell (blue, the answer)
     1.7 ├─ +  + η_ohm        (resistive losses grow linearly with j)
         │  + η_act           (Tafel — biggest loss at realistic j)
     1.5 ├─ E_tn ─ ─ ─ ─ ─ ─  (thermoneutral: above = exothermic)
     1.2 ├─ E_rev ─ ─ ─ ─ ─ ─ (reversible floor, no losses)
         │
         └──────────────────→ j [A/cm²]
              0.5       2.0
```

- **E_rev** (bottom dashed line, green): thermodynamic minimum (1.229 V at standard, ~1.18 V at 80 °C, 10 bar)
- **E_tn** (dotted red line): above this, the cell heats up; below, it needs external heat
- **Blue curve**: what the cell actually needs — the sum of the reversible voltage and all overpotentials
- **Gap between blue and E_rev**: total losses → waste heat

**Rule of thumb:** at 1 A/cm², U_cell ≈ 1.8–2.0 V is healthy. Above 2.2 V → something's wrong (membrane too thick, catalyst poor, or contact resistance high).

---

## 5. How to interpret the thermal tab

**Heat generation** Q_stack tells you how big your cooling system needs to be.

- At 1 A/cm² and 20 cells × 100 cm², expect **Q ≈ 0.5–1 kW** of waste heat
- **Cooling flow** (L/min) is the water pump requirement

**Thermal efficiency** ratios:

| Metric | Definition | Meaning |
|---|---|---|
| **η_voltage** (Gibbs) | E_rev / U_cell | Fraction of electric energy stored chemically (useful work) |
| **η_thermal_HHV** | E_tn / U_cell | Higher — includes the latent heat bonus |

**η_energy** (top KPI) uses LHV and Faraday-efficiency, typical 60–75 % for healthy operation.

---

## 6. How to interpret the materials tab

- **"Selected materials"** table: what's active right now
- **"Available presets"** expanders: the whole library you can switch to
- Every entry has a **Reference** column → traceable to a paper

**Changing a material** (sidebar dropdown) immediately updates the whole app.
Try it:

1. Start with Nafion 212 → note U_cell at 1 A/cm²
2. Switch to Nafion 117 (thicker) → U_cell goes up (higher ohmic)
3. Switch to Nafion 211 (thinner) → U_cell goes down

That's the design tradeoff: thin membrane = lower voltage loss, but more gas crossover and mechanical fragility.

---

## 7. Common pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| U_cell > 2.5 V at 1 A/cm² | Membrane too thick, or j₀ too low | Thinner membrane / higher j₀ |
| U_cell < 1.5 V at 1 A/cm² | Unrealistic parameters | Check alpha values (should be 0.4–0.6) |
| Cooling flow > 20 L/min | Too many cells, too high j, or too small ΔT | Reduce N or increase allowed ΔT |
| App errors on concentration | j > j_limiting (default 3 A/cm²) | Reduce operating current density |

---

## 8. What this tool does NOT do

Please read [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for the honest limits:

- No spatial resolution (0D) — can't show where the hotspots are
- No transient dynamics — only steady-state
- No multi-phase flow — assumes no flooding
- No degradation — cell is treated as fresh

For those, you need full CFD (ANSYS Fluent, COMSOL, STAR-CCM+, AVL Fire M) or transient system simulators. This tool is for fast early-stage sizing.

---

## 9. What to do next

- **Feature request or bug?** → open a GitHub issue
- **Want to understand the equations?** → [docs/theory/MASTER_THEORY_REFERENCE.md](theory/MASTER_THEORY_REFERENCE.md)
- **Want to extend the code?** → [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Want to cite this work?** → see the Author section in [../README.md](../README.md)
