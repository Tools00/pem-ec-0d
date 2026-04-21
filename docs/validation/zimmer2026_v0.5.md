# Zimmer 2026 Statistical Validation — v0.5

**Paper:** Zimmer, S.; Vollmert, F.; Wiesner, N.; Steiger, J.; Engelhard, T.;
Wessling, M.; Keller, R. (2026). "Data Mining for Enhanced PEM Electrolysis."
*J. Electrochem. Soc.* **173**, 024503. DOI:
[10.1149/1945-7111/ae335e](https://doi.org/10.1149/1945-7111/ae335e). Open
Access (CC-BY 4.0).

**Dataset:** [`tests/data/zimmer_2026_fig1c.csv`](../../tests/data/zimmer_2026_fig1c.csv) —
5 benchmark points from Fig. 1c, filtered to Nafion N115 + 80 °C, aggregating
>127 peer-reviewed publications (2006-2024). Digitized by visual inspection:
mean ±15 mV, band edges ±20 mV.

**Test file:**
[`tests/test_validation_zimmer2026.py`](../../tests/test_validation_zimmer2026.py).

## Why this validation is stronger than single-paper

Zimmer et al. explicitly document:

> "cell voltages reported at the same current density can vary by as much as
> **1.5 V, with standard deviations often exceeding 500 mV**"

This is a direct, independent confirmation of the reasoning behind the Bernt
2020 `xfail` (`docs/validation/bernt2020_v0.5.md`): a single-paper RMSE cannot
discriminate "model broken" from "we picked a non-average paper." An
envelope-based validation against the aggregated literature can.

Zimmer's Fig. 1c shows the *filtered* dataset (only N115 + 80 °C) — still
spanning ~0.3-0.8 V min/max, but much tighter than the full corpus.

## Data (as digitized)

| j [A/cm²] | E_mean [V] | σ [V] | [E_min, E_max] [V] |
|-----------|------------|-------|---------------------|
| 0.2       | 1.58       | 0.05  | [1.45, 1.75]        |
| 0.5       | 1.68       | 0.07  | [1.50, 1.90]        |
| 1.0       | 1.78       | 0.08  | [1.55, 2.10]        |
| 1.5       | 1.85       | 0.10  | [1.60, 2.25]        |
| 2.0       | 1.90       | 0.12  | [1.65, 2.40]        |

## Model predictions (N115 filter, zero-fit defaults)

```
 j [A/cm²]  E_pred [V]  vs mean     in ±σ?   in [min, max]?
 0.2        1.600       +20 mV      YES      YES
 0.5        1.765       +85 mV      NO       YES
 1.0        1.951      +171 mV      NO       YES
 1.5        2.104      +254 mV      NO       YES
 2.0        2.243      +343 mV      NO       YES

 Bias (mean residual) = +175 mV
 RMSE (vs mean)       = 210 mV
```

## Interpretation

- **Passing:** Model lands inside the full literature envelope at every
  benchmark j. This is the meaningful v0.5 validation claim. The model is
  *literature-consistent*, not an outlier. `test_model_within_literature_envelope`.
- **Failing (xfail):** Model sits at the upper (hotter) edge of the envelope,
  outside mean ± 1σ at 4 of 5 j. Bias is +175 mV, RMSE 210 mV.
  `test_model_within_one_sigma_band` is marked `xfail(strict=True)`.

The +175 mV mean bias is consistent with the 510 mV Bernt 2020 overshoot at
higher j. Both point to the same root cause: Carmo 2013 Table 4 "typical
commercial" defaults for j₀ and the 0.05 + 0.02 + 0.05 Ω·cm² interface-resistance
stack run hotter than research-grade setups.

## Why we `xfail` instead of calibrating

Same rationale as Bernt. Calibrating defaults to one paper or one figure would:

- Break the zero-fit property the rest of the suite relies on.
- Make the corresponding test circular.

Zimmer-specific caveat: even if we fit to Zimmer's *mean*, we'd bias the model
against one specific membrane (N115). Our default membrane in
`src.electrochemistry` has no "type" field — thickness and conductivity are
free. Calibration therefore needs to live in a preset system, not in the
defaults.

## v0.6 path

1. **Catalyst-preset table** in `src/components.py`:
   - `IrO2_generic` — current defaults, Carmo 2013 (Ir density 11.66 g/cm³,
     j₀ = 1 × 10⁻³ A/cm² at 80 °C).
   - `IrO2_TiO2_Umicore_Elyst_Ir75` — Bernt 2020 (kinetic params from his
     independent Tafel analysis, not from Fig. 1 fit).
   - Optional: derived fits per Zimmer's support-material analysis
     (25/50/80 wt% Ir/Support, Fig. 3).
2. **Membrane-preset table** already exists in `src/components.py`
   (`MEMBRANES`) — add `Nafion 115` if absent and verify the conductivity
   model tracks Zimmer's filtered N115 corpus.
3. **Contact-resistance preset**: `generic_commercial` (current) vs
   `research_grade`.
4. After the presets land, re-run both Bernt and Zimmer validations. Target:
   Bernt RMSE < 60 mV, Zimmer inside ±1σ at all 5 j. If both pass, flip the
   strict-xfail tests to normal asserts and bump validation docs to v0.6.

## Reproduction

```bash
python -m pytest tests/test_validation_zimmer2026.py -v
```

Expected output:

```
test_dataset_loads_and_is_sane            PASSED
test_model_within_literature_envelope     PASSED
test_model_within_one_sigma_band          XFAIL
```
