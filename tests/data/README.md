# Validation datasets

## bernt_2020_fig1.csv

**Source:** Bernt, M.; Hartig-Weiß, A.; Tovini, M. F.; El-Sayed, H. A.;
Schramm, C.; Schröter, J.; Gebauer, C.; Gasteiger, H. A. (2020).
"Current challenges in catalyst development for PEM water electrolyzers."
*Chemie Ingenieur Technik* **92**(1–2), 31–39.
DOI: [10.1002/cite.201900101](https://doi.org/10.1002/cite.201900101).
Open Access (CC-BY).

**Figure digitized:** Fig. 1, red solid line labeled
`2 mg/cm² (measured)` — polarization curve at 80 °C.

**Cell conditions (from paper text):**
- Temperature: 80 °C
- Pressure: 1 bar (atmospheric)
- Membrane: Nafion 212 (~50 µm)
- Anode catalyst: Umicore Elyst Ir75 0480 (75 wt.% IrO₂ on TiO₂), 2 mg Ir/cm²
- Cathode catalyst: Pt/C, 0.35 mg Pt/cm²
- Active area: 5 cm² single-cell
- Flow: water-flooded anode, dry cathode (typical low-pressure MEA test)

**Columns:**
- `j_A_cm2` — current density, A/cm² (figure x-axis is log-scale, 0.01–10)
- `E_V`    — cell voltage, V (figure y-axis linear, 1.2–2.0)

**Digitization:** By visual inspection of a user-taken screenshot of Fig. 1,
not WebPlotDigitizer. Accuracy is dominated by:
- log-x reading resolution → ±5 % on current density
- pixel-to-voltage resolution → ±15–20 mV on E_V

This is deliberately coarser than WPD would give (~±5 mV) but sufficient for
an RMSE-based validation against a zero-fit physics model where the target
tolerance is ±40 mV (see `tests/test_validation_bernt2020.py`).

**Sanity-check anchors on the curve (as read from the screenshot):**
- E ≈ 1.48 V @ j = 0.1 A/cm²
- E ≈ 1.65 V @ j = 1.0 A/cm²
- E ≈ 1.79 V @ j = 4.0 A/cm²
