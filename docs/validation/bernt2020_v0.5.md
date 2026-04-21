# Bernt 2020 Validation — v0.5 Baseline

**Paper:** Bernt, M.; Hartig-Weiß, A.; Tovini, M. F.; El-Sayed, H. A.; Schramm, C.;
Schröter, J.; Gebauer, C.; Gasteiger, H. A. (2020). "Current challenges in catalyst
development for PEM water electrolyzers." *Chemie Ingenieur Technik* **92**(1-2), 31-39.
DOI: [10.1002/cite.201900101](https://doi.org/10.1002/cite.201900101). Open Access (CC-BY).

**Dataset:** [`tests/data/bernt_2020_fig1.csv`](../../tests/data/bernt_2020_fig1.csv) — 15
points digitized from Fig. 1 (red solid line, "2 mg/cm² measured") by visual
inspection of a screenshot. Accuracy ~±20 mV on E, ±5 % on j (log-x readout).

**Test file:** [`tests/test_validation_bernt2020.py`](../../tests/test_validation_bernt2020.py).

## Bernt operating conditions

| Parameter | Value |
|---|---|
| Temperature | 80 °C |
| Pressure | 1 bar (atmospheric) |
| Membrane | Nafion 212 (~50 µm) |
| Anode catalyst | Umicore Elyst Ir75 0480 (75 wt% IrO₂ on TiO₂), 2 mg Ir/cm² |
| Cathode catalyst | Pt/C, 0.35 mg Pt/cm² |
| Active area | 5 cm² single cell |

## Results with v0.5 defaults

| Test | Result | RMSE |
|---|---|---|
| Dataset load & sanity | PASS | — |
| Low-j shape (j ≤ 0.1 A/cm²) | PASS | ~35 mV |
| Full-range RMSE vs 40 mV target | **XFAIL (strict)** | ~510 mV |

Residual growth is monotonic with j:

```
     j [A/cm²]    E_meas [V]    E_pred [V]    residual
        0.01         1.380         1.327       -53 mV
        0.05         1.450         1.442        -8 mV
        0.10         1.480         1.505       +25 mV
        0.50         1.580         1.726      +146 mV
        1.00         1.650         1.874      +224 mV
        4.00         1.790         2.436      +646 mV
       10.00         1.900         3.333     +1433 mV
```

## Context from Zimmer 2026 — why single-paper RMSE is fraught

Zimmer et al. (2026) *J. Electrochem. Soc.* 173, 024503 performed a
data-mining study on 127 PEMWE publications and report that

> "cell voltages reported at the same current density can vary by as much as
> 1.5 V, with standard deviations often exceeding 500 mV"

A 510 mV RMSE between a generic zero-fit model and one specific paper is
therefore **within the literature's own variance**. This doesn't excuse the
model — it just says that calibration must target an *average* or an
*envelope*, not a single paper. See
[`docs/validation/zimmer2026_v0.5.md`](zimmer2026_v0.5.md) for the
envelope-based statistical validation that passes at v0.5.

## Why the RMSE is 510 mV — diagnosis

Two dominant causes, both structural in the defaults rather than bugs in the physics:

1. **R_total overshoots.** The default area-specific resistance is 0.131 Ω·cm²
   (membrane 0.05 + GDL_a 0.02 + GDL_c 0.01 + contact 0.05 + bpp 0.001). Bernt's
   high-j slope implies ~0.05 Ω·cm². The defaults track Carmo et al. (2013) Table 4
   generic commercial values; Bernt uses research-grade Ti felt, optimized cell
   compression, and a thinner effective ionomer path.

2. **j₀,anode is too low for a premium catalyst.** The default j₀ = 1 × 10⁻³ A/cm²
   matches Carmo's "typical commercial IrO₂". Umicore Elyst Ir75 is a
   high-surface-area IrO₂/TiO₂ formulation with an expected j₀ 5–10× higher.

## Why we `xfail` instead of calibrating

Calibrating defaults to match one paper would:

- Break the **zero-fit** property the rest of the test suite relies on
  (`test_tafel_slope_matches_analytical`, `test_monotonicity`, etc. currently assume
  documented-only inputs).
- Couple the generic model to Bernt's specific hardware.
- Make the `bernt_2020_fig1.csv` test circular — fitting to a curve and validating
  against the same curve is not validation.

The cleaner path (v0.6 scope):

- **Catalyst-preset system.** Add a `catalyst` enum to `Electrochemistry` or a
  new preset table in `src/components.py`:
  - `IrO2_generic` (current defaults, Carmo 2013) — stays as default.
  - `IrO2_TiO2_Umicore_Elyst_Ir75` — Bernt-matched, with j₀ and α drawn from
    Bernt's **independent** Tafel analysis (not from fitting Fig. 1 directly).
- **Contact-resistance preset** similarly: `generic_commercial` vs `research_grade`.

The xfail test is `strict=True`, so if v0.6 calibration lands and the full-range
RMSE drops under 40 mV, pytest will raise XPASS and force us to re-baseline the
target. That is intentional — it prevents silent regression on either side.

## Reproduction

```bash
python -m pytest tests/test_validation_bernt2020.py -v
```

Expected output:

```
test_dataset_loads_and_is_sane                            PASSED
test_low_j_shape_within_50mv_rmse                         PASSED
test_full_range_rmse_under_40mv_calibration_target        XFAIL
```
